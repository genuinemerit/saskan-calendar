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
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union  # noqa: F401

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
    timesig = dict()
    for sig in ("2/2", "3/4", "4/4", "6/8"):
        timesig[sig] = m21.meter.TimeSignature(sig)


@dataclass(frozen=True)
class ThemeSet:
    theme = dict()
    theme[0] = ["ii", "V", "I"]
    theme[1] = ["I", "V", "vi", "IV"]
    theme[2] = ["I", "V", "vi", "ii"]
    theme[3] = ["I", "iii", "vi", "IV"]
    theme[4] = ["I", "iii", "vi", "ii"]
    theme[5] = ["I", "vi", "IV", "V"]
    theme[6] = ["I", "IV", "vi", "V"]
    theme[7] = ["I", "vi", "ii", "V"]
    theme[8] = ["I", "ii", "vi", "V"]
    theme[9] = ["I", "IV", "I", "IV", "V"]
    theme[10] = ["I", "IV", "I", "IV"]
    theme[11] = ["vi", "IV", "vi", "IV"]
    theme[12] = ["ii", "V", "IV", "V"]
    theme[13] = ["ii", "V", "vi", "IV"]
    theme[14] = ["I", "iii", "IV", "V"]
    theme[15] = ["I", "ii", "iii", "IV", "V"]
    theme[16] = ["I", "V", "vi", "iii"]
    theme[17] = ["IV", "I", "IV", "V"]
    theme[18] = ["I", "I", "I", "I"]
    theme[19] = ["IV", "IV", "I", "I"]
    theme[20] = ["V", "IV", "I", "V"]
    theme[21] = ["I", "IV", "I", "I"]
    theme[22] = ["V", "IV", "I", "I"]


@dataclass(frozen=True)
class DegreeSet:
    degree = {"I": 1, "ii": 2, "iii": 3, "IV": 4, "V": 5, "vi": 6, "vii": 7}


@dataclass(frozen=True)
class ProgressionMap:
    prog = dict()
    theme = ThemeSet.theme
    prog[0] = {"phrases": 4, "chords": theme[0] * 4}
    prog[1] = {"phrases": 3, "chords": theme[1] * 3}
    prog[2] = {"phrases": 3, "chords": theme[2] * 3}
    prog[3] = {"phrases": 3, "chords": theme[3] * 3}
    prog[4] = {"phrases": 3, "chords": theme[4] * 3}
    prog[5] = {"phrases": 3, "chords": theme[5] * 3}
    prog[6] = {"phrases": 3, "chords": theme[6] * 3}
    prog[7] = {"phrases": 3, "chords": theme[7] * 3}
    prog[8] = {"phrases": 3, "chords": theme[8] * 3}
    prog[9] = {"phrases": 3, "chords": theme[9] * 3}
    prog[10] = {"phrases": 3, "chords": theme[10] * 2 + theme[11]}
    prog[11] = {"phrases": 4, "chords": theme[11] + theme[12] + theme[11] + theme[12]}
    prog[12] = {"phrases": 4, "chords": theme[10] + theme[13] + theme[10] + theme[13]}
    prog[13] = {"phrases": 3, "chords": theme[14] * 3}
    prog[14] = {"phrases": 3, "chords": theme[15] * 3}
    prog[15] = {"phrases": 4, "chords": theme[16] + theme[17] + theme[16] + theme[17]}
    prog[16] = {"phrases": 3, "chords": theme[18] + theme[19] + theme[20]}
    prog[17] = {"phrases": 3, "chords": theme[21] + theme[19] + theme[20]}
    prog[18] = {"phrases": 3, "chords": theme[18] + theme[19] + theme[22]}


@dataclass(frozen=True)
class MotifGrammar:
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


@dataclass(frozen=True)
class MuseBox:
    notes: NoteSet
    scales: ScaleSet
    themes: ThemeSet
    degrees: DegreeSet
    progressions: ProgressionMap
    motifs: MotifGrammar


# MUSEBOX = MuseBox(
#     notes=NoteSet(),
#     scales=ScaleSet(),
#     themes=ThemeSet(),
#     degrees=DegreeSet(),
#     progressions=ProgressionMap(),
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
