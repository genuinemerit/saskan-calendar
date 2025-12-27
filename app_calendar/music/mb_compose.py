#!python
"""
:module:    mb_compose.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to drive composition generation.
"""

import json
import music21 as m21  # noqa: F401
from pathlib import Path
from typing import List, Dict, Optional, Any

from shared.utils.file_io import FileMethods
from shared.utils.shell import ShellMethods
import mb_tools as MBT
from mb_themes import MuseBoxThemeLibrary

FIL = FileMethods()
SHL = ShellMethods()
THEMES = MuseBoxThemeLibrary()


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
    "Steps metdata" is a high-level tracker of plan-step status and changes.
    The log records all actions taken on a Composition, inculuding opening.
    The Compostion object is pickled to a file for later retrieval, typically by ID.
    It holds all detail about the Composition, such as themes, motifs, and scores.
    Use the FileMethods class to write to files.
    """

    def __init__(self):
        """
        Initialize the object with paths for log and steps.
        The paths are defined in the mb_tools module.
        Inititalize the log file if it does not yet exist.
        """
        self.log_path = MBT.set_data_path("log", f"log_musebox_{SHL.get_date_string()}")
        if not FIL.is_file_or_dir(self.log_path):
            FIL.write_file(
                p_path=self.log_path,
                p_data=f"{SHL.get_iso_time_stamp()} | Log initialized. | \n",
            )
        self.steps_path = MBT.set_data_path("steps", "steps_musebox")

    def log_action(self, action: str, description: str = None):
        """Record an action in the log file."""
        description = "" if description is None else description
        FIL.append_file(
            p_path=self.log_path,
            p_text=f"{SHL.get_iso_time_stamp()} | {action} | {description}\n",
        )

    def record_steps(self, comp: Composition):
        """
        For each Composition, record steps executed and their status.
        The steps metadata is stored in a single JSON file.
        """
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
        FIL.pickle_object(comp.path, comp)

    def log_and_record(self, comp: Composition, action: str, description: str = None):
        """
        Log an action, record the plan-steps status and pickle the Composition object.
        This method combines logging, recording status and saving the Composition
          into a single step.
        """
        self.log_action(action, description)
        self.record_steps(comp)
        self.record_comp(comp)


class CompositionMetadata:
    """
    Handle metadata operations for the CompositionEngine.
    Get composition IDs, steps, last step status and Composition object by ID.
    """

    def __init__(self):
        """
        Initialize the object with paths for steps metadata file.
        """
        self.steps_path = MBT.set_data_path("steps", "steps_musebox")
        self.steps: List[Dict[str, Any]] = []

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

    def get_steps_metadata(self) -> List[Dict[str, Any]]:
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
        steps = self.get_steps_metadata()
        plan = steps[id]["plans"]
        highest_plan = max(list(plan.keys()))
        highest_step = max(list(plan[highest_plan].keys()))
        status = plan[highest_plan][highest_step]["stat"]
        return (highest_plan, highest_step, status)

    def get_composition_by_id(self, id: int) -> Optional[Composition]:
        """
        Retrieve a Composition object by its ID.
        :param id: The ID of the Composition to retrieve.
        :return: The Composition object or None if not found.
        """
        steps = self.get_steps_metadata()
        if str(id) in steps:
            comp_data = steps[str(id)]
            obj_path = Path(
                MBT.Paths.compositions / f"Comp{comp_data['data_name']}.pkl"
            )
            comp = FIL.unpickle_object(obj_path)
            return comp
        return None

    @classmethod
    def get_composition_list(cls) -> Dict:
        """
        Get a list of all compositions in the compositions directory.
        Move this to CompositionMetadata
        """
        comp_list = FIL.scan_dir(MBT.Paths.compositions, p_file_pattern="Comp*.pkl")
        if len(comp_list) == 0:
            return None
        for i, c in enumerate(comp_list):
            comp_list[i] = c.stem[4:]  # Remove 'Comp' prefix
            print(f"{i+1}: {comp_list[i]}")
        return comp_list


class CompositionData:
    """
    These methods are used internally by the CompositionEngine class.
    They are not intended to be called directly by the user.
    They prepare data to to be stored in the Composition object and
    they call the CompositionHistory methods to log and record actiosn
    and steps.
    """

    def __init__(self):
        """
        Initialize the CompositionData object.
        """
        self.HIST = CompositionHistory()
        self.META = CompositionMetadata()

    def create_composition(
        self, comp_name: str, data_name: str, comp_path: str
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
        self.HIST = CompositionHistory()
        self.HIST.log_and_record(
            comp,
            "CompositionEngine.init_composition",
            f"Initialized composition with name: {comp_name} | ID: {comp.id}",
        )
        return comp  # Return the created Composition object

    def mark_selected_composition(self, comp: Composition) -> Composition:
        """
        Mark the composition as selected.
        """
        comp.plans[0][1] = {
            "step": "open_composition",
            "desc": "Open an existing composition.",
            "stat": "completed",
        }
        self.HIST = CompositionHistory()
        self.HIST.log_and_record(
            comp,
            "CompositionEngine.open_composition",
            f"Opened composition with name: {comp.name} | ID: {comp.id}",
        )
        return comp

    def rename_composition(self, comp: Composition, new_name: str) -> Composition:
        """
        Rename the composition and update its metadata.
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
        self.HIST = CompositionHistory()
        self.HIST.log_and_record(
            comp,
            "CompositionEngine.rename_composition",
            f"Renamed to: {comp.name} | ID: {comp.id}",
        )
        return comp  # Return the updated Composition object

    def save_theme_picks(self, comp_id: str, picks: list, themes: list) -> Composition:
        """
        :param: comp_id (str) - Composition unique ID
        :param: picks (List of int) - Theme IDs to add to Composition
        :param: thems (List of Theme objects) - From selected categories
        Update the Composition object with selected themes.
        """
        step = self.META.get_steps_metadata()[comp_id]
        obj_path = Path(MBT.Paths.compositions / f"{step['data_name']}.pkl")
        comp = FIL.unpickle_object(obj_path)
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
        self.HIST.log_and_record(
            comp,
            "CompositionEngine.select_themes",
            f"Themes selected: {str(picks)} | ID: {comp.id}",
        )
        return comp  # Return the updated Composition object


class CompositionEngine:
    """
    Make changes to a Composition via discrete plan steps.
    Each step updates a copy of the plan being implemented
     and records metadata about the step.
    """

    def __init__(self):
        """
        Initialize the CompositionEngine with necessary components.
        """
        self.META = CompositionMetadata()
        self.DATA = CompositionData()
        self.comp_id = None  # ID of the open composition.

    def init_composition(self, comp_id=None) -> Optional[int]:
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
                f"\nName of composition\nor {MBT.Text.quit_prompt}"
                + f"\n{MBT.Text.entry_prompt}"
            )
            MBT.if_exit_app(comp_name)
            data_name = MBT.to_pascal_case(f"comp_{comp_name}")
            comp_path = str(MBT.set_data_path("composition", data_name, "pkl"))
            if FIL.is_file_or_dir(comp_path):
                print(
                    f"\nComposition `{data_name}` already created.\n"
                    + "Choose a different name."
                )
            else:
                comp = self.DATA.create_composition(comp_name, data_name, comp_path)
                print(f"\nCreated new composition: {comp.name} ({comp.data_name})")
                created = True
                id = comp.id
        return id

    def open_composition(self, comp_id) -> Optional[int]:
        """
        Plan 0, Step 1: Open an existing Composition.
        Open an existing Composition.
        May be executed at any time against an existing comp.
        Required for most other steps.
        """
        comp_list = self.META.get_composition_list()
        if comp_list is None:
            print(f"{MBT.Text.no_data}")
            return None
        picked = False
        while not picked:
            choice = MBT.prompt_for_value(
                f"\nSelect a composition by number \nor {MBT.Text.quit_prompt}: "
                + f"\n{MBT.Text.entry_prompt}"
            )
            MBT.if_exit_app(choice)
            if 1 <= int(choice) < len(comp_list) + 1:
                comp = FIL.unpickle_object(
                    MBT.Paths.compositions / f"Comp{comp_list[int(choice)-1]}.pkl"
                )
                comp = self.DATA.mark_selected_composition(comp)
                print(f"\nOpened composition: {comp.name} ({comp.data_name})")
                picked = True
            else:
                print(f"\n{MBT.Text.invalid_input}")
        return comp.id

    def rename_composition(self, comp_id: int) -> Optional[int]:
        """
        Plan 0, Step 2 (optional): Request a change of name for a Composition.
        Optional step. Can be executed at any time against an existing comp.
        """
        comp = self.META.get_composition_by_id(comp_id)
        assert_done = False
        while not assert_done:
            yesno = MBT.prompt_for_value(
                f"\nChange name of composition `{comp.name}`"
                + f"\n{MBT.Text.yes_no_prompt}"
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
                MBT.if_exit_app(new_name)
                if new_name.lower().strip() in ("", "n", "no"):
                    print(f"\nNo change to composition name: {comp.name}")
                    assert_done = True
                    break
                else:
                    comp = self.DATA.rename_composition(comp, new_name)
                    print(f"\nRenamed composition to: {comp.name} ({comp.data_name})")
                    assert_done = True
            elif yesno.strip().lower() in ["n", "no"]:
                assert_done = True
            else:
                print(f"\n{MBT.Text.invalid_input}")
        return comp

    def select_themes_by_category(self) -> list:
        """
        Pick one or two theme categories. A category contains 1 to N themes.
        This is an extension to the select_themes() Engine method (Plan 0, Step 3).
        It is broken out just to prevent the main method from being too long.
        :returns: (list) of Themes in the selected categories.
        """
        theme_library, theme_cats, cat_nums, cat_prompt = (
            THEMES.prompt_theme_categories()
        )
        cat_picks = []
        prompt = (
            "\nSelect one or two Categories by Number. Separate number by commas.\n"
            + "For example: 1, 3\n"
            + f"or {MBT.Text.quit_prompt}\n{cat_prompt}"
            + f"\n{MBT.Text.entry_prompt}"
        )
        ok = False
        while not ok:
            choice = MBT.prompt_for_value(prompt)
            MBT.if_exit_app(choice)
            try:
                err = False
                for c in choice.split(","):
                    if int(c.strip()) not in cat_nums:
                        print(f"\n[{c.strip()}] {MBT.Text.invalid_input}")
                        err = True
                        break
                if err:
                    continue
                cat_picks = [int(x.strip()) for x in choice.split(",")]
                if len(cat_picks) > 2 or len(cat_picks) < 1:
                    print(f"\n{MBT.Text.invalid_input}")
                    continue
                else:
                    ok = True
            except Exception as e:
                print(f"{e}")

        comp_themes = []
        for p in cat_picks:
            cat = theme_cats[p - 1]
            for theme in theme_library.get_by_category(cat):
                comp_themes.append(theme)
        return comp_themes

    def select_themes(self, id: int) -> Optional[int]:
        """
        Plan 0, Step 3: Select up to three themes for the Composition
        from the list of available themes from the selected categories.
        It calls the select_themes_by_category() method to get themes.
        :returns: (int) - The ID of the updated Composition.
        """
        themes = self.select_themes_by_category()
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
        comp = self.DATA.save_theme_picks(id, picks, themes)
        return comp.id
