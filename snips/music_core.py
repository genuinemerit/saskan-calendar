#!python
"""
:module:    music_core.py

:author:    PQ (pq_rfw @ pm.me)

Use music21 to assign parts, phrases, pitches, notes, durations, etc.
 to nodes, then to generate scores and midi files.
"""

import music21 as m21
import random

from copy import copy
from dataclasses import dataclass   # fields
from pathlib import Path
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp
from tabulate import tabulate
from typing import Union

import method_files as mf  # noqa F401

FM = mf.FileMethods()


class MusicCore():
    """Class for managing music data, generating scores
       and other music-related methods for the Saskan game.
    """
    def __init__(self,
                 p_data: list = None):
        """
        :args: p_data: list
        - High-level names of JSON data file(s) to load from disk.
        - Assume they are stored in the app's data directory and
           have a ".json" extension.
        - Example: "moons_data" --> ../data/moons_data.json
        """
        p_data = [] if p_data is None else p_data
        self.DB: dict = self.load_data(p_data)

    def load_data(self, p_data: Union[str, list[str]]) -> dict[str, dict]:
        """
        :args:
        - p_data: list or str
        Load data from JSON files into the DB dictionary.
        :returns:
        - db: dict

        Potential Enhancements
        - Accept a directory path, and auto-load everything in it.
        - Add a .describe() method that prints schema-ish summaries of your loaded files.
        """
        db = {}
        p_data = [p_data.strip()] if isinstance(p_data, str) else p_data
        for d in p_data:
            f = Path('..') / 'data' / f"{d}.json"
            if not FM.is_file_or_dir(f):
                print(f"File {f} does not exist. Skipping.")
                continue
            db[d] = FM.get_json_file(f)
        if len(db) > 0:
            print("Loaded data files into the DB: "
                  f"{pf(list(db.keys()))}")
        return db

    def get_data_by_type(self, data_type: str) -> list:
        """Return key(s) to DB entries that match the specified data type,
           that is, the file name starts with <data_type>."""
        return [v for k, v in self.DB.items() if k.startswith(data_type)]

    def get_data_by_key(self, data_key: str) -> dict:
        """Return the data entry for the specified key, if it exists."""
        if data_key in self.DB:
            return self.DB[data_key]
        else:
            return []

    def list_db(self) -> None:
        """Print summary of DB contents."""
        print(tabulate([[k, len(v)] for k, v in self.DB.items()], headers=["Data", "Entries"]))

