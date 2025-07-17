#!python
"""
:module:    mb_compose.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to use drive composition generation.
"""

import json
import music21 as m21  # noqa: F401
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field  # noqa: F401
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional, Any  # noqa: F401

import method_files
import method_shell
import mb_themes
import mb_tools as MBT

FIL = method_files.FileMethods()
SHL = method_shell.ShellMethods()


class Composition:
    """
    A class representing a composition in the MuseBox system.
    This class is a placeholder for the actual implementation of a composition.
    It contains methods and attributes related to a specific composition process.
    """

    def __init__(self):
        self.id = None
        self.name = None
        self.data_name = None
        self.path = None
        self.plans: Dict[str, Any] = {}
        self.theme = None
        # Add attributes and methods as needed.


class CompositionHistory:
    """
    Tracks changes to a Plan as discrete steps.
    Actions are logged using the FileMethods class.
    Each step stores a shallow or deep copy of its data.
    """

    def __init__(self):
        self.log_path = MBT.set_data_path("log", f"log_musebox_{SHL.get_date_string()}")
        if not FIL.is_file_or_dir(self.log_path):
            FIL.write_file(
                p_path=self.log_path,
                p_data=f"{SHL.get_iso_time_stamp()} | Log initialized. | \n",
            )
        self.steps_path = MBT.set_data_path("steps", "steps_musebox")
        self.steps: List[Dict[str, Any]] = []

    def log_action(self, action: str, description: str = None):
        """Record an action in the history log."""
        description = "" if description is None else description
        FIL.append_file(
            p_path=self.log_path,
            p_text=f"{SHL.get_iso_time_stamp()} | {action} | {description}\n",
        )

    def record_steps(self, comp: Composition):
        # Save steps metadata to JSON file
        steps_meta = {}
        if FIL.is_file_or_dir(self.steps_path):
            steps_meta = json.loads(FIL.get_file(self.steps_path))
        steps_meta[comp.id] = {
            "name": comp.name,
            "plans": comp.plans,
            "data_name": comp.data_name,
        }
        FIL.write_file(
            self.steps_path,
            p_data=json.dumps(steps_meta, indent=2),
            p_file_type="w+",
        )

    def record_comp(self, comp: Composition):
        """
        Save the composition object as a pickled file.
        """
        # Save the composition object as a pickled file
        FIL.pickle_object(comp.path, comp)

    def log_and_record(self, comp: Composition, action: str, description: str = None):
        """
        Log an action and record the steps and composition.
        This method combines logging and recording into a single step.
        """
        self.log_action(action, description)
        self.record_steps(comp)
        self.record_comp(comp)

    def get_steps(self) -> List[Dict[str, Any]]:
        """
        Read latest steps data from the steps file.
        Populate self.steps with the data and return it.
        If the file does not exist, return an empty list.
        :return: List of steps with their metadata..
        """
        if FIL.is_file_or_dir(self.steps_path):
            self.steps = json.loads(FIL.get_file(self.steps_path))
        return self.steps

    def get_last_step_status(self, id: int) -> tuple:
        """
        :param id: The id of the Composition object to check.
        Get the last completed step for the given composition.
        :return: The highest plan and step number, along with the status.
        """
        steps = self.get_steps()
        plan = steps[id]["plans"]
        highest_plan = max(list(plan.keys()))
        highest_step = max(list(plan[highest_plan].keys()))
        status = plan[highest_plan][highest_step]["stat"]
        return (highest_plan, highest_step, status)


class CompositionEngine:
    """
    Make changes to a Composition via discrete plan steps.
    Each step updates a copy of the plan being implemented
     and records metadata about the step.
    """

    # ========== Utility Methods ==========

    @classmethod
    def _if_exit_app(cls, prompt):
        if prompt.strip().lower() == "q":
            print(f"{MBT.Text.goodbye}")
            exit(0)

    @classmethod
    def _get_composition_list(cls) -> Dict:
        """
        Get a list of all compositions in the compositions directory.
        """
        comp_list = FIL.scan_dir(MBT.Paths.compositions, p_file_pattern="Comp*.pkl")
        if len(comp_list) == 0:
            return None
        for i, c in enumerate(comp_list):
            comp_list[i] = c.stem.replace("Comp", "")
            print(f"{i+1}: {comp_list[i]}")
        return comp_list

    @classmethod
    def _create_composition(
        cls, comp_name: str, data_name: str, comp_path: str
    ) -> Composition:
        """
        Create a Composition object with the given names and path.
        """
        comp = Composition()
        comp.id = SHL.get_uid()
        comp.name = comp_name
        comp.data_name = data_name
        comp.path = comp_path
        comp.plans: Dict = {}
        comp.plans[0]: Dict = {}
        comp.plans[0][0] = {
            "step": "init_composition",
            "desc": "Set ID and name of the composition.",
            "stat": "completed",
        }
        HIST = CompositionHistory()
        HIST.log_and_record(
            comp,
            "CompositionEngine.init_composition",
            f"Initialized composition with name: {comp_name} | ID: {comp.id}",
        )
        return comp  # Return the created Composition object

    @classmethod
    def _mark_selected_composition(cls, comp: Composition) -> Composition:
        """
        Mark the composition as selected.
        """
        comp.plans[0][1] = {
            "step": "open_composition",
            "desc": "Open an existing composition.",
            "stat": "completed",
        }
        HIST = CompositionHistory()
        HIST.log_and_record(
            comp,
            "CompositionEngine.open_composition",
            f"Opened composition with name: {comp.name} | ID: {comp.id}",
        )
        return comp

    @classmethod
    def _rename_composition(cls, comp: Composition, new_name: str) -> Composition:
        """
        Rename the composition and update its metadata.
        """
        comp.name = new_name
        comp.data_name = MBT.to_pascal_case(f"comp_{new_name}")
        FIL.rename_file(comp.path, comp.data_name)  # old path, new name
        comp.path = str(
            MBT.set_data_path("composition", comp.data_name, "pkl")
        )  # new path
        comp.plans[0][1][1] = {
            "step": "_rename_composition",
            "desc": "Renamed the composition.",
            "stat": "completed",
        }
        print(f"Renamed composition to: {comp.name} ({comp.data_name})")
        HIST = CompositionHistory()
        HIST.log_and_record(
            comp,
            "CompositionEngine.rename_composition",
            f"Renamed to: {comp.name} | ID: {comp.id}",
        )
        return comp  # Return the updated Composition object

    # ========== Plan/Step Methods ==========

    @classmethod
    def init_composition(cls):
        """
        Plan 0, Step 0: Initialize a new Composition.
        Initialize a new Composition.
        Assign an ID and name to the composition.
        """
        created = False
        id = None
        while not created:
            comp_name = MBT.prompt_for_value(
                f"Name of composition\nor {MBT.Text.quit_prompt}: "
            )
            cls._if_exit_app(comp_name)
            data_name = MBT.to_pascal_case(f"comp_{comp_name}")
            comp_path = str(MBT.set_data_path("composition", data_name, "pkl"))
            if FIL.is_file_or_dir(comp_path):
                print(
                    f"Composition `{data_name}` already created.\n"
                    + "Choose a different name."
                )
            else:
                comp = cls._create_composition(comp_name, data_name, comp_path)
                print(f"Created new composition: {comp.name} ({comp.data_name})\n")
                created = True
                id = comp.id
        return id  # Return the ID of the created composition, or None if not created

    @classmethod
    def open_composition(cls):
        """
        Plan 0, Step 1: Open an existing Composition.
        Open an existing Composition.
        Optionally change the name --> Step 1.1 (optional)
        """
        comp_list = cls._get_composition_list()
        if comp_list is None:
            print(f"{MBT.Text.no_data}")
            return None
        picked = False
        while not picked:
            choice = MBT.prompt_for_value(
                f"Select a composition by number \nor {MBT.Text.quit_prompt}: "
            )
            cls._if_exit_app(choice)
            if 1 <= int(choice) < len(comp_list) + 1:
                print(f"Selected composition: {comp_list[int(choice)-1]}")
                comp = FIL.unpickle_object(
                    MBT.Paths.compositions / f"Comp{comp_list[int(choice)-1]}.pkl"
                )
                comp = cls._mark_selected_composition(comp)
                print(f"Opened composition: {comp.name} ({comp.data_name})\n")
                picked = True
            else:
                print(f"{MBT.Text.invalid_input}")
        comp = cls._request_change_name(comp)
        return comp.id

    @classmethod
    def _request_change_name(cls, comp: Composition) -> Composition:
        """
        Plan 0, Step 1.1 (optional): Request a change of name for the current Composition.
        This step is optional and executed only after opening a composition.
        It is not triggered directly from the CLI.
        """
        assert_done = False
        while not assert_done:
            yesno = MBT.prompt_for_value(
                f"Change name of composition `{comp.name}`\n{MBT.Text.yes_no_prompt}: "
            )
            if yesno.strip().lower() in ["y", "yes"]:
                new_name = MBT.prompt_for_value(
                    "Enter new name for the composition.\n"
                    + "or [N]o change or Return to keep current name.\n"
                    + f"or {MBT.Text.quit_prompt}: "
                )
                cls._if_exit_app(new_name)
                if new_name.lower().strip() in ("", "n", "no"):
                    print(f"No change to composition name: {comp.name}")
                    assert_done = True
                    break
                else:
                    comp = cls._rename_composition(comp, new_name)
                    assert_done = True
            elif yesno.strip().lower() in ["n", "no"]:
                assert_done = True
            else:
                print(f"{MBT.Text.invalid_input}")
        return comp

    @classmethod
    def select_theme(cls, id: int) -> None:
        """
        Plan 0, Step 2: Select a theme for the currently selected Composition.
        """
        theme_library = mb_themes.MuseBoxThemeLibrary()
        categories = theme_library.list_categories()
        prompt = "Select a Theme category by number\n" \
                 f"or {MBT.Text.quit_prompt}\n"
        select_range = []
        for i, category in enumerate(categories):
            select_range.append(i + 1)
            prompt += f"  {i + 1}: {category}\n"

        assert_done = False
        while not assert_done:
            choice = MBT.prompt_for_value(prompt)
            cls._if_exit_app(choice)
            if int(choice) in select_range:
                print(f"choice: {int(choice)}")
                assert_done = True
            else:
                print(f"{MBT.Text.invalid_input}")
        category = categories[int(choice) - 1]
        themes = theme_library.get_by_category(category)
        pp((f"Themes in category '{category}': ", themes))
