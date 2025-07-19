#!python
"""
:module:    mb_tools.py
:author:    PQ (pq_rfw @ pm.me)

Define helper functions for MuseBox.
"""

from colorama import init, Fore, Style  # noqa: F401
from dataclasses import dataclass, field  # noqa: F401
from pathlib import Path
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401


@dataclass(frozen=True)
class Text:
    """
    Often-used text strings for MuseBox.
    """

    init(autoreset=True)
    comp_id: str = "Composition ID: "
    confirm_exit: str = "Are you sure you want to exit? (Y/N): "
    edit_prompt: str = "[N]ext step, [E]dit, [Q]uit"
    entry_prompt: str = "==> "
    error: str = "⚠️  An error occurred. Please try again."
    goodbye: str = "Goodbye!  👋"
    invalid_input: str = "⚠️  Invalid input. Please try again."
    loading: str = "Loading data..."
    main_prompt: str = "[N]ew, [O]pen, [Q]uit"
    no_data: str = "🤨  No data available."
    ord_first: str = "First"
    ord_second: str = "Second"
    ord_third: str = "Third"
    quit_prompt: str = "[Q]uit"
    saving: str = "Saving data..."
    select_one_prompt: str = "Select one."
    welcome: str = "Welcome to MuseBox! 🎶"
    yes_no_prompt: str = "[Y]es/[N]o"


def prompt_for_value(prompt: str) -> str:
    value = input(prompt).lower().strip()
    return value


def to_pascal_case(text: str) -> str:
    """Replace underscores with spaces, split into words, capitalize, and join"""
    return "".join(word.capitalize() for word in text.replace("_", " ").split())


@dataclass(frozen=True)
class Paths:
    """
    Immutable paths used in MuseBox.
    Refine more as needed.
    """

    data: Path = Path("..") / "data"
    logs: Path = Path("..") / "data"
    compositions: Path = Path("..") / "data"


def set_data_path(path_type: str, data_name: str, ext: str = "json") -> str:
    """
    Return the path where to store the data file for the specified data name.
    """

    if path_type not in ["data", "logs", "compositions"]:
        path_type = "data"  # Default to 'data' if invalid type
    mb_path = (
        Paths.data
        if path_type == "data"
        else Paths.logs if path_type == "logs" else Paths.compositions
    )
    return Path(f"{mb_path}") / (f"{data_name}.{ext}")


def pitch_from_diatonic_number(dn: int) -> str:
    """
    Converts a diatonic note number to a pitch name + octave string.
    E.g., 31 -> 'F4', 35 -> 'B4', 36 -> 'C5'
    """

    base_letters = ["C", "D", "E", "F", "G", "A", "B"]
    letter = base_letters[dn % 7]
    octave = dn // 7
    return f"{letter}{octave}"
