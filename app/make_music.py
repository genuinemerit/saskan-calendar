from pprint import pprint as pp # noqa F401
import music_core as mus
from musebox import NoteSet, ScaleSet


"""
Text, experiment with music generation using music21.
"""


def basic_tests():
    """
    Check the basic functionality of the music_core and musebox modules.
    """
    results = ""
    messages = ""

    test = "\n01. Init. No data."
    MUS = mus.MusicCore(p_data=[])
    if MUS.DB == {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tMusicCore DB should be empty with no data provided."

    test = "\n02. Init. Bad data file name."
    f = ["bad_file_name"]  # Example of a valid data file name
    MUS = mus.MusicCore(p_data=f)
    if MUS.DB == {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should be empty."

    test = "\n03. Init. Good data file name."
    f = ["moons_data"]  # Example of a valid data file name
    MUS = mus.MusicCore(p_data=f)
    if MUS.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n04. Init. Good and bad file names."
    f = ["moons_data", "bad_data_file"]  # Example of a valid data file name
    MUS = mus.MusicCore(p_data=f)
    if MUS.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n05. Init. Good file name as a string."
    f = "moons_data"  # Example of a valid data file name sent as a string
    MUS = mus.MusicCore(p_data=f)
    if MUS.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n06. Init. Two good file names."
    f = ["moons_data", "lore_events"]  # Example of two valid data file names
    MUS = mus.MusicCore(p_data=f)
    if MUS.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    # Using the MUS instance created in test 06 to get data by type or key
    test = "\n07. Get data by type."
    data_type = "moons"
    data = MUS.get_data_by_type(data_type)
    if isinstance(data, list) and len(data) > 0:
        results += "."
    else:
        results += "X"
        messages += test + "\tData should be a non-empty list."

    test = "\n08. Get data by key (file name)."
    data_key = "moons_data"
    data = MUS.get_data_by_key(data_key)
    if isinstance(data, list) and len(data) > 0:
        results += "."
    else:
        results += "X"
        messages += test + "\tData should be a non-empty list."

    MUS.list_db()  # Print the contents of the DB

    print(f"\n{results}\n{messages}")

    # Next, some explicit checks on NS.note values.

    NS = NoteSet()
    print(f"\ndisplay_notes:\n{NS.display_notes()}")

    # Next, some explicit checks on SS.scale values.
    SS = ScaleSet()
    print(f"\ndisplay_scale() [all scales]:\n{SS.display_scale()}")
    print(f"\nget_modes(harmonicminor):\n{SS.get_modes('harmonicminor')}")
    print(f"\nget_key_signatures [all signatures]:\n{SS.get_key_signatures()}")
    print(f"\nget_key_signatures [all modes in C]:\n{SS.get_key_signatures(key='C')}")
    print(f"\nget_key_signatures [all major modes]:\n{SS.get_key_signatures(mode='major')}")
    print(f"\nget_key_signatures [C major]:\n{SS.get_key_signatures(key='C', mode='major')}")


if __name__ == "__main__":
    basic_tests()
