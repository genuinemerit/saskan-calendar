#!python
"""
:module:    mb_dictionary.py
:author:    PQ (pq_rfw @ pm.me)

Define sets of immutable components, pre-loaded static values.
"""

import music21 as m21
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401
from shared.utils.file_io import FileMethods
import mb_tools as mtools  # noqa F401

FM = FileMethods()


@dataclass(frozen=True)
class NoteSet:
    """
    Defines standard note durations, rests, dotted values, and tuplets.

    Durations are based on music21's quarterLength system:
    - quarter note = 1.0
    - half note = 2.0
    - eighth note = 0.5
    - etc.

    Tuplets are defined as:
        Tuplet(actual, normal)
    Where:
    - `actual` = number of notes to play
    - `normal` = number of notes you'd normally expect in the same space

    Examples:
    - Tuplet(3, 2): 3 notes in the time of 2 — a standard triplet
    - Tuplet(5, 2): 5 notes in the time of 2 — a quintuplet

    Potential Enhancements:
    - Add tuplet metadata (ratios, labels)
    - Generate tied note groups for phrase shaping
    - Support dotted tuplets for advanced rhythm
    - Add helper accessors and filters (by length, category, etc.)
    - Support display of tuplet ratios in display_notes()

    """

    note: dict = field(init=False, default_factory=lambda: NoteSet.build_notes())

    @staticmethod
    def build_notes():
        note = {
            ntype: {}
            for ntype in (
                "plain",
                "rest",
                "dotted",
                "triplet",
                "quintuplet",
                "septuplet",
            )
        }

        base_durations = {
            "breve": 8.0,
            "whole": 4.0,
            "half": 2.0,
            "quarter": 1.0,
            "eighth": 0.5,
            "16th": 0.25,
            "32nd": 0.125,
            "64th": 0.0625,
        }

        for name, dur_val in base_durations.items():
            dur_plain = m21.duration.Duration(dur_val)
            note["plain"][name] = dur_plain
            note["rest"][name] = m21.note.Rest(quarterLength=dur_val)
            note["dotted"][name] = m21.duration.Duration(dur_val * 1.5)

            # Create tuplets as separate Duration objects
            for kind, ratio in {
                "triplet": (3, 2),
                "quintuplet": (5, 2),
                "septuplet": (7, 2),
            }.items():
                d = m21.duration.Duration(dur_val)
                d.appendTuplet(m21.duration.Tuplet(*ratio))
                note[kind][name] = d

        return note

    def display_notes(self):
        """
        Display each category of note durations in separate tables.
        """
        output = ""
        for category, notes in self.note.items():
            headers = ["Note Name", "Duration (quarterLength)"]
            rows = []
            for name, dur in notes.items():
                ql = dur.quarterLength if hasattr(dur, "quarterLength") else "?"
                rows.append([name, ql])
            output += f"\n{category.upper()}:\n"
            output += tabulate(rows, headers=headers, tablefmt="grid")
            output += "\n"
        return output


@dataclass(frozen=True)
class ScaleSet:
    """
    Define pitches for all types of modern, traditional western scales as well
    as for non-western traditions and other alternatives.
    Scale names are based on music21 version 9.7.1.

    Proposed enhancments:
    - Read up on the Abstract etc. scales. They are meant to be inherited, built on:
    ['AbstractCyclicalScale', 'AbstractDiatonicScale',
     'AbstractHarmonicMinorScale', 'AbstractMelodicMinorScale',
     'AbstractOctatonicScale', 'AbstractOctaveRepeatingScale', 'AbstractRagAsawari',
     'AbstractRagMarwa', 'AbstractScale', 'AbstractWeightedHexatonicBlues',
     'ConcreteScale', ]
    """

    scale: dict = field(init=False, default_factory=lambda: ScaleSet.build_scales())

    @staticmethod
    def build_scales():
        scale = {}
        keys = [
            "C",
            "G",
            "D",
            "A",
            "E",
            "B",
            "F#",
            "C#",
            "G#",
            "F",
            "B-",
            "E-",
            "A-",
            "D-",
            "G-",
            "C-",
            "F-",
        ]
        for k in keys:
            scale[k] = {}
        m21.scales = [
            "ChromaticScale",
            "CyclicalScale",
            "DiatonicScale",
            "DorianScale",
            "HarmonicMinorScale",
            "HypoaeolianScale",
            "HypodorianScale",
            "HypolocrianScale",
            "HypolydianScale",
            "HypomixolydianScale",
            "HypophrygianScale",
            "LocrianScale",
            "LydianScale",
            "MajorScale",
            "MelodicMinorScale",
            "MinorScale",
            "MixolydianScale",
            "OctatonicScale",
            "OctaveRepeatingScale",
            "PhrygianScale",
            "RagAsawari",
            "RagMarwa",
            "ScalaScale",
            "SieveScale",
            "WeightedHexatonicBlues",
            "WholeToneScale",
        ]
        for k in keys:
            for s in m21.scales:
                try:
                    ScaleClass = getattr(m21.scale, s)
                    scale_name = s.replace("Scale", "").replace("Blues", "").lower()
                    scale_instance = ScaleClass(k)
                    scale[k][scale_name] = scale_instance
                except Exception as e:
                    print(f"Failed to create {s} for key {k}: {e}")
        return scale

    def display_scale(self, root=None, mode=None):
        """
        Display the pitches in all scales, or a specified key/mode.
        """
        output = ""
        keys = [root] if root else self.scale.keys()

        for k in keys:
            modes = [mode] if mode else self.scale[k].keys()
            for m in modes:
                scl = self.scale[k][m]
                pitches = [p.nameWithOctave for p in scl.getPitches(k + "4", k + "5")]
                output += f"{k} {m}: {' '.join(pitches)}\n"
        return output

    def get_modes(self, mode_name):
        return {
            k: self.scale[k][mode_name]
            for k in self.scale
            if mode_name in list(self.scale[k].keys())
        }

    def get_key_signatures(self, key=None, mode=None) -> dict:
        """
        Return a dict of KeySignature objects for each (key, mode) pair.
        Count sharps and flats separately. Ignore double-flats, double-sharps.
        N.B. - Will still need to pay attention to accidentals when scoring;
         this just identifies the proper key signature for a given scale.
         Remember that it may or may not actually cover all the accidentals.
        """
        key_param = key
        mode_param = mode
        ks_map = {}
        for k, modes in self.scale.items():
            if key_param is not None and k != key_param:
                continue
            ks_map[k] = {}
            for m, scale in modes.items():
                if mode_param is not None and m != mode_param:
                    continue
                pitches = scale.getPitches()
                sharps = sum(1 for p in pitches if "#" in p.name and "##" not in p.name)
                flats = sum(1 for p in pitches if "-" in p.name and "--" not in p.name)
                if sharps > flats:
                    acc_count = sharps
                elif flats > sharps:
                    acc_count = -flats
                else:
                    # arbitrarily favor sharps if tied
                    acc_count = sharps
                ks_map[k][m] = m21.key.KeySignature(acc_count)
        return ks_map


@dataclass(frozen=True)
class TimeSignatureSet:
    """
    A curated set of common and expressive time signatures,
    categorized by rhythmic feel and musical context.
    """

    timesig: Dict[str, Dict] = field(
        init=False, default_factory=lambda: TimeSignatureSet.build_timesigs()
    )

    @staticmethod
    def build_timesigs() -> Dict[str, Dict]:
        tsigs = {}

        signature_data = [
            # Simple meters
            ("2/4", "simple", "marchy, quick", "classical, marches"),
            ("3/4", "simple", "waltz feel", "romantic, dance"),
            ("4/4", "simple", "neutral, common", "everything"),
            ("2/2", "simple", "cut time", "fast orchestral"),
            # Compound meters
            ("6/8", "compound", "galloping, flowing", "lyrical, baroque"),
            ("9/8", "compound", "broad swing", "folk, hymn, Brahms"),
            ("12/8", "compound", "rolling, bluesy", "blues, rock ballads"),
            # Asymmetrical meters
            ("5/4", "asymmetrical", "uneven, driving", "jazz, cinematic"),
            ("7/8", "asymmetrical", "urgent, shifting", "Balkan, prog rock"),
            ("5/8", "asymmetrical", "snappy, syncopated", "modern jazz"),
            ("7/4", "asymmetrical", "long, offset", "epic, Holst"),
            # Rare or advanced
            ("3/8", "rare", "short, pickup energy", "dance fragments, scherzo"),
            ("11/8", "rare", "complex, shifting pulse", "Eastern European folk"),
            ("2/8", "rare", "tight, staccato", "fragmented themes"),
        ]

        for sig, category, feel, usage in signature_data:
            tsigs[sig] = {
                "signature": m21.meter.TimeSignature(sig),
                "category": category,
                "feel": feel,
                "usage": usage,
            }

        return tsigs

    def list_all_time_sigs(self) -> List[str]:
        """
        Return all time signature strings.
        """
        return list(self.timesig.keys())

    def display_all_time_sigs(self) -> str:
        """
        Return a formatted string listing all time signatures with metadata.
        """
        lines = []
        for sig, data in self.timesig.items():
            lines.append(
                f"{sig:>5} | {data['category']:<12} | {data['feel']:<18} | {data['usage']}"
            )
        return "\n".join(lines)

    def get_time_sig_by_category(self, category: str) -> Dict[str, Dict]:
        """
        Return all time signatures matching a rhythmic category.
        """
        return {k: v for k, v in self.timesig.items() if v["category"] == category}


@dataclass(frozen=True)
class EmbellishmentSet:
    """
    A curated set of common and expressive embellishments,
    categorized by their musical function and context.

    music21's terminology splits **Embellishments** into more technical subcategories:

    | MuseBox Term       | music21 / MusicXML Equivalent      |
    | ------------------ | ---------------------------------- |
    | Ornament           | `ornamentations`, e.g., `Trill`, `Turn`, `Mordent`, `Appoggiatura` |
    | Articulation       | `articulations`, e.g., `Staccato`, `Tenuto`, `Accent`, `Marcato` |
    | Expression         | `expressions`, e.g., `DynamicWedge`, `Crescendo`, `TextExpression` |
    | Style/Technique    | `technical`, `style`, `notations`, e.g., `Harmonic`, `Fermata`,
                             `ArpeggioMark` |
    | Performance Effect | MIDI-based, e.g., bends, vibrato, slide (not native in music21)  |
    ## ✅ Approach for MuseBox (Now and Later)

    ### 1. **Keep `Embellishment` Layer Unified**
    - MuseBox should keep using `Embellishment` as a general term—it works well at
      the composition grammar level. Think of it as the "intention" layer.

    ### 2. **Don’t Lock Into music21’s API Yet**
    - The music21 documentation (e.g., Chapter 33) is still thin or placeholder-ish. So:
      - Only link to music21 **if the class is stable** (e.g., `Staccato()`, `Trill()` are stable)
      - For MIDI-style or continuous effects (vibrato, bend), we may need to stub or
        model them in MuseBox independently for now

    ### 3. **Later **
    - Others could be added later, such as `Harmonic()`, `Fermata()`, ArpeggioMark()`, etc.
    - For now, keep it simple. Focus on core embellishments most relevant to MuseBox's goals.
    """

    embells: Dict[str, Dict] = field(
        init=False, default_factory=lambda: EmbellishmentSet.build_embellishments()
    )

    @staticmethod
    def build_embellishments():
        embells = {}

        embells["grace_note"] = {
            "m21_type": "ornamentation",
            "description": "Quick lead-in note before a main note.",
            "music21_symbol": "GraceNote",
        }
        embells["trill"] = {
            "m21_type": "ornamentation",
            "description": "Rapid alternation between two adjacent notes.",
            "music21_symbol": "Trill",
        }
        embells["turn"] = {
            "m21_type": "ornamentation",
            "description": "Four-note ornament surrounding the main note.",
            "music21_symbol": "Turn",
        }
        embells["mordent"] = {
            "m21_type": "ornamentation",
            "description": "Rapid alternation with the note below.",
            "music21_symbol": "Mordent",
        }
        embells["acciaccatura"] = {
            "m21_type": "ornamentation",
            "description": "Crushed note played before the main note.",
            "music21_symbol": "Acciaccatura",
        }
        embells["appoggiatura"] = {
            "m21_type": "ornamentation",
            "description": "Leaning note that takes time from the main note.",
            "music21_symbol": "Appoggiatura",
        }
        embells["slide"] = {
            "m21_type": "expression",
            "description": "Glide between notes, especially on string or synth.",
            "music21_symbol": None,  # Not directly in music21
        }
        embells["bend"] = {
            "m21_type": "expression",
            "description": "Pitch bend, often for guitar or synth.",
            "music21_symbol": None,  # Not directly in music21
        }
        embells["vibrato"] = {
            "m21_type": "expression",
            "description": "Oscillation in pitch or volume.",
            "music21_symbol": None,  # Not directly in music21
        }
        embells["staccato"] = {
            "m21_type": "articulation",
            "description": "Short and detached.",
            "music21_symbol": "Staccato",
        }
        embells["tenuto"] = {
            "m21_type": "articulation",
            "description": "Hold for full value.",
            "music21_symbol": "Tenuto",
        }
        embells["accent"] = {
            "m21_type": "articulation",
            "description": "Play with emphasis.",
            "music21_symbol": "Accent",
        }
        return embells

    def get_by_name(self, name: str) -> Optional[Dict]:
        """
        Get an embellishment by its name.
        :param name: Name of the embellishment to retrieve.
        :return: Dictionary with embellishment details or None if not found.
        """
        return self.embells.get(name, None)

    def get_by_type(self, m21_type: str) -> Optional[List[Dict]]:
        """
        Get all embellishments of a specific music21 type.
        :param m21_type: Type of embellishment (e.g., 'ornamentation', 'articulation').
        :return: List of dictionaries with embellishment details or an empty list if not found.
        """
        return [
            {name: data}
            for name, data in self.embells.items()
            if data.get("m21_type").lower() == m21_type.lower()
        ]

    def get_by_symbol(self, symbol: str) -> Optional[List]:
        """
        Get an embellishment by its music21 symbol.
        :param symbol: Music21 symbol of the embellishment to retrieve.
        :return: List of dictionaries with embellishment details or an empty list if not found.
        """
        syms = []
        for emb_name, emb_data in self.embells.items():
            if "music21_symbol" not in emb_data or emb_data["music21_symbol"] is None:
                continue
            if symbol.lower() in emb_data.get("music21_symbol", "").lower():
                syms.append({emb_name: emb_data})
        return syms


@dataclass(frozen=True)
class DynamicSet:
    """
    Represents a basic dynamic marking.
    Build out to include full set of dynamics, including
    crescendos, decrescendos, and other expressive markings.
    This is a simplified version, but can be extended later.
    The values can be populated either in this class or
    in a separate library that maps to music21's dynamic classes.
    """

    dynams: Dict[str, Dict] = field(
        init=False, default_factory=lambda: DynamicSet.build_dynamics()
    )

    @staticmethod
    def build_dynamics():
        dynams = {}
        # Populate the dynamics dictionary with common dynamic markings
        dynams["ppp"] = {
            "description": "pianississimo (very very soft)",
            "m21_symbol": "pp",
            "velocity": 16,  # MIDI velocity
        }
        dynams["pp"] = {
            "description": "pianissimo (very soft)",
            "m21_symbol": "pp",
            "velocity": 33,
        }
        dynams["p"] = {"description": "piano (soft)", "m21_symbol": "p", "velocity": 49}
        dynams["mp"] = {
            "description": "mezzo piano (moderately soft)",
            "m21_symbol": "mp",
            "velocity": 65,
        }
        dynams["mf"] = {
            "description": "mezzo forte (moderately loud)",
            "m21_symbol": "mf",
            "velocity": 80,
        }
        dynams["f"] = {"description": "forte (loud)", "m21_symbol": "f", "velocity": 96}
        dynams["ff"] = {
            "description": "fortissimo (very loud)",
            "m21_symbol": "ff",
            "velocity": 112,
        }
        dynams["fff"] = {
            "description": "fortississimo (very very loud)",
            "m21_symbol": "fff",
            "velocity": 127,
        }
        dynams["crescendo"] = {
            "description": "Gradually getting louder",
            "m21_symbol": "crescendo",
        }
        dynams["decrescendo"] = {
            "description": "Gradually getting softer",
            "m21_symbol": "decrescendo",
        }
        return dynams

    def get_by_description(self, description: str) -> Optional[List]:
        """
        Get a dynamic marking by its description.
        :param description: Description of the dynamic marking to retrieve.
        :return: Dictionary with dynamic marking details or None if not found.
        """
        dyns = []
        for dyn_name, dyn_data in self.dynams.items():
            if description.lower() in dyn_data.get("description", "").lower():
                dyns.append({dyn_name: dyn_data})
        return dyns

    def get_by_symbol(self, symbol: str) -> Optional[List]:
        """
        Get a dynamic marking by its music21 symbol.
        :param symbol: Music21 symbol of the dynamic marking to retrieve.
        :return: List of dictionaries with dynamic marking details or an empty list if not found.
        """
        dyns = []
        for dyn_name, dyn_data in self.dynams.items():
            if "m21_symbol" not in dyn_data or dyn_data["m21_symbol"] is None:
                continue
            if symbol.lower() in dyn_data["m21_symbol"].lower():
                dyns.append({dyn_name: dyn_data})
        return dyns


@dataclass(frozen=True)
class ClefSet:
    """
    Represents a musical clef for staff layout.
    Music21 provides all standard and many non-standard clefs, so here we can
    just provide a kind of overview into the music21 Clef sub-classes.
    See: https://www.music21.org/music21docs/moduleReference/moduleClef.html#music21.clef.Clef
    """

    clefs: Dict[str, Dict] = field(
        init=False, default_factory=lambda: ClefSet.build_clefs()
    )

    @staticmethod
    def build_clefs():
        """
        Capture clef info from muusic21's Clef classes.
        Returns a dictionary of clef names and their properties.
        N.B. -
        A diatonic note number is a way to represent a pitch in terms of its
        letter name and scale degree, ignoring accidentals (sharps/flats).
        Generally, using C as the root, it increases in steps of 1 per letter,
        regardless of sharps/flats or octaves:  0 = C, 1 = D, 2 = E, 3 = F,...
        So, for example:
        31 ÷ 7 = 4 with remainder of 3.  31 is in the *5th* diatonic octave, because
          it lies _after_ 4 (or you could think of it as 4 indexing from 0).
          The note of the scale is the 4th degree (because the remainder, 3, indexes
          from 0), so F (or F5, if you prefer to think of it that way).
        """
        clefs = {}

        for name, cls in m21.clef.__dict__.items():
            if not isinstance(cls, type):
                continue
            if not issubclass(cls, m21.clef.Clef):
                continue
            if cls is m21.clef.Clef:
                continue
            inst = cls()  # Create an instance of the clef class
            clefs[cls.__name__] = {
                "name": inst.name,
                # -n or +n indicates transposition, e.g., '8va', '8vb'
                "octaveChange": inst.octaveChange,
                # Line, counting from bottom up, that the clef resides on.
                "line": inst.line,
                # Diatonic note number of the clef's lowest line
                "lowestLine_diatonic": (
                    inst.lowestLine if hasattr(inst, "lowestLine") else None
                ),
                # The sign of the clef, generally, ‘C’, ‘G’, ‘F’, ‘percussion’, ‘none’ or None.
                "lowestLine_pitch": (
                    mtools.pitch_from_diatonic_number(inst.lowestLine)
                    if hasattr(inst, "lowestLine")
                    else None
                ),
                "sign": inst.sign,
            }
        return clefs

    def get_clef_by_name(self, name: str) -> Optional[Dict[str, object]]:
        """
        Return a clef matching a specific name or class name.
        """
        return {
            k: v
            for k, v in self.clefs.items()
            if (
                name.lower().strip() in v["name"].lower()
                or name.lower().strip() in k.lower()
            )
        }

    def list_all_clefs(self) -> List[str]:
        """
        Return a list of all clef names.
        """
        return list(self.clefs.keys())


@dataclass(frozen=True)
class TempoSet:
    """
    Represents a tempo indication.
    Build out to include a standard set of tempo markings,
    such as 'Largo', 'Adagio', 'Andante', 'Allegro', etc.
    Tie them to BPM ranges and provide English descriptions.
    See: https://www.music21.org/music21docs/moduleReference/moduleTempo.html#music21.tempo.TempoIndication  # noqa: E501
    """

    tempos: Dict[str, Dict] = field(
        init=False, default_factory=lambda: TempoSet.build_tempos()
    )

    @staticmethod
    def build_tempos():

        tempos = {}

        # Basic English label map for common tempo terms
        english_names = {
            "larghissimo": "Very, very slow",
            "largamente": "Broad and slow",
            "grave": "Very slow and solemn",
            "molto adagio": "Very slow",
            "largo": "Slow and broad",
            "lento": "Slow",
            "adagio": "Leisurely",
            "slow": "Slow",
            "langsam": "Slow (German)",
            "larghetto": "Rather broadly",
            "adagietto": "Quite slow",
            "andante": "At a walking pace",
            "andantino": "Slightly faster than andante",
            "andante moderato": "Moderate walking pace",
            "maestoso": "Majestic",
            "moderato": "Moderate speed",
            "moderate": "Moderate",
            "allegretto": "Moderately fast",
            "animato": "Animated or lively",
            "allegro moderato": "Moderately quick",
            "allegro": "Fast, quickly and bright",
            "fast": "Fast",
            "schnell": "Fast (German)",
            "allegrissimo": "Very fast",
            "molto allegro": "Very fast",
            "très vite": "Very fast (French)",
            "vivace": "Lively and fast",
            "vivacissimo": "Very lively",
            "presto": "Extremely fast",
            "prestissimo": "As fast as possible",
        }

        for name, duration in m21.tempo.defaultTempoValues.items():
            tempos[name] = {
                "bpm": duration,
                "english_name": english_names.get(name, "N/A"),
            }
        return tempos

    def list_all_tempos(self) -> List[str]:
        """
        Return a list of all tempo names.
        """
        return list(self.tempos.keys())

    def get_tempo_by_name(self, name: str) -> Optional[Dict[str, object]]:
        """
        Return a tempo matching a specific name or class name.
        """
        return {
            k: v
            for k, v in self.tempos.items()
            if (
                name.lower().strip() in v["english_name"].lower()
                or name.lower().strip() in k.lower()
            )
        }

    def get_nearest_tempo_by_bpm(self, bpm: float) -> Optional[Dict[str, object]]:
        """
        Return a tempo that most closely matches the given BPM.
        """
        closest_tempo = None
        min_diff = float("inf")
        for k, v in self.tempos.items():
            diff = abs(v["bpm"] - bpm)
            if diff < min_diff:
                min_diff = diff
                closest_tempo = {k: v}
        return closest_tempo
