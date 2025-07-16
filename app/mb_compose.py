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
        # Additional attributes and methods can be added as needed.


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
        plans[0] = {"steps": {0: CompositionEngine.init_composition,
                              1: CompositionEngine.open_composition}}
        return plans


@dataclass
class CompositionHistory:
    """
    Tracks changes to a CompositionPlan as discrete steps.
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

    def record_comp(self, comp: Composition):
        """Record step metadata to in-memory metadata and as a JSON file.
        Save the composition object as a pickled file.
        """
        # Save steps metadata to JSON file
        steps_meta = {}
        if FIL.is_file_or_dir(self.steps_path):
            steps_meta = json.loads(FIL.get_file(self.steps_path))
        steps_meta[comp.id] = {"name": comp.name,
                               "plans": comp.plans,
                               "data_name": comp.data_name}
        FIL.write_file(
            self.steps_path,
            p_data=json.dumps(steps_meta, indent=2),
            p_file_type="w+",
        )
        # Save the composition object as a pickled file
        FIL.pickle_object(comp.path, comp)


class CompositionEngine:
    """
    Tracks changes to a Composition as discrete steps.
    Each step stores a copy of the plan being implemented.
    """

    def __init__(self):
        pass

    @classmethod
    def init_composition(cls) -> Composition:
        """
        Initialize a new Composition.
        """
        created = False
        while not created:
            comp_name = MBT.prompt_for_value(f"Name of composition, or {MBT.Text.quit_prompt}: ")
            if comp_name.strip().lower() == "q":
                print(f"{MBT.Text.goodbye}")
                return None
            data_name = MBT.to_pascal_case(f"comp_{comp_name}")
            comp_path = str(MBT.set_data_path("composition", data_name, "pkl"))
            if FIL.is_file_or_dir(comp_path):
                print(f"Composition `{data_name}` already created. " +
                      "Choose a different name.")
            else:
                hist = CompositionHistory()
                comp = Composition()
                comp.id = SHL.get_uid()
                comp.name = comp_name
                comp.data_name = data_name
                comp.path = comp_path
                comp.plans[0] = {"init_composition (Step 0)": "Set ID and name of the composition."}
                hist.log_action(
                    "CompositionEngine.init_composition", f"{comp.data_name} | {comp.id}"
                )
                hist.record_comp(comp)
                created = True

    @classmethod
    def open_composition(cls) -> Composition:
        """
        Open an existing Composition.
        """
        comp_list = FIL.scan_dir(MBT.Paths.compositions, p_file_pattern="Comp*.pkl")
        if len(comp_list) == 0:
            print(f"{MBT.Text.no_data}")
            return None
        for i, c in enumerate(comp_list):
            comp_list[i] = c.stem.replace('Comp', '')
            print(f"{i+1}: {comp_list[i]}")
        picked = False
        while not picked:
            choice = MBT.prompt_for_value("Select a composition by number, " +
                                          f"or {MBT.Text.quit_prompt}: ")
            if choice.strip().lower() == "q":
                print(f"{MBT.Text.goodbye}")
                return None
            elif 1 <= int(choice) < len(comp_list) + 1:
                print(f"Selected composition: {comp_list[int(choice)-1]}")
                hist = CompositionHistory()
                comp = FIL.unpickle_object(
                    MBT.Paths.compositions / f"Comp{comp_list[int(choice)-1]}.pkl"
                )
                comp.plans[0] = {"open_composition (Step 1)": "Open an existing composition."}
                hist.log_action(
                    "CompositionEngine.open_composition",
                    f"{comp.data_name} | {comp.id}"
                )
                hist.record_comp(comp)
                picked = True
            else:
                print(f"{MBT.Text.invalid_input}")
