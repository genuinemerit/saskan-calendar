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
        self.themes: Dict[str, Any] = {}
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

    # ========== Metadata Methods ==========
    # May want to consider moving these to a separate class
    # that handles metadata operations for compositions.
    # =======================================

    def get_comp_ids(self) -> Dict[str, Dict[str, Any]]:
        """
        Read basic metadata from the steps JSON file.
        :return: Dictionary of composition IDs with their metadata.
        """
        comp_ids = {}
        if FIL.is_file_or_dir(self.steps_path):
            self.steps = json.loads(FIL.get_file(self.steps_path))
            for comp_id, data in self.steps.items():
                comp_ids[comp_id] = {
                    "name": data["name"],
                    "plans": data["plans"],
                    "data_name": data["data_name"],
                }
        return comp_ids

    def get_steps(self) -> List[Dict[str, Any]]:
        """
        :return: List of steps with their metadata.
        """
        if FIL.is_file_or_dir(self.steps_path):
            self.steps = json.loads(FIL.get_file(self.steps_path))
        return self.steps

    def get_last_step_status(self, id: int) -> tuple:
        """
        :param id: The id of the Composition object to check.
        Get the last completed step for the given composition.
        :return: The highest plan and step number, along with its status.
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
    Consider breakig this class into smaller classes,
    maybe one for GUI interaction and presentation,
    one for data management, and one for more detailed
    composition logic, like building up themes or motifs,
    or possibly using sub-classes for each plan step.
    """

    # ========== Utility Methods ==========
    # These can probably go elsewhere.
    # =======================================

    @classmethod
    def _if_exit_app(cls, prompt):
        # TODO;
        # See similar method in mb_musebox.py
        # Can we use a commoon method? Maybe in mb_tools.py?
        if prompt.strip().lower() == "q":
            print(f"\n{MBT.Text.goodbye}")
            exit(0)

    @classmethod
    def _get_composition_list(cls) -> Dict:
        """
        Get a list of all compositions in the compositions directory.
        May want to move this to a "metadata" class.
        We also need a "get_composition_by_id" method.
        """
        comp_list = FIL.scan_dir(MBT.Paths.compositions, p_file_pattern="Comp*.pkl")
        if len(comp_list) == 0:
            return None
        for i, c in enumerate(comp_list):
            comp_list[i] = c.stem.replace("Comp", "")
            print(f"{i+1}: {comp_list[i]}")
        return comp_list

    # ========== Worker Methods ==========
    # These methods are used internally by the main called methods.
    # They are not intended to be called directly by the user.
    # Generally, they prepare data to to be stored and should
    # always return an updated Composition object.
    # =======================================

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
        Give this "worker" method a different name from its calling method.
        """
        comp.name = new_name
        comp.data_name = MBT.to_pascal_case(f"comp_{new_name}")
        FIL.rename_file(comp.path, comp.data_name)  # old path, new name
        comp.path = str(
            MBT.set_data_path("composition", comp.data_name, "pkl")
        )  # new path
        comp.plans[0][2] = {
            "step": "rename_composition",
            "desc": "Renamed the composition.",
            "stat": "completed",
        }
        print(f"\nRenamed composition to: {comp.name} ({comp.data_name})")
        HIST = CompositionHistory()
        HIST.log_and_record(
            comp,
            "CompositionEngine.rename_composition",
            f"Renamed to: {comp.name} | ID: {comp.id}",
        )
        return comp  # Return the updated Composition object

    @classmethod
    def _get_theme_categories(cls) -> tuple:
        """
        Return theme_library, theme_cats and cat_nums
        TODO:
        - Consider moving this to a separate class that handles theme operations,
          or one that pulls in data and objects from the various static dataclasses.
        - OR it could be a method of the mb_themes.MuseBoxThemeLibrary class.
        """
        theme_library = mb_themes.MuseBoxThemeLibrary()
        theme_cats = theme_library.list_categories()
        cat_nums = []
        cat_prompt = ""
        for i, category in enumerate(theme_cats):
            cat_nums.append(i + 1)
            cat_prompt += f"  {i + 1}: {category}\n"
        return (theme_library, theme_cats, cat_nums, cat_prompt)

    @classmethod
    def _save_theme_picks(cls, comp_id: str, picks: list, themes: list) -> Composition:
        """
        :param: comp_id (str) - Composition unique ID
        :param: picks (List of int) - Theme IDs to add to Composition
        :param: thems (List of Theme objects) - From selected categories
        Update the Composition object with selected themes.
        """
        HIST = CompositionHistory()
        step = HIST.get_steps()[comp_id]
        comp = FIL.unpickle_object(MBT.Paths.compositions / f"{step["data_name"]}.pkl")
        comp.plans[0][3] = {
            "step": "select_themes",
            "desc": "Select themes for the composition.",
            "stat": "completed",
        }
        comp.themes: Dict = {}
        for p in picks:
            for t in themes:
                if p == t.id:
                    comp.themes[p] = t
        HIST.log_and_record(
            comp,
            "CompositionEngine.select_themes",
            f"Themes selected: {str(picks)} | ID: {comp.id}",
        )
        return comp  # Return the updated Composition object

    # ========== Plan/Step Methods ==========
    # For these main methods, always pass in and return the Composition ID.
    # Don't assume the user has a Composition object in memory.
    # Do assume all methods can handled a composition ID passed in, including
    # one that is nul (None).
    # =======================================

    @classmethod
    def init_composition(cls, comp_id=None) -> Optional[int]:
        """
        Plan 0, Step 0: Initialize a new Composition.
        Initialize a new Composition.
        Assign an ID and name to the composition.
        :returns: (int) - The ID of the newly created Composition.
        If the user chooses to quit, return None.
        """
        created = False
        id = None
        while not created:
            comp_name = MBT.prompt_for_value(
                f"\nName of composition\nor {MBT.Text.quit_prompt}" +
                f"\n{MBT.Text.entry_prompt}"
            )
            cls._if_exit_app(comp_name)
            data_name = MBT.to_pascal_case(f"comp_{comp_name}")
            comp_path = str(MBT.set_data_path("composition", data_name, "pkl"))
            if FIL.is_file_or_dir(comp_path):
                print(
                    f"\nComposition `{data_name}` already created.\n"
                    + "Choose a different name."
                )
            else:
                comp = cls._create_composition(comp_name, data_name, comp_path)
                print(f"\nCreated new composition: {comp.name} ({comp.data_name})")
                created = True
                id = comp.id
        return id

    @classmethod
    def open_composition(cls, comp_id) -> Optional[int]:
        """
        Plan 0, Step 1: Open an existing Composition.
        Open an existing Composition.
        May be executed at any time against an existing comp.
        Required for most other steps.
        """
        comp_list = cls._get_composition_list()
        if comp_list is None:
            print(f"{MBT.Text.no_data}")
            return None
        picked = False
        while not picked:
            choice = MBT.prompt_for_value(
                f"\nSelect a composition by number \nor {MBT.Text.quit_prompt}: " +
                f"\n{MBT.Text.entry_prompt}"
            )
            cls._if_exit_app(choice)
            if 1 <= int(choice) < len(comp_list) + 1:
                comp = FIL.unpickle_object(
                    MBT.Paths.compositions / f"Comp{comp_list[int(choice)-1]}.pkl"
                )
                comp = cls._mark_selected_composition(comp)
                print(f"\nOpened composition: {comp.name} ({comp.data_name})")
                picked = True
            else:
                print(f"\n{MBT.Text.invalid_input}")
        return comp.id

    @classmethod
    def rename_composition(cls, comp_id: int) -> Optional[int]:
        """
        Plan 0, Step 2 (optional): Request a change of name for the identified Composition.
        This step is optional and can be executed at any time against an existing comp.
        TODO:
        Retrieve the Composition object by its ID.
        """
        assert_done = False
        while not assert_done:
            yesno = MBT.prompt_for_value(
                f"\nChange name of composition `{comp.name}`" +
                f"\n{MBT.Text.yes_no_prompt}"
                f"\n{MBT.Text.entry_prompt}"
            )
            if yesno.strip().lower() in ["y", "yes"]:
                prompt = (
                    "\nEnter new name for the composition.\n"
                    + "or [N]o change or Return to keep current name.\n"
                    + f"or {MBT.Text.quit_prompt}"
                    + f"\n{MBT.Text.entry_prompt}"
                )
                new_name = MBT.prompt_for_value(prompt)
                cls._if_exit_app(new_name)
                if new_name.lower().strip() in ("", "n", "no"):
                    print(f"\nNo change to composition name: {comp.name}")
                    assert_done = True
                    break
                else:
                    comp = cls._rename_composition(comp, new_name)
                    assert_done = True
            elif yesno.strip().lower() in ["n", "no"]:
                assert_done = True
            else:
                print(f"\n{MBT.Text.invalid_input}")
        return comp

    @classmethod
    def _select_themes_by_category(cls) -> list:
        """
        Pick one or two theme categories.
        :returns: (list) of Themes in the selected categories.
        TODO:
        - Consider moving this to a separate class that handles theme operations?
          It is properly just an extension to the main method, and not a "worker" method,
          that is, it is still dealing with presentation and user interaction.
          I split it up just to prevent the main method from being too long.
        """
        theme_library, theme_cats, cat_nums, cat_prompt = cls._get_theme_categories()
        comp_themes = []
        ords = [MBT.Text.ord_first, MBT.Text.ord_second]
        for o in ords:
            # FIX ==> simplify by accepting up to two numbers in one choice.
            prompt = (
                f"\nSelect {o} Theme category by number\n"
                f"or {MBT.Text.quit_prompt}\n{cat_prompt}"
            )
            prompt += f"\n{MBT.Text.entry_prompt}"
            assert_done = False
            while not assert_done:
                choice = MBT.prompt_for_value(prompt)
                cls._if_exit_app(choice)
                if int(choice) in cat_nums:
                    cat = theme_cats[int(choice) - 1]
                    for theme in theme_library.get_by_category(cat):
                        comp_themes.append(theme)
                    assert_done = True
                else:
                    print(f"\n{MBT.Text.invalid_input}")
            if o == MBT.Text.ord_second:
                break
            else:
                while True:
                    prompt = f"\nSelect more categories? {MBT.Text.yes_no_prompt}"
                    prompt += f"\n{MBT.Text.entry_prompt}"
                    choice = MBT.prompt_for_value(prompt)
                    if choice.strip().lower() in ["n", "no"]:
                        more = False
                        break
                    elif choice.strip().lower() in ["y", "yes"]:
                        more = True
                        break
                if not more:
                    break
        return comp_themes

    @classmethod
    def select_themes(cls, id: int) -> Optional[int]:
        """
        Plan 0, Step 3: Select up to three themes for the Composition.
        """
        themes = cls._select_themes_by_category()
        prompt = (
            "\nSelect up to 3 Themes by ID. Separate number by commas.\n"
            + "For example: 23, 8, 19"
        )
        theme_ids = []
        for theme in themes:
            if f"ID: {theme.id}" not in prompt:
                theme_ids.append(int(theme.id))
                prompt += (
                    f"\nID: {theme.id}\t{theme.category}   {theme.name}   {theme.degrees}"
                    + f"\trepeats: {theme.repeat}  flavor: {theme.flavor}"
                )
        prompt += f"\n{MBT.Text.entry_prompt}"
        ok = False
        while not ok:
            choice = MBT.prompt_for_value(prompt)
            try:
                err = False
                for p in choice.split(","):
                    if int(p.strip()) not in theme_ids:
                        print(f"\n[{p.strip()}] {MBT.Text.invalid_input}")
                        err = True
                        break
                if err:
                    continue
                picks = [int(x.strip()) for x in choice.split(",")]
                ok = True
            except Exception as e:
                print(f"{e}")

        print(f"\nYou picked: {picks}")
        comp = cls._save_theme_picks(id, picks, themes)
        return comp.id
