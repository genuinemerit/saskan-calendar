#!python
"""
:module:    mb_tools.py
:author:    PQ (pq_rfw @ pm.me)

Define helper functions for MuseBox.
"""
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401


def pitch_from_diatonic_number(dn: int) -> str:
    """
    Converts a diatonic note number to a pitch name + octave string.
    E.g., 31 -> 'F4', 35 -> 'B4', 36 -> 'C5'
    """
    base_letters = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    letter = base_letters[dn % 7]
    octave = dn // 7
    return f"{letter}{octave}"


def prompt_for_value(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️  Input cannot be empty. Please try again.")


def to_pascal_case(text: str) -> str:
    # Replace underscores with spaces, split into words, capitalize, and join
    return ''.join(word.capitalize() for word in text.replace('_', ' ').split())
