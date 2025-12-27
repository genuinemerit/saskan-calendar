import pandas as pd
from langdetect import detect
from openai import OpenAI
import math
import os

# === CONFIGURATION ===
TEST_MODE = False  # Set True to limit to 15 rows
CHECK_MODE = False  # Set True for dry run (no API calls)
mode = "TEST CASES ONLY" if TEST_MODE else "FULL DATA RUN"
mode += " - DRY RUN" if CHECK_MODE else " - LIVE RUN"
print(f"Run Mode: {mode}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === FILE PATHS ===
input_file = "../data/inventario.ods"
output_file = "../data/inventory_translated.xlsx"
progress_file = "../data/translation_progress.xlsx"

batch_size = 15  # cells per API call

# --- Load spreadsheet ---
ext = input_file.split(".")[-1].lower()
if ext == "csv":
    df = pd.read_csv(input_file, dtype=str)
elif ext == "ods":
    df = pd.read_excel(
        input_file, engine="odf", sheet_name="Inventario consolidado", dtype=str
    )
else:
    df = pd.read_excel(input_file, dtype=str)

if TEST_MODE:
    df = df.head(15)

# --- Build combined DataFrame ---
if os.path.exists(progress_file):
    print(f"Resuming from saved progress: {progress_file}")
    df_combined = pd.read_excel(progress_file, dtype=str)
else:
    df_en = df.copy()
    df_es = df.copy()
    suffixes = ["_orig", "_en", "_es"]
    dfs = [df, df_en, df_es]
    df_combined = pd.concat([d.add_suffix(s) for d, s in zip(dfs, suffixes)], axis=1)
    df_combined.to_excel(progress_file, index=False)


# === TRANSLATION HELPERS ===
def batch_translate_texts_debug(texts, target_lang="en"):
    """Mock translator for dry-run."""
    return [f"[{target_lang}] {t}" if t else t for t in texts]


def batch_translate_texts(texts, target_lang="en"):
    """Translate a batch of texts using OpenAI API."""
    items_to_translate = []
    index_map = []

    for i, t in enumerate(texts):
        if not t or str(t).strip() == "":
            continue
        try:
            lang = detect(str(t))
        except Exception:
            lang = "unknown"

        # Force-translate single words (langdetect fails)
        if len(str(t).split()) == 1:
            items_to_translate.append(str(t))
            index_map.append(i)
        elif target_lang == "en" and lang == "es":
            items_to_translate.append(str(t))
            index_map.append(i)
        elif target_lang == "es" and lang == "en":
            items_to_translate.append(str(t))
            index_map.append(i)

    if not items_to_translate:
        return texts

    # Build prompt
    source_lang = "Spanish" if target_lang == "en" else "English"
    numbered_list = "\n".join(
        [f"{i+1}. {txt}" for i, txt in enumerate(items_to_translate)]
    )
    prompt = (
        f"Translate the following {source_lang} texts into {target_lang.capitalize()}. "
        "Keep numbers/codes unchanged. Return a numbered list of translations " +
        "in the same order:\n\n"
        f"{numbered_list}"
    )

    # Send to API (or dry-run)
    if CHECK_MODE:
        return batch_translate_texts_debug(texts, target_lang)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )

    # Process output and update texts
    translated_lines = [
        line
        for line in response.choices[0].message.content.strip().split("\n")
        if line.strip()
    ]

    for idx, line in enumerate(translated_lines):
        if idx >= len(index_map):
            break
        translation = line.split(". ", 1)[-1] if ". " in line else line
        texts[index_map[idx]] = translation

    return texts


def is_translated_or_empty(text, target_lang):
    """
    Return True if the cell is empty or already in target language.
    Safe for NaNs, floats, and empty strings.
    """
    if not str(text).strip():
        return True
    try:
        return detect(str(text)) == target_lang
    except Exception:
        return False


def translate_column(col_name, target_lang):
    """Translate column and save progress incrementally."""
    col_key = f"{col_name}_{target_lang}"
    texts = df_combined[col_key].tolist()
    total_batches = math.ceil(len(texts) / batch_size)

    for b in range(total_batches):
        start = b * batch_size
        end = min(start + batch_size, len(texts))

        # Skip batch if all cells empty or already in target language
        if all(is_translated_or_empty(text, target_lang) for text in texts[start:end]):
            continue

        texts[start:end] = batch_translate_texts(texts[start:end], target_lang)
        df_combined[col_key] = pd.Series(texts)
        df_combined.to_excel(progress_file, index=False)


# === MAIN TRANSLATION LOOP ===
for col in df.columns:
    # Skip columns that are not text
    if any(k in col.lower() for k in ["autor", "caja", "usd", "euro", "año comprado"]):
        continue

    translate_column(col, "en")
    translate_column(col, "es")

# --- Save final output ---
df_combined.to_excel(output_file, index=False)
print(f"✅ Final translated spreadsheet saved as {output_file}")

if os.path.exists(progress_file):
    os.remove(progress_file)
