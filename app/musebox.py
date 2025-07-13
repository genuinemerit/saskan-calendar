#!python
"""
:module:    MuseBox.py

:author:    PQ (pq_rfw @ pm.me)

Define sets of immutable components to use in the music core
of the Saskan game.

Each section can be accessed via the unified `MUSEBOX` object.

For usage examples, see the comments at the bottom or refer to tests.

See these references for more information on music21 library:
https://www.music21.org/music21docs/
web.mit.edu/music21/doc/genindex.html
web.mit.edu/music21/doc/py-modindex.html
The "genindex" link is the best detailed technical reference.

:description:
    Move these comments into the docstring of the class.

    Class also used for deriving chordal/harmonic progressions.
    A theme is like a motif of chord progressions.
    A prog(gression) is a collection of phrases that repeat a theme.

    These materials should remain immutable.

    Class for deriving melodic progressions.

    So far I have little meta-language for defining motifs.
    No doubt better ones out there. But want to explore a bit.
    Specific pitches are assigned later,
    using both stochastic and deterministic methods.

    My little meta-language...

    motifs MO1...MOn are associated with time signatures.
    A time signature may have 1..n motifs:

    For any score, 6 motifs are required:
    '1' = primary motif
    '2' = secondary motif
    * = surprise motif, use about 2/3 thru score
    x = concluding motif, use on last bar of score
    '3' = tertiary motif
    '$' = turnaround motif, use on penultimate bar of the score
    ..but a motif can be empty.

    A motif is often broken into two half-motifs if 4/4 or 6/8 time,
        or two part-motifs (1/3 , 2/3) if 3/4 time.
    | = mid-point of the motif, if there is one.
    Each partial-motive has one to n motif-notes.

    Every motif-note has a relative duration:

    B = a beat equal to the that of the timesig denominator
        Example, in 4/4 or 3/4, a quarter note duration
    Q = 1/4 B. In 4/4, a sixteenth note.
    S = 1/2 B. In 4/4, an eighth note.
    D = 2 B. In 4/4, a half note.
    T = Triplet B. In 4/4, a triplet-eighth.
    _ - Tie note to next note.  <-- NOT implemented yet.
      - Also see enhancements for NoteSet .. the ties
        need to be defined as specific elements. So there
        could be a good variety of types of ties.

    Rests are defined by following a motify-note with 'r'.  ??

    And a relative direction:

    ^ = ascend as compared to previous note
    v = descend as compared to previous note
    ~ = either ascend or descend or stay the same, but
        do so consistently when the motif is repeated

    Rests have an 'r' instead of a direction.  Oh!

    A score is made up of n bars playing motifs,
    as they are defined, or with variations.

    Variations are rules applied to a motif.
    The simplest rule is "as is", i.e., no change.
    So far, planning to implement only a few others, like:
    - Swap the order of the partial-motifs in a bar.
    - Invert the direction rules in a partial-motive.
    - Invert the order of the motif-notes in a partial-motive.
    - Combination of those.
    - Randomly modify the dynamics of the motifs.

    NOT USING FOR NOW.. but let's add them!
    Optional modifiers for dynamics and articulation,
    if any, follow the note's duration and direction.
    P = piannissimo
    p = piano
    m = mezzo-forte
    f = forte
    F = fortissimo
    > = accent the note
    + = fermata

    Eventually want to add timbre (MIDI instrumentation / orchestration) too.
"""

import music21 as m21
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401

import method_files as mf  # noqa F401

FM = mf.FileMethods()


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
        m21_scales = [
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
            for s in m21_scales:
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
class DegreeSet:
    """
    DegreeSet analyzes the functional harmony of each (key, mode) pair
    in a ScaleSet by building triads on each scale degree and labeling
    them with Roman numeral figures.
    Since the degrees are being built by just piling up pitches from
    the ScaleSets, some chords are iterpreted as inversions.

    N.B. -- Extended Roman Numeral notations:
        Suffix	Meaning
        6	    First inversion (third in the bass)
        64	    Second inversion (fifth in the bass)
        o	    Diminished triad
        # / b	Indicates accidentals in scale degrees
        7, 9, #86, etc.
            Adds upper extensions or altered tones
            (usually if your triad "looks like" something more complex due to scale structure)
    """
    degrees: Dict[str, Dict[str, List[str]]] = field(init=False)

    def __init__(self, scale_set: 'ScaleSet'):
        object.__setattr__(self, 'degrees', self.build_degrees(scale_set))

    @staticmethod
    def build_degrees(scale_set: 'ScaleSet') -> Dict[str, Dict[str, List[str]]]:
        result = {}

        for key, modes in scale_set.scale.items():
            result[key] = {}
            for mode, scale in modes.items():
                try:
                    scale_pitches = scale.getPitches(key + '4', key + '5')[:7]
                    degree_labels = []

                    for i in range(7):
                        triad = m21.chord.Chord([
                            scale_pitches[i % 7],
                            scale_pitches[(i + 2) % 7],
                            scale_pitches[(i + 4) % 7]
                        ])
                        try:
                            rn = m21.roman.romanNumeralFromChord(triad, key)
                            degree_labels.append(rn.figure)
                        except Exception:
                            degree_labels.append("?")
                    result[key][mode] = degree_labels
                except Exception:
                    result[key][mode] = ["?"] * 7  # fallback in case of pitch issue
        return result

    def get_degrees(self, key: str, mode: str, no_inversions: bool = False) -> List[str]:
        """
        Get the Roman numeral degrees for a given key and mode.
        If no_inversions is True, strip inversion notation from the figures.
        """
        figures = self.degrees.get(key, {}).get(mode, [])
        if no_inversions:
            simplified = []
            for fig in figures:
                # Remove common inversion figures (e.g., '64', '6', etc.)
                simplified.append(
                    fig.replace('64', '').replace('6', '')
                    .replace('#863', '').replace('86', '')
                    .strip()
                )
            return simplified
        return figures


@dataclass
class Theme:
    """
    Define a core musical "concept" in the form of a series of Degrees (chords).
    Assign a name, a category, words indicating its "flavor", and default number
      of times to repeat the theme.
    """
    id: int
    name: str
    degrees: List[str]
    category: str = "general"
    flavor: str = ""
    repeat: int = 1


class MuseBoxThemes:
    """
    A collection of default Themes.
    Note that a theme is not yet associated with a key, nor a specific motif
     regarding what to do with each of the chords.
    """
    @staticmethod
    def default_themes() -> List[Theme]:
        return [
            Theme(0,  "Resolve 1",  ["ii", "V", "I"], "jazz", "turnaround, resolving", 4),
            Theme(1,  "Anthem 1",  ["I", "V", "vi", "IV"], "pop", "anthemic, emotional", 3),
            Theme(2,  "Anthem 2",  ["I", "V", "vi", "ii"], "pop", "anthemic, emotional", 3),
            Theme(3,  "Moody 1",  ["I", "iii", "vi", "IV"], "pop", "emotional, introspective", 3),
            Theme(4,  "Moody 2",  ["I", "iii", "vi", "ii"], "pop", "emotional, introspective", 3),
            Theme(5,  "Resolve 2",  ["I", "vi", "IV", "V"], "pop", "classic resolution", 3),
            Theme(6,  "Lifting",  ["I", "IV", "vi", "V"], "pop", "emotional lift", 3),
            Theme(7,  "Resolve 3",  ["I", "vi", "ii", "V"], "jazz", "resolving, classic motion", 3),
            Theme(8,  "Resolve 4",  ["I", "ii", "vi", "V"], "jazz", "resolving, classic motion", 3),
            Theme(9,  "Steady 1",  ["I", "IV", "I", "IV", "V"], "folk", "cadence, steady", 3),
            Theme(10, "Steady 2", ["I", "IV", "I", "IV"], "folk", "cadence, steady", 3),
            Theme(11, "Ambient", ["vi", "IV", "vi", "IV"], "pop", "cyclical, ambient", 3),
            Theme(12, "Upbeat", ["ii", "V", "IV", "V"], "jazz", "resolving, upbeat", 3),
            Theme(13, "Soulful", ["ii", "V", "vi", "IV"], "jazz", "soulful resolution", 3),
            Theme(14, "Ambiguous", ["I", "iii", "IV", "V"], "general", "modally ambiguous", 3),
            Theme(15, "Tension", ["I", "ii", "iii", "IV", "V"], "general", "laddered tension", 3),
            Theme(16, "Circular", ["I", "V", "vi", "iii"], "pop", "circular motion", 3),
            Theme(17, "Steady 3", ["IV", "I", "IV", "V"], "folk", "classic cadence", 3),
            Theme(18, "Grounding 1", ["I", "I", "I", "I"], "folk", "pedal, grounding", 3),
            Theme(19, "Grounding 2", ["IV", "IV", "I", "I"], "folk", "plagal, grounding", 3),
            Theme(20, "Cyclical", ["V", "IV", "I", "V"], "folk", "plagal, cycle", 3),
            Theme(21, "Stable", ["I", "IV", "I", "I"], "folk", "reaffirming, stable", 3),
            Theme(22, "Closure", ["V", "IV", "I", "I"], "folk", "classic closure", 3),
            Theme(23, "Plagal Cadence", ['IV', 'I'], "folk", "reverent, gospel", 4),
            Theme(24, "Deceptive Cadence", ['V', 'vi'], "classical", "unexpected, clever", 4),
            Theme(25, "Backdoor II-V", ['ii', 'bVII', 'I'], "jazz", "cool, laid-back", 4),
            Theme(26, "Mixolydian Rock", ['I', 'bVII', 'IV'], "rock", "strong, anthem", 4),
            Theme(27, "Minor Modal Loop", ['i', 'bVI', 'bVII', 'i'], "modal", "looping, moody", 3),
            Theme(28, "Extended Cycle", ['iii', 'vi', 'ii', 'V', 'I'],
                  "classical", "driving, narrative", 2),
            Theme(29, "Blues Turnaround", ['I', 'IV', 'I', 'V'],
                  "blues", "traditional, foundational", 3),
            Theme(30, "Dorian Lift", ['i', 'ii', 'IV', 'V'], "modal", "minor, hopeful", 3),
            Theme(31, "Chromatic Pivot", ['I', '#iv°', 'V', 'I'],
                  "classical", "surprise, cinematic", 3),
            Theme(32, "Modal Bounce", ['bVII', 'IV', 'bVII', 'I'], "rock", "bright, returning", 3),
        ]


@dataclass
class ThemeLibrary:
    """
    A collection of Themes, along with methods for searching by Theme metadata
      and generating the full progression of Degrees (chords) associated with a Theme.
    """
    themes: List[Theme] = field(default_factory=list)

    def get_by_category(self, category: str) -> List[Theme]:
        return [t for t in self.themes if t.category == category]

    def get_by_flavor(self, flavor: str) -> List[Theme]:
        return [t for t in self.themes if flavor in t.flavor]

    def get_theme_by_name(self, theme_name: str) -> Theme:
        return next((n for n in self.themes if n.name == theme_name), None)

    def render_progression(self, names: List[str]) -> List[str]:
        chords = []
        for n in names:
            theme = self.get_theme_by_name(n)
            if theme:
                chords.extend(theme.degrees * theme.repeat)
        return chords


class MuseBoxThemeLibrary(ThemeLibrary):
    """
    Default ThemeLibary, inherits methods from ThemeLibrary()
    """
    def __init__(self):
        super().__init__(themes=MuseBoxThemes.default_themes())


@dataclass(frozen=True)
class MotifGrammar:
    """
    Lots to think about here.
    A motif is a set of rules for generating musical phrases.
    Each motif is defined by a time signature and a set of rules for generating
      musical phrases within that time signature.
    Each motif can have multiple variations, which are defined by a set of rules
      for generating musical phrases within that motif.
    The Motif Grammar is a simple meta-language for defining the following components
    of a musical composition. Once defined, these components will be used to generate
    a music21 stream.Score object and/or a MIDI file, and to save the MotifGrammar file
    as well, so that it can be reused, modified, edited later.
    Ideally, the MotifGrammar will step the user through a series of questions
    to define the components of a musical composition, and then generate the
    music21 stream.Score object and/or a MIDI file based on the user's answers, as
    well as save the MotifGrammar file for later use.  We also want to be able to
    review and modify the MotifGrammar file later, after listening to the generated music.

    A "Progression" will be passed into the MotifGrammar,
    It contains a string of Degrees (chords) in Roman Numeral notation.
    We may also want to require that some of the metadata about the Theme(s) in
      the Progression is passed in, which just describe its category and flavor.

    orchestration/instrumentation
        What kind of instruments do we want to use?
        Do we want to use a single instrument, or multiple instruments?
        Do we want to use a specific instrument for each motif?
        Do we want to instantiate each motif with its own set of instruments?
    motif
        A composition may have multiple motifs. How many do we want?
        What is the overall structure of the motifs within the composition?
        Example:
            Repeat the motif 3 times (using whatever degrees fit)
            Provide a changed motif, like a break.
            Provide a turn motif, like a turnaround.
            Provide an ending motif, like a cadence.
        This entire pattern could be repeated N times.
        What key do we want to use?
        Do we wnat to use the same key for all the bars?
        What do we want to do with a particular Degree in the Progression?
        Is it a chord that lasts for the entire bar?
        Is it a regular chord with root as base, or is it inverted? What inversion?
        Is it a chord that is arpeggiated, or broken up into notes?
        Is it a chord that is played as a melodic phrase?
        Do we break out its notes into a melodic phrase?
        How many notes -- how do we break it up?
        If it is arpeggiated, or a melodic phrase, what interval do we use?
    rhythm
        What kind of beat do we want to use?
        What time signature do we want to use?
        How many degrees do we want to use with this time signature?
            All of them?  Or will we change the time signature?
            Do we we need to tweak the Theme to fit the time signature?
        Is it a regular beat, or is it syncopated?
        Is it a regular beat, or is it a triplet?
        Is it a regular beat, or is it a dotted note?
        Is it a regular beat, or is it a rest?
        Is it a regular beat, or is it a tied note?
        For tied notes we need to consider joining degrees together, crossing bars.
        Assign notes from the NoteSet to the rhythm.
    embellishments
        What kind of embellishments do we want to use?
        Do we want to use grace notes?
        Do we want to use trills?
        Do we want to use turns?
        Do we want to use mordents?
        Do we want to use appoggiaturas?
        Do we want to use acciaccaturas?
        Do we want to use slides?
        Do we want to use bends?
        Do we want to use vibrato?
        Do we want to use dynamics?
        Do we want to use articulations?
        Do we want to use ornaments?
        Do we want to use special effects?
        Do we want to use any other embellishments?


This is *very much* like an ETL pattern:

* **Extract**: gather themes, user input, keys, motifs
* **Transform**: apply rhythmic logic, motif rules, inversion/arpeggiation logic, etc.
* **Load**: into a `music21.stream.Score`, MIDI output, or saved grammar file

The idea of **trackable, reversible, saveable transformations** is right
in line with professional tooling.

---

## ✅ Design Ideas to Support That

Here’s what we want in our architecture:

### 🧱 1. `CompositionHistory` Class

* Holds a list of **transformation steps**
* Optionally stores **CompositionPlan snapshots**
* Supports `.undo_last()` or `.restore_to(step_index)`

### 🧠 2. Each Transform Step Should Be Pure

* Don't mutate in-place
* Return a new object or modified copy
* Makes rollback and testing trivial

### 💾 3. JSON or YAML Storage

* Store `MotifGrammar` + `CompositionPlan` + steps as JSON
* Allows CLI tools, version control, even GUI support down the line

### 🔁 4. Optional `Replay()` Feature

* Rebuild a final composition from a saved grammar + step list

    """

    motif = dict()

    # 4 total beats per motif - check
    motif["4/4"] = {
        "MO1": {
            "1st": "S~S~B^        | S~S~Bv",
            "2nd": "T~B~          | T~B~",
            "3rd": "",
            "Change": "S~S~S~S~      | SrS~B~",
            "Turn": "Q~QvQ~QvQ~QvQ~Qv  | SvS^S^S^",
            "End": "B~B~          | D~",
        }
    }

    # 3 total beats per motif - check
    motif["3/4"] = {
        "MO2": {
            "1st": "D~        | S^S^",
            "2nd": "D~        | SvSv",
            "3rd": "",
            "Change": "T~        | D~",
            "Turn": "",
            "End": "S~S~      | D~",
        },
        "MO3": {
            "1st": "S~Q~Q~    | D^",
            "2nd": "S~Q~Q~    | Dv",
            "3rd": "",
            "Change": "T~        | D~",
            "Turn": "",
            "End": "S~        | B~B~",
        },
    }

    # 2 total beats per motif - check
    motif["2/2"] = {
        "MO4": {
            "1st": "B~B~",
            "2nd": "D~",
            "3rd": "",
            "Change": "S~S~S~Sr",
            "Turn": "",
            "End": "Dv",
        }
    }

    # 6 total beats per motif - check
    motif["6/8"] = {
        "MO4": {
            "1st": "B~B^B^       | B~BvBv",
            "2nd": "B~BvBv       | B~B~B~",
            "3rd": "B~B~B~       | DvB~",
            "Change": "B^B^B^       | DvB~",
            "Turn": "",
            "End": "SvSvSvSvSvSv | D~B~",
        }
    }


# Initial scaffolding for new approach to MotifGrammar
# This is a scaffold breakdown of your MotifGrammar system,
# separated into clear, modular dataclasses and related elements.
# Each one could be refined and composed into a larger CompositionEngine.


@dataclass
class Instrumentation:
    instruments: List[str]  # MIDI instrument names or numbers
    per_motif: bool = False  # True if each motif gets its own instrumentation


@dataclass
class Embellishment:
    grace_notes: bool = False
    trills: bool = False
    turns: bool = False
    mordents: bool = False
    appoggiaturas: bool = False
    acciaccaturas: bool = False
    slides: bool = False
    bends: bool = False
    vibrato: bool = False
    dynamics: Optional[str] = None  # e.g. 'p', 'mf', 'ff'
    articulations: List[str] = field(default_factory=list)
    ornaments: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)


@dataclass
class RhythmPattern:
    time_signature: str  # e.g., "4/4"
    beat_structure: List[float]  # durations per beat, e.g., [1.0, 0.5, 0.5, 1.0]
    is_syncopated: bool = False
    uses_triplets: bool = False
    uses_dotted: bool = False
    uses_rests: bool = False
    uses_ties: bool = False


@dataclass
class MotifRule:
    name: str
    degrees_used: List[str]  # e.g., ['I', 'vi', 'IV', 'V']
    note_behavior: str  # e.g., 'chord', 'arpeggio', 'melody'
    inversion: Optional[int] = None  # 0 = root, 1 = 1st inversion, etc.
    rhythm: RhythmPattern = None
    embellishments: Embellishment = None
    repeat: int = 1


@dataclass
class MotifStructure:
    motifs: List[MotifRule]
    break_motif: Optional[MotifRule] = None
    turnaround_motif: Optional[MotifRule] = None
    cadence_motif: Optional[MotifRule] = None
    repeat_structure: int = 1  # How many times the entire motif sequence repeats


@dataclass
class CompositionPlan:
    key: str
    mode: str
    theme_metadata: Dict[str, str]  # category, flavor, etc.
    progression: List[str]  # sequence of degrees
    motif_structure: MotifStructure
    instrumentation: Instrumentation
    save_path: Optional[str] = None  # where to save generated MIDI/Score


# The CompositionEngine would consume a CompositionPlan,
# generate a music21 Score, and optionally export files and grammar state.

@dataclass
class CompositionHistory:
    """
    Tracks changes to a CompositionPlan as discrete steps.
    Each step stores a shallow or deep copy of the plan and a short description.
    """
    steps: List[Dict[str, object]] = field(default_factory=list)

    def record_step(self, plan: 'CompositionPlan', description: str):
        self.steps.append({
            'description': description,
            'plan': copy.deepcopy(plan)
        })

    def undo_last(self) -> Optional['CompositionPlan']:
        if len(self.steps) > 1:
            self.steps.pop()  # Remove last step
            return copy.deepcopy(self.steps[-1]['plan'])
        elif self.steps:
            return copy.deepcopy(self.steps[0]['plan'])
        return None

    def restore_to(self, index: int) -> Optional['CompositionPlan']:
        if 0 <= index < len(self.steps):
            return copy.deepcopy(self.steps[index]['plan'])
        return None

    def describe_history(self) -> List[str]:
        return [f"Step {i}: {step['description']}" for i, step in enumerate(self.steps)]


@dataclass(frozen=True)
class MuseBox:
    notes: NoteSet
    scales: ScaleSet
    degrees: DegreeSet
    themes: Theme
    progressions: ThemeLibrary
    motifs: MotifGrammar


# MUSEBOX = MuseBox(
#     notes=NoteSet(),
#     scales=ScaleSet(),
#     degrees=DegreeSet(),
#     themes=Theme(),
#     progressions=ThemeLibrary(),
#     motifs=MotifGrammar()
# )
# The MUSEBOX object is now ready to be used in the application.
# This structure allows for easy access to all musical components defined in MuseBox.
# Example usage:
# print(MUSEBOX.notes.note['plain']['quarter'])     # Access a quarter note
# print(MUSEBOX.scales.scale['C']['major'])         # Access C major
# print(MUSEBOX.themes.theme[0])                    # Access the first theme
# print(MUSEBOX.degrees.degree['I'])               # Access the degree I
# print(MUSEBOX.progressions.prog[0])               # Access the first progression
# print(MUSEBOX.motifs.motif['4/4']['MO1']['1st'])  # Access a motif in 4/4 time
