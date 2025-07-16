#!python
"""
:module:    MuseBox.py

:author:    PQ (pq_rfw @ pm.me)

Define sets of immutable components, pre-loaded toolboxes, and methods
 to use in the music core of the Saskan game.

For usage examples, see the comments at the bottom or refer to tests.

SFor more information on music21 library, see: https://www.music21.org/music21docs/

"""

from copy import copy, deepcopy  # noqa: F401
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401

import mb_tools as MBT
import mb_files
from mb_compose import CompositionPlan
MBF = mb_files.MuseBoxFiles()
PLAN = CompositionPlan()
# import mb_dictionary as MD
# import mb_instruments as MI
# import mb_themes as MT
# import mb_design as DS


class MuseBox:
    """Class for managing the music core of the Saskan game.
    It provides access to various music components and methods.
    """

    def __init__(self):
        pass
        # self.Tools = MBT
        # self.Files = MBF.MuseBoxFiles
        # self.Notes = MD.NoteSet
        # self.Scales = MD.ScaleSet
        # self.TimeSignatures = MD.TimeSignatureSet
        # self.Embellishments = MD.EmbellishmentSet
        # self.Clefs = MD.ClefSet
        # self.Tempos = MD.TempoSet
        # self.Dynamics = MD.DynamicSet
        # self.MidiInstruments = MI.MidiInstrument
        # self.MidiDrums = MI.MidiDrum
        # self.Music21Instruments = MI.Music21Instrument
        # self.Degrees = MT.DegreeSet   # requires scaleset as input
        # self.Themes = MT.MuseBoxThemeLibrary
        # self.MotifGrammar = DS.MotifGrammar
        # self.MotifRules = DS.MotifRule
        # self.RhythmPatterns = DS.RhythmPattern
        # self.MotifStructure = DS.MotifStructure
        # self.Phrase = DS.Phrase
        # self.Voice = DS.Voice
        # self.Composition = MC.Composition
        # self.Plan = MC.CompositionPlan
        # self.History = MC.CompositionHistory
        # self.Engine = MC.CompositionEngine

    def start_cli(self):
        """Start the command line interface for MuseBox."""
        print(f"{MBT.Text.welcome}\n")
        yesno = ""
        while yesno.strip()[:1].lower() not in ['n', 'o', 'q']:
            yesno = MBT.prompt_for_value(f"Start a {MBT.Text.new_prompt} composition, " +
                                         f"{MBT.Text.open_prompt} existing, or " +
                                         f"{MBT.Text.quit_prompt}: ")
        if yesno.strip()[:1].lower() == 'n':
            PLAN.plans[0]["steps"][0]()
        else:
            print(f"{MBT.Text.goodbye}")


if __name__ == "__main__":
    MB = MuseBox()
    MB.start_cli()
