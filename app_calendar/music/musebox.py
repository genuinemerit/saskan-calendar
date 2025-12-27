#!python
"""
:module:    MuseBox.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to drive interactive use of the MuseBox system.
Composition plans are defined in the CompositionPlan class.
The MuseBox class provides a command line interface (CLI) to interact with the plans.
For more information on music21 library, see: https://www.music21.org/music21docs/
"""

from colorama import init, Fore, Style
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from typing import Dict

import mb_tools as MBT
from mb_compose import CompositionEngine, CompositionHistory, CompositionMetadata


@dataclass(frozen=True)
class CompositionPlan:
    """
    The CompositionPlan maps tasks to generate a piece of music using MuseBox.
    It is is similar to an ETL process. Multiple plans need to be executed in
    a specific order. Previous plan must be completed before next one can start.

    Each plan is a sequence of steps executing methods in the CompositionEngine class.
    Each step/method performs a specific major task in the composition process.
    Steps are required or optional.
    Requried steps must complete before the next required step can start.
    All required steps in a plan must complete before the next plan can start.

    A repeatable step can be executed multiple times, in any order, as long as
    preceding required steps and preceding plans are complete.

    Composition objects are pickled for storage and recall.
    Plan and setp status metadata are stored in JSON files.
    Most activities are loggged as well.

    The plans are:
    1. Create a new composition. Assign ID, Name and Themes.
    2. Select Motif Grammar, Rules, and Structures to apply to the Themes.
       In summary: define the Motifs of the composition, including key signature(s).
    3. Select Rhythmic Patterns to apply to Motifs.
    4. Define Phrases, which are clusters of Motifs.
    5. Define Voices, Roles, and Instrumentation.
    6. Compose scores and music as music21 Stream, MIDI file, JSON, MusicXML file.
    7. Play, publish, print or export the music.

    Possible future plans:
    8. Add Lyrics, Chords, and other metadata.
    9. Add more advanced features, such as AI-assisted composition.
    10. Add more advanced features, such as AI-assisted arrangement.
    """

    plan: Dict[str, Dict] = field(
        init=False, default_factory=lambda: CompositionPlan.build_plans()
    )

    @classmethod
    def build_plans(cls):
        """
        Build the composition plans.
        This method defines the plans and their steps.
        Each plan is a dictionary with a name, description, and steps.
        Each step is a dictionary with a method to execute, and flags for optional
        and repeatable steps.
        """
        ENGINE = CompositionEngine()

        steps = [
            {"method": ENGINE.init_composition, "optional": False, "repeatable": False},
            {"method": ENGINE.open_composition, "optional": False, "repeatable": True},
            {"method": ENGINE.rename_composition, "optional": True, "repeatable": True},
            {"method": ENGINE.select_themes, "optional": False, "repeatable": True},
        ]

        plan = {
            0: {
                "name": "Plan 0: Name, ID and Themes",
                "desc": (
                    "Create a new composition, assign name and ID."
                    "\nThen select one or two themes."
                ),
                "step": {i: step for i, step in enumerate(steps)},
            }
        }

        return plan


class MuseBox:
    """
    Provide user access to MuseBox Plans, and via the Plans to Compositions.
    Main CLI entry point for the system. Create, open, and manage compositions
    via command line interface (CLI), guiding users through the processes for
    creating and managing compositions.
    """

    def __init__(self):
        self.comp_id = None  # ID of the open composition.
        self.PLAN = CompositionPlan()
        self.HIST = CompositionHistory()
        self.META = CompositionMetadata()

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

    def action_is_new(self, choice: str):
        if choice in ["n", "new"]:
            plan_0 = self.PLAN.plan[0]
            self.comp_id = plan_0["step"][0]["method"]()

    def action_is_next(self, choice: str):
        """
        Execute the next step in the composition process, either in
        the current plan or in the next plan.
        """
        if choice not in ["n", "next"]:
            return

        print("Executing next step in the composition process.")

        last_step = self.META.get_last_step_status(self.comp_id)
        last_plan_num, last_step_num = map(int, last_step)

        for n, plan in sorted(self.PLAN.plan.items()):
            if n < last_plan_num:
                continue

            for step_num, step in sorted(plan["step"].items()):
                if not step["optional"] and (
                    n > last_plan_num or step_num > last_step_num
                ):
                    self.comp_id = step["method"](self.comp_id)
                    return self.comp_id

        print("\nNo next step available. All steps completed. No more plans defined.")

    def action_is_open(self, choice: str):
        """
        Get list of open compositions and user chooses one.
        """
        if choice in ["o", "open"]:
            # print('Executing Plan 0 Step 1: Open a Composition.')
            plan_0 = self.PLAN.plan[0]
            self.comp_id = plan_0["step"][1]["method"](self.comp_id)

    def action_is_edit(self, choice: str):
        """
        Provide choice of available repeatable steps and execute
        the selected one.
        """
        if choice not in ["e", "edit"]:
            return

        last_step = self.META.get_last_step_status(self.comp_id)
        # returns a tuple (plan_num, step_num, status) of the last completed step

        print("Executing an edit step in the composition process.")
        pp(("Last step status:", last_step))
        print(f"Last completed step: Plan {last_step[0]} Step {last_step[1]}")

        last_plan_num, last_step_num, last_step_status = last_step

        steps_available = [
            (n, s, step["method"].__name__.split(".")[-1])
            for n, plan in self.PLAN.plan.items()
            if n <= last_plan_num
            for s, step in plan["step"].items()
            if step["repeatable"] and s <= last_step_num
        ]

        if not steps_available:
            print(
                "\nNo edit steps available. All steps completed or no repeatable steps defined."
            )
            return

        pick_steps = [f"{n}.{s}" for n, s, _ in steps_available]
        step_descriptions = "\n".join(f"{n}.{s} {m}" for n, s, m in steps_available)

        prompt = (
            f"\nSelect an edit step by number (e.g., '0.1' for Plan 0, Step 1):"
            f"\n{step_descriptions}"
            f"\nor {MBT.Text.quit_prompt}"
            f"\n{MBT.Text.entry_prompt}"
        )

        while choice not in pick_steps:
            choice = MBT.prompt_for_value(prompt)

            if self.action_is_quit(choice):
                exit(0)

            if not self.action_is_ok(choice, pick_steps):
                continue

            n, s = map(int, choice.split("."))
            plan = self.PLAN.plan[n]
            self.comp_id = plan["step"][s]["method"](self.comp_id)

    def main_menu_cli(self):
        """
        Main menu for the MuseBox CLI.
        TODO:
        - Look into using the click or rich libraries to enhance the CLI experience.
        - Consider adding a [H]elp option to the main menu.
        - Consider adding a [V]iew current composition option.
        """
        while True:
            menu, prompt = (
                (MBT.Text.edit_menu, MBT.Text.edit_prompt)
                if self.comp_id
                else (MBT.Text.main_menu, MBT.Text.main_prompt)
            )

            choice = ""
            while choice not in menu:
                choice = MBT.prompt_for_value(f"\n{prompt} \n{MBT.Text.entry_prompt}")

                if self.action_is_quit(choice):
                    exit(0)

                if not self.action_is_ok(choice, menu):
                    continue

                # Standard main menu actions:
                actions = {
                    "new": self.action_is_new,
                    "next": self.action_is_next,
                    "open": self.action_is_open,
                    "edit": self.action_is_edit,
                }

                for action_key, action_method in actions.items():
                    if action_key in menu:
                        action_method(choice)


if __name__ == "__main__":
    """Run the command line interface for MuseBox."""
    MB = MuseBox()
    init(autoreset=True)  # Initialize colorama for colored output
    print(Fore.YELLOW + Style.BRIGHT + f"\n{MBT.Text.welcome}")
    MB.main_menu_cli()
