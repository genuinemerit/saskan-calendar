#!python
"""
:module:    mb_compose.py

:author:    PQ (pq_rfw @ pm.me)

Define methods to use drive composition generation.
"""

import json  # For JSON file handling
import music21 as m21  # noqa: F401
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field  # noqa: F401
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional, Any  # noqa: F401

import mb_files  # noqa: F401
import mb_tools as MBT  # noqa: F401
import method_files  # noqa F401
import method_shell  # noqa F401

FIL = method_files.FileMethods()
SHL = method_shell.ShellMethods()
MBF = mb_files.MuseBoxFiles()


class Composition:
    """
    A class representing a composition in the MuseBox system.
    This class is a placeholder for the actual implementation of a composition.
    It contains methods and attributes related to a specific composition process.
    """

    def __init__(self):
        self.id = None
        self.name = None
        self.file_type = None
        self.path = None
        self.steps: Dict[str, Any] = {}
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
        plans[0] = {
            "method": CompositionEngine.init_composition,
            "sub_steps": []
        }
        return plans


@dataclass
class CompositionHistory:
    """
    Tracks changes to a CompositionPlan as discrete steps.
    Actions are logged using the FileMethods class.
    Each step stores a shallow or deep copy of its data.
    """

    def __init__(self):
        self.log_path = MBF.set_data_path(f"log_musebox_{SHL.get_date_string()}")
        self.steps_path = MBF.set_data_path("steps_musebox")
        self.steps: List[Dict[str, Any]] = []

    def log_action(self, action: str, description: str = None):
        """Record an action in the history log."""
        description = "" if description is None else description
        FIL.append_file(p_path=self.log_path,
                        p_text=f"{SHL.get_iso_time_stamp()} | {action} | {description}\n")

    def record_comp(self, comp: Composition):
        """Record step metadata to in-memory metadata and as a JSON file.
           Record composition object as a pickled file.
        """
        # Save steps metadata to JSON file
        # TO DO:
        # Might be bettter to treat this more like a log file?
        # In any case, keep in mind that if there is a single steps metadata file,
        # it will be overwritten each time a new composition is created, so need to
        # read it first (to a list), then append the new steps and save it back (as JSON).
        if comp.name not in self.steps:
            self.steps.append({comp.id: {"name": comp.name, "steps": comp.steps}})
        else:
            self.steps[comp.id] = {"name": comp.name, "steps": comp.steps}
        FIL.write_file(self.steps_path, p_data=json.dumps(self.steps, indent=2), p_file_type="w+")
        # Save the composition object as a pickled file
        FIL.pickle_object(comp.path, comp)

    """
    steps: List[Dict[str, object]] = field(default_factory=list)

    def record_step(self, plan: "CompositionPlan", description: str):
        self.steps.append({"description": description, "plan": copy.deepcopy(plan)})

    def undo_last(self) -> Optional["CompositionPlan"]:
        if len(self.steps) > 1:
            self.steps.pop()  # Remove last step
            return copy.deepcopy(self.steps[-1]["plan"])
        elif self.steps:
            return copy.deepcopy(self.steps[0]["plan"])
        return None

    def restore_to(self, index: int) -> Optional["CompositionPlan"]:
        if 0 <= index < len(self.steps):
            return copy.deepcopy(self.steps[index]["plan"])
        return None

    def describe_history(self) -> List[str]:
        return [f"Step {i}: {step['description']}" for i, step in enumerate(self.steps)]
    """


class CompositionEngine:
    """
    Tracks changes to a CompositionPlan as discrete steps.
    Each step stores a shallow or deep copy of the plan and a short description.
    """

    def __init__(self):
        pass

    @classmethod
    def init_composition(cls) -> Composition:
        """
        Initialize a new Composition.
        TODO:
        - Make sure composition name is unique.
        """
        hist = CompositionHistory()
        comp = Composition()
        comp.id = SHL.get_uid()
        comp.name = MBT.prompt_for_value("Enter the name of the composition: ")
        comp.file_type = MBT.to_pascal_case(f"comp_{comp.name}")
        comp.path = str(MBF.set_data_path(comp.file_type)).replace(".json", ".pkl")
        comp.steps["init_composition"] = {0: "Set ID and name of the composition."}

        pp((dir(comp)))
        print(f"Log file: {hist.log_path}")

        hist.log_action("CompositionEngine.init_composition",
                        f"Initialize new composition {comp.id}")

        hist.record_comp(comp)

    """
    def apply_changes(self, changes: Dict[str, Any]):
        # Apply changes to the current plan
        for key, value in changes.items():
            setattr(self.current_plan, key, value)
        self.history.record_step(self.current_plan, "Applied changes")

    def undo_last_change(self):
        self.current_plan = self.history.undo_last() or self.current_plan

    def redo_change(self):
        self.current_plan = self.history.redo_last() or self.current_plan

    def generate_score(self) -> m21.stream.Score:
        # Placeholder: Implement actual score generation logic here
        return m21.stream.Score()

    def export_to_midi(self, file_path: str):
        # Placeholder: Implement actual MIDI export logic here

    def export_to_json(self, file_path: str):
        # Placeholder: Implement actual JSON export logic here
        pass
    """
