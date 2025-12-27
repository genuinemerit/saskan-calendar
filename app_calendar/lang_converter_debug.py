import pandas as pd
from langdetect import detect
from openai import OpenAI
from tqdm import tqdm
from pprint import pprint as pp  # noqa: F401
import math
import os

# Prepare environment
# pd.set_option("display.max_columns", None)  # show all columns
TEST_MODE = True  # Set to False for full data run
CHECK_MODE = False  # Set to True for dry run (no API calls, just testing logic)
mode = "TEST CASES ONLY" if TEST_MODE else "FULL DATA RUN"
if CHECK_MODE:
    mode += " - DRY RUN"
else:  # Normal operation
    mode += "- LIVE RUN"
print(f"Run Mode: {mode}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# File paths
input_file = "../data/inventario.ods"
output_file = "../data/inventory_translated.xlsx"
progress_file = "../data/translation_progress.xlsx"

# Constants
batch_size = 15  # cells per API call

# --- Load spreadsheet ---
file_extension = input_file.split(".")[-1].lower()

if file_extension == "csv":
    df = pd.read_csv(input_file, dtype=str)
elif file_extension == "ods":
    df = pd.read_excel(
        input_file,
        engine="odf",
        sheet_name="Inventario consolidado",  # name of your sheet
        dtype=str,
    )
else:
    df = pd.read_excel(input_file, dtype=str)

if TEST_MODE:
    # Limit to first 15 rows for testing purposes
    df = df.head(15)  # only keep first 15 rows

# Constants
progress_file = "../data/translation_progress.xlsx"

# --- Check if we have saved progress ---
if os.path.exists(progress_file):
    print(f"Resuming from saved progress: {progress_file}")
    df_combined = pd.read_excel(progress_file, dtype=str)
else:
    # Prepare blank dataframes for English and Spanish translations
    df_en = df.copy()
    df_es = df.copy()

    # Initialize combined dataframe with original columns
    suffixes = ["_orig", "_en", "_es"]
    dfs = [df, df_en, df_es]
    df_combined = pd.concat([d.add_suffix(s) for d, s in zip(dfs, suffixes)], axis=1)

    # Save initial progress
    df_combined.to_excel(progress_file, index=False)


def batch_translate_texts_debug(texts, target_lang="en"):
    return [f"[{target_lang}] {t}" if t else t for t in texts]


def batch_translate_texts(texts, target_lang="en"):
    """
    Translate a batch of texts using OpenAI API.
    Handles short words, language detection, trimming, and logs actions.
    """
    print(f"\n🔄 Translating {len(texts)} cells → target: {target_lang}")

    items_to_translate = []
    index_map = []

    for i, t in enumerate(texts):
        if not t or str(t).strip() == "":
            continue  # skip empty cells

        try:
            lang = detect(str(t))
        except Exception:
            lang = "unknown"

        # Force translate single words (langdetect often fails on these)
        if len(str(t).split()) == 1:
            items_to_translate.append(str(t))
            index_map.append(i)
            print(f"  • [{i}] '{t}' (forced single-word translation)")
        elif target_lang == "en" and lang == "es":
            items_to_translate.append(str(t))
            index_map.append(i)
            print(f"  • [{i}] '{t}' (Spanish → English)")
        elif target_lang == "es" and lang == "en":
            items_to_translate.append(str(t))
            index_map.append(i)
            print(f"  • [{i}] '{t}' (English → Spanish)")

    if not items_to_translate:
        print("  ✅ No translations needed in this batch")
        return texts

    # Build the prompt
    source_lang = "Spanish" if target_lang == "en" else "English"
    numbered_list = "\n".join(
        [f"{i+1}. {txt}" for i, txt in enumerate(items_to_translate)]
    )
    prompt = (
        f"Translate the following {source_lang} texts into {target_lang.capitalize()}. "
        "Keep numbers/codes unchanged. Return a numbered list of translations "
        "in the same order:\n\n"
        f"{numbered_list}"
    )

    # Send to API
    print(f"  🔗 Sending {len(items_to_translate)} items for translation...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )

    # Process output, strip blanks
    translated_lines = [
        line
        for line in response.choices[0].message.content.strip().split("\n")
        if line.strip()
    ]

    if len(translated_lines) != len(index_map):
        print(
            f"⚠️ Warning: expected {len(index_map)} translations, got {len(translated_lines)}"
        )
        print("   → Raw output:")
        print("\n".join(translated_lines))

    for idx, line in enumerate(translated_lines):
        if idx >= len(index_map):
            print(f"⚠️ Extra line ignored: {line}")
            break

        # Remove any "1. " numbering if present
        translation = line.split(". ", 1)[-1] if ". " in line else line
        texts[index_map[idx]] = translation
        print(f"  ✅ [{index_map[idx]}] '{items_to_translate[idx]}' → '{translation}'")

    return texts


def translate_column(col_name, target_lang):
    """Translate column with progress bar and resume support."""
    col_key = f"{col_name}_{target_lang}"
    texts = df_combined[col_key].tolist()
    total_batches = math.ceil(len(texts) / batch_size)

    # Determine translation function based on mode
    translation_function = (
        batch_translate_texts_debug if CHECK_MODE else batch_translate_texts
    )

    with tqdm(total=total_batches, desc=f"Translating {col_key}", disable=True) as pbar:
        # with tqdm(total=total_batches, desc=f"Translating {col_key}") as pbar:
        for b in range(total_batches):
            start = b * batch_size
            end = min(start + batch_size, len(texts))

            # Skip batch if already translated
            if all(
                (isinstance(text, str) and detect(text) == target_lang)
                or not str(text).strip()
                for text in texts[start:end]
            ):
                pbar.update(1)
                continue

            # Translate and update texts
            texts[start:end] = translation_function(texts[start:end], target_lang)

            # Update DataFrame and save progress
            df_combined[col_key] = pd.Series(texts)
            df_combined.to_excel(progress_file, index=False)

            pbar.update(1)


# --- Translate ---
for col in df.columns:
    if any(k in col.lower() for k in ["autor", "caja", "usd", "euro", "año comprado"]):
        # skip these columns since they are not text
        continue

    translate_column(col, "en")
    translate_column(col, "es")

# --- Save final output ---
df_combined.to_excel(output_file, index=False)
print(f"✅ Final translated spreadsheet saved as {output_file}")
os.remove(progress_file)  # Clean up progress file
