#!python
"""
:module:    mb_themes.py
:author:    PQ (pq_rfw @ pm.me)

Define sets of Degrees and Themes for use in composing music.
"""

import music21 as m21
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401

from mb_dictionary import ScaleSet  # noqa: F401


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

    def __init__(self, scale_set: "ScaleSet"):
        object.__setattr__(self, "degrees", self.build_degrees(scale_set))

    @staticmethod
    def build_degrees(scale_set: "ScaleSet") -> Dict[str, Dict[str, List[str]]]:
        result = {}

        for key, modes in scale_set.scale.items():
            result[key] = {}
            for mode, scale in modes.items():
                try:
                    scale_pitches = scale.getPitches(key + "4", key + "5")[:7]
                    degree_labels = []

                    for i in range(7):
                        triad = m21.chord.Chord(
                            [
                                scale_pitches[i % 7],
                                scale_pitches[(i + 2) % 7],
                                scale_pitches[(i + 4) % 7],
                            ]
                        )
                        try:
                            rn = m21.roman.romanNumeralFromChord(triad, key)
                            degree_labels.append(rn.figure)
                        except Exception:
                            degree_labels.append("?")
                    result[key][mode] = degree_labels
                except Exception:
                    result[key][mode] = ["?"] * 7  # fallback in case of pitch issue
        return result

    def get_degrees(
        self, key: str, mode: str, no_inversions: bool = False
    ) -> List[str]:
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
                    fig.replace("64", "")
                    .replace("6", "")
                    .replace("#863", "")
                    .replace("86", "")
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
            Theme(0, "Resolve 1", ["ii", "V", "I"], "jazz", "turnaround, resolving", 4),
            Theme(
                1, "Anthem 1", ["I", "V", "vi", "IV"], "pop", "anthemic, emotional", 3
            ),
            Theme(
                2, "Anthem 2", ["I", "V", "vi", "ii"], "pop", "anthemic, emotional", 3
            ),
            Theme(
                3,
                "Moody 1",
                ["I", "iii", "vi", "IV"],
                "pop",
                "emotional, introspective",
                3,
            ),
            Theme(
                4,
                "Moody 2",
                ["I", "iii", "vi", "ii"],
                "pop",
                "emotional, introspective",
                3,
            ),
            Theme(
                5, "Resolve 2", ["I", "vi", "IV", "V"], "pop", "classic resolution", 3
            ),
            Theme(6, "Lifting", ["I", "IV", "vi", "V"], "pop", "emotional lift", 3),
            Theme(
                7,
                "Resolve 3",
                ["I", "vi", "ii", "V"],
                "jazz",
                "resolving, classic motion",
                3,
            ),
            Theme(
                8,
                "Resolve 4",
                ["I", "ii", "vi", "V"],
                "jazz",
                "resolving, classic motion",
                3,
            ),
            Theme(
                9, "Steady 1", ["I", "IV", "I", "IV", "V"], "folk", "cadence, steady", 3
            ),
            Theme(10, "Steady 2", ["I", "IV", "I", "IV"], "folk", "cadence, steady", 3),
            Theme(
                11, "Ambient", ["vi", "IV", "vi", "IV"], "pop", "cyclical, ambient", 3
            ),
            Theme(12, "Upbeat", ["ii", "V", "IV", "V"], "jazz", "resolving, upbeat", 3),
            Theme(
                13, "Soulful", ["ii", "V", "vi", "IV"], "jazz", "soulful resolution", 3
            ),
            Theme(
                14,
                "Ambiguous",
                ["I", "iii", "IV", "V"],
                "general",
                "modally ambiguous",
                3,
            ),
            Theme(
                15,
                "Tension",
                ["I", "ii", "iii", "IV", "V"],
                "general",
                "laddered tension",
                3,
            ),
            Theme(16, "Circular", ["I", "V", "vi", "iii"], "pop", "circular motion", 3),
            Theme(17, "Steady 3", ["IV", "I", "IV", "V"], "folk", "classic cadence", 3),
            Theme(
                18, "Grounding 1", ["I", "I", "I", "I"], "folk", "pedal, grounding", 3
            ),
            Theme(
                19,
                "Grounding 2",
                ["IV", "IV", "I", "I"],
                "folk",
                "plagal, grounding",
                3,
            ),
            Theme(20, "Cyclical", ["V", "IV", "I", "V"], "folk", "plagal, cycle", 3),
            Theme(
                21, "Stable", ["I", "IV", "I", "I"], "folk", "reaffirming, stable", 3
            ),
            Theme(22, "Closure", ["V", "IV", "I", "I"], "folk", "classic closure", 3),
            Theme(23, "Plagal Cadence", ["IV", "I"], "folk", "reverent, gospel", 4),
            Theme(
                24,
                "Deceptive Cadence",
                ["V", "vi"],
                "classical",
                "unexpected, clever",
                4,
            ),
            Theme(
                25, "Backdoor II-V", ["ii", "bVII", "I"], "jazz", "cool, laid-back", 4
            ),
            Theme(
                26, "Mixolydian Rock", ["I", "bVII", "IV"], "rock", "strong, anthem", 4
            ),
            Theme(
                27,
                "Minor Modal Loop",
                ["i", "bVI", "bVII", "i"],
                "modal",
                "looping, moody",
                3,
            ),
            Theme(
                28,
                "Extended Cycle",
                ["iii", "vi", "ii", "V", "I"],
                "classical",
                "driving, narrative",
                2,
            ),
            Theme(
                29,
                "Blues Turnaround",
                ["I", "IV", "I", "V"],
                "blues",
                "traditional, foundational",
                3,
            ),
            Theme(
                30, "Dorian Lift", ["i", "ii", "IV", "V"], "modal", "minor, hopeful", 3
            ),
            Theme(
                31,
                "Chromatic Pivot",
                ["I", "#iv°", "V", "I"],
                "classical",
                "surprise, cinematic",
                3,
            ),
            Theme(
                32,
                "Modal Bounce",
                ["bVII", "IV", "bVII", "I"],
                "rock",
                "bright, returning",
                3,
            ),
        ]


@dataclass
class ThemeLibrary:
    """
    A collection of Themes, along with methods for searching by Theme metadata
      and generating the full progression of Degrees (chords) associated with a Theme.
    TODO:
    - List categories of themes.
    - List flavors of themes.
    """

    themes: List[Theme] = field(default_factory=list)

    def list_categories(self) -> List[str]:
        return sorted(set(t.category for t in self.themes))

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

    def prompt_theme_categories(self) -> tuple:
        """
        Return theme_library, theme_cats, cat_nums and a preformmated
          prompt string for selecting theme categories.
        :returns: (ThemeLibrary, List[str], List[int], str)
        """
        theme_library = self
        theme_cats = self.list_categories()
        cat_nums = []
        cat_prompt = ""
        for i, category in enumerate(theme_cats):
            cat_nums.append(i + 1)
            cat_prompt += f"  {i + 1}: {category}\n"
        return (theme_library, theme_cats, cat_nums, cat_prompt)


class MuseBoxThemeLibrary(ThemeLibrary):
    """
    Default ThemeLibary, inherits methods from ThemeLibrary()
    """

    def __init__(self):
        super().__init__(themes=MuseBoxThemes.default_themes())
