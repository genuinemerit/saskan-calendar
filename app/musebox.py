#!python
"""
:module:    MuseBox.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to drive interactive use of the MuseBox system.
This module provides the main entry point for the MuseBox system,
menuing users to create, open, and manage compositions.
For more information on music21 library, see: https://www.music21.org/music21docs/
"""

from colorama import init, Fore, Style
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from typing import Dict

import mb_tools as MBT
from mb_compose import CompositionEngine, CompositionHistory


@dataclass(frozen=True)
class CompositionPlan:
    """
    The CompositionPlan maps tasks to generate a piece of music using MuseBox.
    It is is similar to an ETL process map. There are multiple plans, which need
    to be executed in a specific order. Previous plan must be completed before
    the next one can be started.

    Each plan is a sequence of steps, which are methods in the CompositionEngine class.
    Each step is a method that performs a specific task in the composition process.
    Some steps are required (non-optional), while others are optional. Non-optional
    steps must be completed before the next step can be started. All non-optional steps
    in a plan must be completed before the next plan can be started.
    Steps are tied to methods defined in the CompositionEngine class.

    Many steps are repeatable, meaning they can be executed multiple times, and in
    any order, as long as its preceding plans and non-optional steps are completed.

    The details of each composition are stored in a pickled object. The status
    of the plans and steps are stored in JSON file.  Most activities are loggged as well.

    The plans are:
    1. Create a new composition. Assign ID, Name and Themes.
    2. Select Motif Grammar, Rules, and Structures to apply to the Themes.
       In summary: define the Motifs of the composition. Includes key signature(s).
    3. Select Rhythmic Patterns to apply to the Motifs.
    4. Define Phrases, which are clusters of Motifs.
    5. Define Voices, Roles, and Instrumentation.
    6. Compose scores and music as music21 Stream, MIDI file, JSON, MusicXML file.
    7. Play, publish, print or export the music.
    """

    plan: Dict[str, Dict] = field(
        init=False, default_factory=lambda: CompositionPlan.build_plans()
    )

    @classmethod
    def build_plans(cls):
        ENGINE = CompositionEngine()
        plan: dict = {}
        plan[0] = {
            "name": "Plan 0: Name, ID and Themes",
            "desc": (
                "Create a new composition, assign name and ID."
                + "\nThen select one or two themes."
            ),
            "step": {
                0: {
                    "method": ENGINE.init_composition,
                    "optional": False,
                    "repeatable": False,
                },
                1: {
                    "method": ENGINE.open_composition,
                    "optional": False,
                    "repeatable": True,
                },
                2: {
                    "method": ENGINE.rename_composition,
                    "optional": True,
                    "repeatable": True,
                },
                3: {
                    "method": ENGINE.select_themes,
                    "optional": False,
                    "repeatable": True,
                },
            },
        }
        return plan


class MuseBox:
    """Class for providing user access to various MuseBox components and methods.
    This class serves as the main entry point for the MuseBox system, menuing users
    to create, open, and manage compositions. It provides a command line interface
    (CLI) for interacting with the system, guiding users through the process of
    creating and managing compositions.
    """

    def __init__(self):
        self.comp_id = None  # ID of the open composition.
        self.PLAN = CompositionPlan()
        self.HIST = CompositionHistory()

    def action_is_quit(self, choice: str):
        if choice in ["q", "quit"]:
            print(f"\n{MBT.Text.goodbye}")
            return True
        else:
            return False

    def action_is_ok(self, choice: str, menu: list):
        if choice in menu:
            return True
        else:
            print(f"\n{MBT.Text.invalid_input}")
            return False

    def action_new(self, choice: str):
        if choice in ["n", "new"]:
            # print('Executing Plan 0 Step 0: New Composition.')
            plan_0 = self.PLAN.plan[0]
            self.comp_id = plan_0["step"][0]["method"]()

    def action_next(self, choice: str):
        """
        Execute the next step in the composition process.
        """
        if choice in ["n", "next"]:
            last_step = self.HIST.get_last_step_status(self.comp_id)
            last_plan_num = int(last_step[0])
            last_step_num = int(last_step[1])
            for n in self.PLAN.plan.keys():
                if n < last_plan_num:
                    continue
                plan = self.PLAN.plan[n]
                for step_num, step in plan["step"].items():
                    if step["optional"] is False and step_num > last_step_num:
                        self.comp_id = step["method"](self.comp_id)
                        return
            print(
                "\nNo next step available. "
                + "All steps completed. No more plans defined."
            )

    def action_open(self, choice: str):
        """
        Get list of open compositions and user chooses one.
        """
        if choice in ["o", "open"]:
            # print('Executing Plan 0 Step 1: Open a Composition.')
            plan_0 = self.PLAN.plan[0]
            self.comp_id = plan_0["step"][1]["method"]()

    def action_edit(self, choice: str):
        """
        Execute an available edit step in the composition process.
        """
        if choice in ["e", "edit"]:
            last_step = self.HIST.get_last_step_status(self.comp_id)
            last_plan_num = int(last_step[0])
            last_step_num = int(last_step[1])
            steps_available = []
            for n in self.PLAN.plan.keys():
                if n > last_plan_num:
                    break
                plan = self.PLAN.plan[n]
                for s, step in plan["step"].items():
                    if (
                        step["repeatable"] is True
                        and n <= last_plan_num
                        and s <= last_step_num
                    ):
                        m = step["method"].__name__.split(".")[-1]
                        steps_available.append(f"Plan {n}, Step {s}, {m}")
            if not steps_available:
                print(
                    "\nNo edit steps available. "
                    + "All steps completed or no repeatable steps defined."
                )
            else:
                prompt = (
                    "\nSelect an edit step by number "
                    + "(e.g., '0.1' for Plan 0, Step 1): "
                )
                pick_steps = []
                for step in steps_available:
                    step_p = step.replace('Plan ', '').replace('Step ', '').replace(', ', '.')
                    pick_steps.append(step_p[:3])
                    prompt += f"\n{step_p}"
                prompt += f"\nor {MBT.Text.quit_prompt}"
                prompt += f"\n{MBT.Text.entry_prompt}"
                while choice not in pick_steps:
                    choice = MBT.prompt_for_value(prompt)
                    if self.action_is_quit(choice):
                        exit(0)
                    if not self.action_is_ok(choice, pick_steps):
                        continue
                    plan = self.PLAN.plan[int(choice[0])]
                    # print("\nExecuting " +
                    #       f"{plan['step'][int(choice[2])]['method'].__name__}...")
                    self.comp_id = plan["step"][int(choice[2])]["method"](self.comp_id)

    def main_menu_cli(self):
        """
        TODO:
        - Refactor this to use the CompositionPlan class more fluidly.
        - Make it more flexible to menu jumping to any step in the plan.
        - Use sequential flow to choose what to present to the user.
        - Make use of HIST methods to check status of steps and plans,
          which should determine what repeatable steps are available and
          what should be the next unfinished step in the flow.
        - Think in terms of a single "menu" presentation, which is driven by
          steps status metadata. Use familiar interactive patterns and text
          like "New", "Open", "Edit", "Quit".
        - Consider whether "Save" is appropriate. So far, a step is either
          completed or not. When it is completed, it is saved. If it is not
          completed, it has to be started again.
        MAYBE:
        - Rather than "Save", might want something more like "Lock". If a
          user wants to change a composition step that is locked, then the
          composition needs to forked or unlocked. (Maybe this is for down the road.)
        - Also consider if a [B]ack option is needed, to go back to the previous step
          or action within a step.
        - look into using the click or rich libraries to enhance CLI experience.
        """
        while True:
            # print("comp_id:", self.comp_id)
            if self.comp_id is None:
                menu = ["n", "o", "e", "q", "new", "open", "quit"]
                prompt = f"{MBT.Text.main_prompt}"
            else:
                menu = ["n", "e", "q", "next", "edit", "quit"]
                prompt = f"{MBT.Text.edit_prompt}"
            choice = ""
            while choice not in menu:
                choice = MBT.prompt_for_value(
                    f"\n{prompt} " + f"\n{MBT.Text.entry_prompt}"
                )
                if self.action_is_quit(choice):
                    exit(0)
                if not self.action_is_ok(choice, menu):
                    continue
                # Standard main menu actions:
                if "new" in menu:
                    self.action_new(choice)
                if "next" in menu:
                    self.action_next(choice)
                if "open" in menu:
                    self.action_open(choice)
                if "edit" in menu:
                    self.action_edit(choice)

        """
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
        """

    def run_cli(self):
        """Run the command line interface for MuseBox."""
        init(autoreset=True)
        print(Fore.YELLOW + Style.BRIGHT + f"\n{MBT.Text.welcome}")
        self.main_menu_cli()


if __name__ == "__main__":
    MB = MuseBox()
    MB.run_cli()
