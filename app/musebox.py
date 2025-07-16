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
from mb_compose import CompositionPlan
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

    def start_cli(self):
        """Start the command line interface for MuseBox.
        NEXT:
        - Based on the status of the current composition, prompt the user to
          go to the next step. For example, if a plan is active, and either
          plan 0/step 0, or plan 0 / step 1 is completed, but plan 0 / step 2
          is not started or not completed, then prompt the user to work on plan 0 / step 2,
          which will be to select and load a theme.
        - Update the steps metadata struture to indicate what plan is currently
          being executed. Also update to indicate if a step is completed,
          is currently being executed, or has been started but not completed.
          At present I am only storing the current step, but need to store all
          initiated steps and their status.
        """
        print(f"{MBT.Text.welcome}\n")
        yesno = ""
        while yesno.strip()[:1].lower() not in ['n', 'o', 'q']:
            yesno = MBT.prompt_for_value(f"Start a {MBT.Text.new_prompt} composition, " +
                                         f"{MBT.Text.open_prompt} existing, or " +
                                         f"{MBT.Text.quit_prompt}: ")
        if yesno.strip()[:1].lower() == 'n':
            PLAN.plans[0]["steps"][0]()
        elif yesno.strip()[:1].lower() == 'o':
            PLAN.plans[0]["steps"][1]()
        else:
            print(f"{MBT.Text.goodbye}")


if __name__ == "__main__":
    MB = MuseBox()
    MB.start_cli()
