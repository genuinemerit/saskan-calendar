#!python
"""
:module:    mb_design.py

:author:    PQ (pq_rfw @ pm.me)

Define methods and tools to use to assemble motifs, rhythms, phrases,
voices and compositions.

"""

import music21 as m21   # noqa: F401
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field   # noqa: F401
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional, Any  # noqa: F401


@dataclass(frozen=True)
class MotifGrammar:
    """
    A Motif is a set of rules for generating musical Phrases applied to a Progression. It is
      the result of applying a MotifGrammar to a Progression in order to create a Phrase.

    The MotifGrammar is a meta-language that defines components of a musical Phrase and
      a kind of "compiler" for generating Motifs based on those rules. The Grammar (rules) are
      defined by the user, but a pre-configured set of grammars is provided.  The MotifGrammar
      consists of a set of rules that define how to generate Motifs based on a set of Degrees

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
    A Phrase consists of N bars, each bar containing N Notes.

    A Progression is a set of Themes, which are defined by a set of Degrees (chords), and
      it should also include metadata about the Themes in the Progression.

    A Composition is a set of fully realized Progressions, that is, its Phrases are complete
      in the sense that all of its Phrases are defined by a set of Notes, its MotifGrammar
      is complete.

    Each Phrase (defined by a MotifGrammar) has a time signature.
      A Phrase may have 1 or more Voices.

    Each Voice is a Role for a given Phrase covering the same set of Degrees, but with a
        modified MotifGrammar. A Phrase has one Voice by default.
    - A Voice may or may not be associated with a specific instrument.

    A Composition is used to generate:
      - a music21 stream.Score object
      - a MIDI file
      - a MotifGrammar file (a/k/a, a MuseBox JSON or YAML file)

    The process of generating a Composition is interactive and is managed by the
      CompositionEngine.  It is an ETL-like process, where the user provides input
      and the system generates output based on that input. Each step in the process
      is reversible and editable, allowing the user to go back and modify their choices.
      The output is saved in a structured format that can be easily shared, and each
      step produces a new instance of the Composition, tracked by a CompositionHistory.
    Each transformation step is pure:
    - Don't mutate in-place
    - Return a new object or modified copy
    - Make rollback and testing trivial

    The CompositionPlan:
    - Defines the overall structure of the ETL process for creating a Composition
    - Identifies what methods, classes, data structures are needed in each step
    - Provides a high-level overview of the transformation pipeline
    - Provides a way to visualize the entire process
    - Provides a scaffold for using a plug-in architecture making it easy to add new steps
      or to modify, extend, enhance existing ones.

    The CompositionHistory:
    - Holds a list of transformation steps performed
    - Optionally stores CompositionPlan snapshots
    - Supports `.undo_last()` or `.restore_to(step_index)`

    All data is stored in a structured format, such as JSON or YAML:
    - Store MotifGrammar, CompositionPlan, any other relevant crafted data as JSON
    - Allows CLI tools, version control, even GUI support down the line

    Balance creative expression with solid software design for a modular, extensible
    generative music system. Its design dimensions:

    **Clarity:**
    - Each layer (Motif, Phrase, Voice, Progression, Composition) is well-defined.
    - Use common musical terms to enhance readability for musicians, while grounding
      the architecture in object-like clarity for programmers.

    **Simplicity:**
    - Separate concerns. Each part (Grammar, Plan, Engine, History) has a defined role.
    - Avoid premature optimization (e.g., handling all embellishments or dynamics from
      the start). Tag them as "plugin" features or `TODO` stubs.

    **Testability:**
    - Emphasize pure functions, immutable data, and undoable steps.
      This inherently supports good testability.
    - Add a formal "validation step" to CompositionPlan or CompositionHistory to
      confirm the resulting object is complete and musically coherent before rendering.

    **Minimum Viability:**
    To prototype or prove the system quickly, define a minimal working pipeline in code:

    1. One `Motif` rule, one `Phrase`, one `Progression`, and a static time signature
    2. Generate one Score using basic triads only (no ornamentation, one voice)
    3. Use Music21 to render and play
    4. Serialize to JSON
    5. Then add a simple CLI to run the pipeline with user input for the MotifGrammar

    This will prototype a working pipeline:
    ThemeSet + MotifGrammar => Phrase => Score => MIDI + JSON

    **Completeness:**
    - Consider: tempo, modulation, sectional form (e.g., ABA, rondo, etc.).
      Not urgent, but good next-tier features.
    - Eventually: "PlaybackConfig" or "PerformanceSettings" (e.g., tempo curves,
      swing, humanization).

    NOTES:

    orchestration/instrumentation
        What kind of instruments do we want to use?
        Do we want to use a single instrument, or multiple instruments?
        Do we want to use a specific instrument for each voice?
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
    """

    # Old prototype of MotifGrammar
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
    # embellishments: Embellishment = None
    repeat: int = 1


@dataclass
class MotifStructure:
    motifs: List[MotifRule]
    break_motif: Optional[MotifRule] = None
    turnaround_motif: Optional[MotifRule] = None
    cadence_motif: Optional[MotifRule] = None
    repeat_structure: int = 1  # How many times the entire motif sequence repeats


@dataclass
class Phrase:
    name: str


@dataclass
class Voice(Phrase):
    name: str
    instrumentation: bool = False  # True if Voice has specific instrumentation
