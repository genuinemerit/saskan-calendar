#!python
"""
:module:    MuseBox.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to drive interactive use of the MuseBox system.
This module provides the main entry point for the MuseBox system,
allowing users to create, open, and manage compositions.
For more information on music21 library, see: https://www.music21.org/music21docs/
"""

from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from typing import Dict

from mb_compose import CompositionEngine as Engine
from mb_compose import CompositionHistory as History
import mb_tools as MBT


@dataclass(frozen=True)
class CompositionPlan:
    """
    A composition plan is a static map of the steps needed to generate a piece of music
    using MuseBox components. It is like the control script for an ETL process.
    Each step of the plan produces specific metadata and saved outputs (JSON files,
    for the most part). Each step is logged using CompositionHistory methods. Each
    of the steps are handled using interface and middleware methods defined in the
    CompositionEngine class.

    The actual progress of a particular composition, that is, creation of objects, dicts,
    files and status updated, occurs in instances of the Composition class.

    A new instance of a CompositionPlan requires a Theme input.
    To edit an existing plan, use the CompositionHistory class to restore a previous state.

    The main steps of the plan are:
    1. Obtain the Theme and name the piece.
    2. Select MotifGrammar, MotifRules, and MotifStructure. (?) This includes key.
    3. Select RhythmPatterns. (May need to happen before step 2.)
    4. Define or iterate over the Phrases.
    5. Define the Voice(s) and their roles, including optionally instrumentation.
    6. Compose the music in the form of a music21 Stream, a MIDI file and/or a JSON
       or MusicXML file.
    7. Play, publish, or export the music.

    At each step, actions are logged by CompositionHistory and the plan instance is
    updated with discrete data structures for each step.  Any saved step can be restored
    using the CompositionHistory class, and then edited further using the CompositionEngine.

    As the system evolves, the CompositionPlan is likely to include additional metadata
    and sub-steps to handle more complex compositions, such as:
    - Multiple themes or motifs.
    - Complex rhythmic structures.
    - Dynamic changes in instrumentation.
    """

    plans: Dict[str, Dict] = field(
        init=False, default_factory=lambda: CompositionPlan.build_plans()
    )

    @staticmethod
    def build_plans():
        plans: dict = {}
        plans[0] = {"steps": {0: Engine.init_composition,
                              1: Engine.open_composition,
                              2: Engine.select_themes}}
        return plans


class MuseBox:
    """Class for managing the music core of the Saskan game.
    It provides access to various music components and methods.
    """

    PLAN = CompositionPlan()
    HIST = History()

    def plan_0_name_id_theme(self):
        """Plan 0: Name the composition, assign an ID, and select a theme."
        Step 0: New composition, assign an ID and name.
        Step 1: Open an existing composition. Option to change name.
        Step 2: Select a theme.
        """
        yesno = ""
        while yesno.strip()[:1].lower() not in ['n', 'o', 'q']:
            yesno = MBT.prompt_for_value(f"\nStart a {MBT.Text.new_prompt} composition, " +
                                         f"{MBT.Text.open_prompt} existing, or " +
                                         f"{MBT.Text.quit_prompt}: " +
                                         f"\n{MBT.Text.entry_prompt}")
        if yesno.strip()[:1].lower() == 'n':    # new
            id = self.PLAN.plans[0]["steps"][0]()
            print(f"\n{MBT.Text.comp_id}", id)
        elif yesno.strip()[:1].lower() == 'o':  # open
            id = self.PLAN.plans[0]["steps"][1]()
            print(f"\n{MBT.Text.comp_id}", id)
        else:
            print(f"\n{MBT.Text.goodbye}")
            exit(0)
        # This works for a sequential flow. It assumes themes not picked yet.
        # Need to engineer it so user can jump to either editing any completed
        # step or move to the next unfinished or not-started step. May make sense
        # to treat re-naming as a discrete but optional step, rather than as a
        # "sub-step" of plan 0 / step 1. Each step can have a quality of "required"
        # or "optional".
        (plan, step, status) = self.HIST.get_last_step_status(id)
        if status == "completed" and int(plan) == 0 and int(step) in [0, 1]:
            id = self.PLAN.plans[0]["steps"][2](id)
        else:
            print("\nNot ready to add a theme yet. ⛔")

    def run_cli(self):
        """Run the command line interface for MuseBox.
        """
        print(f"\n{MBT.Text.welcome}")
        self.plan_0_name_id_theme()


if __name__ == "__main__":
    MB = MuseBox()
    MB.run_cli()
