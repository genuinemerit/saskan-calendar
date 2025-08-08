from pprint import pprint as pp # noqa F401
import musebox
# import mb_files as mfiles
# import mb_dictionary as mdict
# import mb_instruments as mbins
# import mb_themes as mtheme


"""
Test, experiment with music generation using music21.
"""


def object_tests():
    MB = musebox.MuseBox()
    pp(('MB', MB))


def file_tests():
    """
    Check the basic functionality of the music_core and musebox modules.
    """
    MB = musebox.MuseBox()
    results = ""
    messages = ""

    test = "\n01. Init. No data."
    MFIL = MB.Files(p_data=[])
    if MFIL.DB == {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tMusicCore DB should be empty with no data provided."

    test = "\n02. Init. Bad data file name."
    f = ["bad_file_name"]  # Example of a valid data file name
    MFIL = MB.Files(p_data=f)
    if MFIL.DB == {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should be empty."

    test = "\n03. Init. Good data file name."
    f = ["moons_data"]  # Example of a valid data file name
    MFIL = MB.Files(p_data=f)
    if MFIL.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n04. Init. Good and bad file names."
    f = ["moons_data", "bad_data_file"]  # Example of a valid data file name
    MFIL = MB.Files(p_data=f)
    if MFIL.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n05. Init. Good file name as a string."
    f = "moons_data"  # Example of a valid data file name sent as a string
    MFIL = MB.Files(p_data=f)
    if MFIL.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    test = "\n06. Init. Two good file names."
    f = ["moons_data", "lore_events"]  # Example of two valid data file names
    MFIL = MB.Files(p_data=f)
    if MFIL.DB != {}:
        results += "."
    else:
        results += "X"
        messages += test + "\tDB should NOT be empty."

    # Using the MFIL instance created in test 06 to get data by type or key
    test = "\n07. Get data by type."
    data_type = "moons"
    data = MFIL.get_data_by_type(data_type)
    if isinstance(data, list) and len(data) > 0:
        results += "."
    else:
        results += "X"
        messages += test + "\tData should be a non-empty list."

    test = "\n08. Get data by key (file name)."
    data_key = "moons_data"
    data = MFIL.get_data_by_key(data_key)
    if isinstance(data, list) and len(data) > 0:
        results += "."
    else:
        results += "X"
        messages += test + "\tData should be a non-empty list."

    MFIL.list_db()  # Print the contents of the DB

    print(f"\n{results}\n{messages}")

    # Next, some explicit checks on NS.note values.


def dictionary_tests():
    MB = musebox.MuseBox()

    NS = MB.Notes()
    print(f"\ndisplay_notes:\n{NS.display_notes()}")

    # Next, some explicit checks on SS.scale values.
    SS = MB.Scales()
    print(f"\ndisplay_scale() [all scales]:\n{SS.display_scale()}")
    print(f"\nget_modes(harmonicminor):\n{SS.get_modes('harmonicminor')}")
    print(f"\nget_key_signatures [all signatures]:\n{SS.get_key_signatures()}")
    print(f"\nget_key_signatures [all modes in C]:\n{SS.get_key_signatures(key='C')}")
    print(f"\nget_key_signatures [all major modes]:\n{SS.get_key_signatures(mode='major')}")
    print(f"\nget_key_signatures [C major]:\n{SS.get_key_signatures(key='C', mode='major')}")

    TS = MB.TimeSignatures()
    print(f"\nlist_all_time_sigs:\n{TS.list_all_time_sigs()}")
    print(f"\ndisplay_all_time_sigs:\n{TS.display_all_time_sigs()}")
    print(f"\nTS.get_time_sig_by_category('simple'):\n{TS.get_time_sig_by_category('simple')}")

    EM = MB.Embellishments()
    pp((EM))
    print(f"\nget_by_name('trill'): {EM.get_by_name('trill')}")
    print(f"\nget_by_symbol('tr'): {EM.get_by_symbol('tr')}")
    print(f"\nget_by_type('ornamentation'): {EM.get_by_type('ornamentation')}")

    DY = MB.Dynamics()
    pp((DY))
    print(f"\nget_by_description('piano'): {DY.get_by_description('piano')}")
    print(f"\nget_by_description('loud'): {DY.get_by_description('loud')}")
    print(f"\nget_by_symbol('p'): {DY.get_by_symbol('p')}")
    print(f"\nget_by_symbol('mp'): {DY.get_by_symbol('mp')}")
    print(f"\nget_by_symbol('fffffffffff'): {DY.get_by_symbol('fffffffffff')}")

    CL = MB.Clefs()
    pp((CL))
    print(f"\nlist_all_clefs: {CL.list_all_clefs()}")
    print(f"\nget_clef_by_name('treble'): {CL.get_clef_by_name('treble')}")
    print(f"\nget_clef_by_name('bass'): {CL.get_clef_by_name('bass')}")
    print(f"\nget_clef_by_name('8vb'): {CL.get_clef_by_name('8vb')}")

    TP = MB.Tempos()
    pp((TP))
    print(f"\nlist_all_tempos: {TP.list_all_tempos()}")
    print(f"\nget_tempo_by_name('Largo'): {TP.get_tempo_by_name('Largo')}")
    print(f"\nget_tempo_by_name('fast'): {TP.get_tempo_by_name('fast')}")
    print(f"\nget_tempo_by_name('Andante'): {TP.get_tempo_by_name('Andante')}")
    print(f"\nget_tempo_by_name('SCHNELL'): {TP.get_tempo_by_name('SCHNELL')}")
    print(f"\nget_tempo_by_name('whoziwhat?'): {TP.get_tempo_by_name('whoziwhat?')}")
    print(f"\nget_nearest_tempo_by_bpm(10): {TP.get_nearest_tempo_by_bpm(10)}")
    print(f"\nget_nearest_tempo_by_bpm(60): {TP.get_nearest_tempo_by_bpm(60)}")
    print(f"\nget_nearest_tempo_by_bpm(120): {TP.get_nearest_tempo_by_bpm(120)}")
    print(f"\nget_nearest_tempo_by_bpm(300): {TP.get_nearest_tempo_by_bpm(300)}")


def instrument_tests():
    MB = musebox.MuseBox()
    midi = MB.MidiInstruments()
    pp((midi))
    print("\nget_midi_inst_by_category('Piano'): " +
          f"{midi.get_midi_inst_by_category('Piano')}")
    print("\nget_midi_inst_by_category('Silence'): " +
          f"{midi.get_midi_inst_by_category('Silence')}")
    print("\nget_midi_inst_by_name('sax'): " +
          f"{midi.get_midi_inst_by_name('sax')}")
    print("\nget_midi_inst_by_name('HARPSICHORD'): " +
          f"{midi.get_midi_inst_by_name('HARPSICHORD')}")
    print("\nget_midi_inst_by_name('mongo-bongo'): " +
          f"{midi.get_midi_inst_by_name('mongo-bongo')}")
    print("get_midi_inst_by_number(1): " +
          f"{midi.get_midi_inst_by_number(1)}")
    print("get_midi_inst_by_number(1, 1): " +
          f"{midi.get_midi_inst_by_number(1, 1)}")
    print("get_midi_inst_by_number(1, 2): " +
          f"{midi.get_midi_inst_by_number(1, 2)}")
    print("get_midi_inst_by_number(999): " +
          f"{midi.get_midi_inst_by_number(999)}")
    print("get_midi_inst_by_number(27, 32): " +
          f"{midi.get_midi_inst_by_number(27, 32)}")

    midi_drum = MB.MidiDrums()
    pp((midi_drum))
    print("\nmidi_drum.get_midi_drum_by_name('Bass'): " +
          f"{midi_drum.get_midi_drum_by_name('Bass')}")
    print("\nmidi_drum.get_midi_drum_by_name('Open Surdo'): " +
          f"{midi_drum.get_midi_drum_by_name('Open Surdo')}")
    print("\nmidi_drum.get_midi_drum_by_name('BONGO'): " +
          f"{midi_drum.get_midi_drum_by_name('BONGO')}")

    m21instr = MB.Music21Instruments()
    pp((m21instr))
    print("\nm21instr.get_m21_inst_by_name('marimba'): " +
          f"{m21instr.get_m21_inst_by_name('marimba')}")
    print("\nm21instr.get_m21_inst_by_name('PIANO'): " +
          f"{m21instr.get_m21_inst_by_name('PIANO')}")

    # Not using synths, but it is interesting to look at the data.
    # synths = mbins.SynthPlugin()
    #  pp((synths))


def theme_tests():
    MB = musebox.MuseBox()
    SS = MB.Scales()
    degrees = MB.Degrees(SS)
    print(f"degrees.get_degrees('C', 'major'): {degrees.get_degrees('C', 'major')}")
    print("degrees.get_degrees('C', 'major', no_inversions=True): " +
          f"{degrees.get_degrees('C', 'major', no_inversions=True)}")
    print("degrees.get_degrees('D', 'dorian', no_inversions=True): " +
          f"{degrees.get_degrees('D', 'dorian', no_inversions=True)}")

    themes = MB.Themes()
    pp((themes))
    print(f"\nthemes category is 'pop': {themes.get_by_category('pop')}")
    print(f"\nthemes flavor is 'gospel': {themes.get_by_flavor('gospel')}")
    print(f"\nthemes name is 'Cyclical': {themes.get_theme_by_name('Cyclical')}")
    print("\nrender_progression(['Cyclical', 'Plagal Cadence']: " +
          f"{themes.render_progression(['Cyclical', 'Plagal Cadence'])}")


if __name__ == "__main__":
    # object_tests()
    # file_tests()
    # dictionary_tests()
    # instrument_tests()
    theme_tests()
