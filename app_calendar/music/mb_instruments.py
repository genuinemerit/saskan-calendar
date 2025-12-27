#!python
"""
:module:    mb_instruments.py

:author:    PQ (pq_rfw @ pm.me)

Classes and methods for defining musical instruments, using music21,
standard and extended MIDI definitions, and search for synth plugins.
"""

import music21 as m21
import os
import platform
from copy import copy, deepcopy  # noqa: F401
from dataclasses import dataclass, field
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
from tabulate import tabulate  # noqa: F401
from typing import Union, List, Dict, Optional  # noqa: F401
from shared.utils.file_io import FileMethods

FM = FileMethods()


@dataclass(frozen=True)
class MidiInstrument:
    """
    Represents a General MIDI instrument definition,
    also known as Level 1 MIDI.
    This is the original MIDI standard that defines 128 instruments
    with program numbers 0-127, each with a name and family.
    This is the core MIDI instrument set that most software and hardware
    synths support.
    Level 2 MIDI extends this with bank variations. These are extended
    MIDI definitions that allow for more complex instrument mappings.
    The spec is extended by appending a bank number to the Level 1 program
    number. The original instrument is said to be in bank 0. There may be
    1, 2, 3 or zero additional banks, each with a qualifying name.
    See: https://soundprogramming.net/file-formats/general-midi-instrument-list/
    And: https://soundprogramming.net/file-formats/general-midi-level-2-instrument-list/

    """

    midi: dict = field(
        init=False, default_factory=lambda: MidiInstrument.build_midi_instruments()
    )

    @staticmethod
    def build_midi_instruments():

        instruments = {
            "Piano": {
                1: {
                    0: "Acoustic Grand Piano",
                    1: "Wide Acoustic Grand",
                    2: "Dark Acoustic Grand",
                },
                2: {0: "Bright Acoustic Piano", 1: "Wide Bright Acoustic"},
                3: {0: "Electric Grand Piano", 1: "Wide Electric Grand"},
                4: {0: "Honky-tonk Piano", 1: "Wide Honky-tonk"},
                5: {
                    0: "Rhodes Piano",
                    1: "Detuned Electric Piano 1",
                    2: "Electric Piano 1 Variation",
                    3: "60's Electric Piano",
                },
                6: {
                    0: "Chorused Electric Piano",
                    1: "Detuned Electric Piano 2",
                    2: "Electric Piano 2 Variation",
                    3: "Electric Piano Legend",
                    4: "Electric Piano Phase",
                },
                7: {
                    0: "Harpsichord",
                    1: "Coupled Harpsichord",
                    2: "Wide Harpsichord",
                    3: "Open Harpsichord",
                },
                8: {0: "Clavinet", 1: "Pulse Clavinet"},
            },
            "Chromatic Percussion": {
                9: {0: "Celesta"},
                10: {0: "Glockenspiel"},
                11: {0: "Music Box"},
                12: {0: "Vibraphone", 1: "Wet Vibraphone"},
                13: {0: "Marimba", 1: "Wide Marimba"},
                14: {0: "Xylophone"},
                15: {0: "Tubular Bells", 1: "Church Bells", 2: "Carillon"},
                16: {0: "Dulcimer/Santur"},
            },
            "Organ": {
                17: {
                    0: "Hammond Organ",
                    1: "Detuned Organ 1",
                    2: "60's Organ 1",
                    3: "Organ 4",
                },
                18: {0: "Percussive Organ", 1: "Detuned Organ 2", 2: "Organ 5"},
                19: {0: "Rock Organ"},
                20: {0: "Church Organ 1", 1: "Church Organ 2", 2: "Church Organ 3"},
                21: {0: "Reed Organ", 1: "Puff Organ"},
                22: {0: "French Accordion", 1: "Italian Accordion"},
                23: {0: "Harmonica"},
                24: {0: "Bandoneon"},
            },
            "Guitar": {
                25: {
                    0: "Nylon-String Guitar",
                    1: "Ukelele",
                    2: "Open Nylon Guitar",
                    3: "Nylon Guitar 2",
                },
                26: {
                    0: "Steel-String Guitar",
                    1: "12-String Guitar",
                    2: "Mandolin",
                    3: "Steel + Body",
                },
                27: {0: "Jazz Guitar", 1: "Hawaiian Guitar"},
                28: {
                    0: "Clean Electric Guitar",
                    1: "Chorus Guitar",
                    2: "Mid Tone Guitar",
                },
                29: {
                    0: "Muted Electric Guitar",
                    1: "Funk Guitar",
                    2: "Funk Guitar 2",
                    3: "Jazz Man",
                },
                30: {0: "Overdriven Guitar", 1: "Guitar Pinch"},
                31: {
                    0: "Distortion Guitar",
                    1: "Feedback Guitar",
                    2: "Distortion Rtm Guitar",
                },
                32: {0: "Guitar Harmonics", 1: "Guitar Feedback"},
            },
            "Bass": {
                33: {0: "Acoustic Bass"},
                34: {0: "Fingered Bass", 1: "Finger Slap"},
                35: {0: "Picked Bass"},
                36: {0: "Fretless Bass"},
                37: {0: "Slap Bass 1"},
                38: {0: "Slap Bass 2"},
                39: {
                    0: "Synth Bass 1",
                    1: "Synth Bass 101",
                    2: "Synth Bass 3",
                    3: "Clavi Bass",
                    4: "Hammer",
                },
                40: {
                    0: "Synth Bass 2",
                    1: "Synth Bass 4",
                    2: "Rubber Bass",
                    3: "Attack Pulse",
                },
            },
            "Strings": {
                41: {0: "Violin", 1: "Slow Violin"},
                42: {0: "Viola"},
                43: {0: "Cello"},
                44: {0: "Contrabass"},
                45: {0: "Tremolo Strings"},
                46: {0: "Pizzicato Strings"},
                47: {0: "Harp", 1: "Yang Qin"},
                48: {0: "Timpani"},
            },
            "Orchestral Ensemble": {
                49: {0: "String Ensemble", 1: "Orchestra Strings", 2: "60's Strings"},
                50: {0: "Slow String Ensemble"},
                51: {0: "Synth Strings 1", 1: "Synth Strings 3"},
                52: {0: "Synth Strings 2"},
                53: {0: "Choir Aahs", 1: "Choir Aahs 2"},
                54: {0: "Voice Oohs", 1: "Humming"},
                55: {0: "Synth Voice", 1: "Analog Voice"},
                56: {0: "Orchestra Hit", 1: "Bass Hit", 2: "6th Hit", 3: "Euro Hit"},
            },
            "Brass": {
                57: {0: "Trumpet"},
                58: {0: "Trombone", 1: "Trombone 2", 2: "Bright Trombone"},
                59: {0: "Tuba"},
                60: {0: "Muted Trumpet", 1: "Muted Trumpet 2"},
                61: {0: "French Horn", 1: "French Horn 2"},
                62: {0: "Brass Section", 1: "Brass Section 2"},
                63: {
                    0: "Synth Brass 1",
                    1: "Synth Brass 3",
                    2: "Analog Brass 1",
                    3: "Jump Brass",
                },
                64: {0: "Synth Brass 2", 1: "Synth Brass 4", 2: "Analog Brass 2"},
            },
            "Reed": {
                65: {0: "Soprano Sax"},
                66: {0: "Alto Sax"},
                67: {0: "Tenor Sax"},
                68: {0: "Baritone Sax"},
                69: {0: "Oboe"},
                70: {0: "English Horn"},
                71: {0: "Bassoon"},
                72: {0: "Clarinet"},
            },
            "Wind": {
                73: {0: "Piccolo"},
                74: {0: "Flute"},
                75: {0: "Recorder"},
                76: {0: "Pan Flute"},
                77: {0: "Blown Bottle"},
                78: {0: "Shakuhachi"},
                79: {0: "Whistle"},
                80: {0: "Ocarina"},
            },
            "Synth Lead": {
                81: {0: "Square Lead", 1: "Square Wave", 2: "Sine Wave"},
                82: {
                    0: "Saw Lead",
                    1: "Saw Wave",
                    2: "Doctor Solo",
                    3: "Natural Lead",
                    4: "Sequenced Saw",
                },
                83: {0: "Synth Calliope"},
                84: {0: "Chiffer Lead"},
                85: {0: "Charang", 1: "Wire Lead"},
                86: {0: "Solo Synth Vox"},
                87: {0: "5th Saw Wave"},
                88: {0: "Bass & Lead", 1: "Delayed Lead"},
            },
            "Synth Pad": {
                89: {0: "Fantasia Pad"},
                90: {0: "Warm Pad", 1: "Sine Pad"},
                91: {0: "Polysynth Pad"},
                92: {0: "Space Voice Pad", 1: "Itopia"},
                93: {0: "Bowed Glass Pad"},
                94: {0: "Metal Pad"},
                95: {0: "Halo Pad"},
                96: {0: "Sweep Pad"},
            },
            "Synth Effects": {
                97: {0: "Ice Rain"},
                98: {0: "Soundtrack"},
                99: {0: "Crystal", 1: "Synth Mallet"},
                100: {0: "Atmosphere"},
                101: {0: "Brightness"},
                102: {0: "Goblin"},
                103: {0: "Echo Drops", 1: "Echo Bell", 2: "Echo Pan"},
                104: {0: "Star Theme"},
            },
            "Ethnic": {
                105: {0: "Sitar", 1: "Sitar 2"},
                106: {0: "Banjo"},
                107: {0: "Shamisen"},
                108: {0: "Koto", 1: "Taisho Koto"},
                109: {0: "Kalimba"},
                110: {0: "Bagpipe"},
                111: {0: "Fiddle"},
                112: {0: "Shanai"},
            },
            "Percussive": {
                113: {0: "Tinkle Bell"},
                114: {0: "Agogo"},
                115: {0: "Steel Drums"},
                116: {0: "Woodblock", 1: "Castanets"},
                117: {0: "Taiko Drum", 1: "Concert Bass Drum"},
                118: {0: "Melodic Tom 1", 1: "Melodic Tom 2"},
                119: {0: "Synth Drum", 1: "808 Tom", 2: "Electric Percussion"},
                120: {0: "Reverse Cymbal"},
            },
            "Sound Effects": {
                121: {0: "Guitar Fret Noise", 1: "Guitar Cut Noise", 2: "String Slap"},
                122: {0: "Breath Noise", 1: "Flute Key Click"},
                123: {
                    0: "Seashore",
                    1: "Rain",
                    2: "Thunder",
                    3: "Wind",
                    4: "Stream",
                    5: "Bubble",
                },
                124: {0: "Bird Tweet", 1: "Dog", 2: "Horse Gallop", 3: "Bird 2"},
                125: {
                    0: "Telephone Ringing",
                    1: "Telephone Off Hook",
                    2: "Door Creaking",
                    3: "Door Closing",
                    4: "Scratch",
                    5: "Wind Chimes",
                },
                126: {
                    0: "Helicopter",
                    1: "Car Engine",
                    2: "Car Stop",
                    3: "Car Pass",
                    4: "Car Crash",
                    5: "Siren",
                    6: "Train",
                    7: "Jetplane",
                    8: "Starship",
                    9: "Burst Noise",
                },
                127: {
                    0: "Applause",
                    1: "Laughing",
                    2: "Screaming",
                    3: "Punch",
                    4: "Heart Beat",
                    5: "Footsteps",
                },
                128: {0: "Gun Shot", 1: "Machine Gun", 2: "Lasergun", 3: "Explosion"},
            },
        }
        return instruments

    def get_midi_inst_by_category(self, category: str) -> Dict[str, Dict]:
        """
        Return all MIDI instruments matching a specific category.
        """
        return {
            k: v for k, v in self.midi.items() if k.lower() == category.lower().strip()
        }

    def get_midi_inst_by_name(self, name: str) -> List[Dict[str, Dict]]:
        """
        Return all MIDI instruments matching a specific name.
        """
        inst = []
        for i, d in self.midi.items():
            for pn, dd in d.items():
                for bn, n in dd.items():
                    if name.lower().strip() in n.lower():
                        inst.append({i: {pn: {bn: n}}})
        return inst

    def get_midi_inst_by_number(
        self, program_number: int, bank_number: int = 0
    ) -> Dict[str, Dict]:
        """
        Return a MIDI instrument by its program number.
        And optionally, by bank number, which defaults to zero (level 1 MIDI).
        """
        for category, instruments in self.midi.items():
            if program_number in instruments:
                if bank_number in instruments[program_number]:
                    return {
                        category: {
                            program_number: {
                                bank_number: instruments[program_number][bank_number]
                            }
                        }
                    }
        return {}


@dataclass(frozen=True)
class MidiDrum:
    """
    MIDI drum notes are distinct from standard MIDI instruments.
    They are defined as a number and name pair.
    See: https://www.midi.org/specifications/item/gm-level-1-sound-set
    """

    midi_drum: dict = field(
        init=False, default_factory=lambda: MidiDrum.build_midi_drum_notes()
    )

    def build_midi_drum_notes():
        """
        Build a dictionary of MIDI drum notes.
        These are the standard MIDI drum notes defined in General MIDI Level 1 and 2.
        """
        drum_notes: dict = {}
        drum_notes[27] = "High Q"
        drum_notes[28] = "Slap"
        drum_notes[29] = "Scratch Push"
        drum_notes[30] = "Scratch Pull"
        drum_notes[31] = "Sticks"
        drum_notes[32] = "Square Click"
        drum_notes[33] = "Metronome Click"
        drum_notes[34] = "Metronome Bell"
        drum_notes[35] = "Bass Drum 2"
        drum_notes[36] = "Bass Drum 1"
        drum_notes[37] = "Side Stick"
        drum_notes[38] = "Snare Drum 1"
        drum_notes[39] = "Hand Clap"
        drum_notes[40] = "Snare Drum 2"
        drum_notes[41] = "Low Tom 2"
        drum_notes[42] = "Closed Hi-hat"
        drum_notes[43] = "Low Tom 1"
        drum_notes[44] = "Pedal Hi-hat"
        drum_notes[45] = "Mid Tom 2"
        drum_notes[46] = "Open Hi-hat"
        drum_notes[47] = "Mid Tom 1"
        drum_notes[48] = "High Tom 2"
        drum_notes[49] = "Crash Cymbal 1"
        drum_notes[50] = "High Tom 1"
        drum_notes[51] = "Ride Cymbal 1"
        drum_notes[52] = "Chinese Cymbal"
        drum_notes[53] = "Ride Bell"
        drum_notes[54] = "Tambourine"
        drum_notes[55] = "Splash Cymbal"
        drum_notes[56] = "Cowbell"
        drum_notes[57] = "Crash Cymbal 2"
        drum_notes[58] = "Vibra Slap"
        drum_notes[59] = "Ride Cymbal 2"
        drum_notes[60] = "High Bongo"
        drum_notes[61] = "Low Bongo"
        drum_notes[62] = "Mute High Conga"
        drum_notes[63] = "Open High Conga"
        drum_notes[64] = "Low Conga"
        drum_notes[65] = "High Timbale"
        drum_notes[66] = "Low Timbale"
        drum_notes[67] = "High Agogo"
        drum_notes[68] = "Low Agogo"
        drum_notes[69] = "Cabasa"
        drum_notes[70] = "Maracas"
        drum_notes[71] = "Short Whistle"
        drum_notes[72] = "Long Whistle"
        drum_notes[73] = "Short Guiro"
        drum_notes[74] = "Long Guiro"
        drum_notes[75] = "Claves"
        drum_notes[76] = "High Wood Block"
        drum_notes[77] = "Low Wood Block"
        drum_notes[78] = "Mute Cuica"
        drum_notes[79] = "Open Cuica"
        drum_notes[80] = "Mute Triangle"
        drum_notes[81] = "Open Triangle"
        drum_notes[82] = "Shaker"
        drum_notes[83] = "Jingle Bell"
        drum_notes[84] = "Belltree"
        drum_notes[85] = "Castanets"
        drum_notes[86] = "Mute Surdo"
        drum_notes[87] = "Open Surdo"
        return drum_notes

    def get_midi_drum_by_name(self, name: str) -> Optional[Dict[str, object]]:
        """
        Return a MIDI drum note matching a specific name.
        """
        return {
            k: v for k, v in self.midi_drum.items() if name.lower().strip() in v.lower()
        }


@dataclass(frozen=True)
class Music21Instrument:
    """
    music21 provides a module: `music21.instrument`, which includes:
    * Class-based instrument definitions (e.g., `Violin()`, `Piano()`, `ElectricGuitar()`)
    * Support for setting instrument metadata on streams
        (like part names, midi program numbers, transpositions)
    """

    m21_inst: dict = field(
        init=False, default_factory=lambda: Music21Instrument.build_m21_instruments()
    )

    @staticmethod
    def build_m21_instruments():
        """
        Build a dictionary of music21 instruments.
        This will scan the music21.instrument module and create a dictionary
        of instrument class names and their corresponding metadata.
        """
        instruments: dict = {}
        for name, cls in m21.instrument.__dict__.items():
            if not isinstance(cls, type):
                continue
            if not issubclass(cls, m21.instrument.Instrument):
                continue
            if cls is m21.instrument.Instrument:
                continue
            inst = cls()  # Create an instance of the instrument class
            # pp((dir(inst)))
            instruments[cls.__name__] = {
                "name": inst.instrumentName,
                "hi_note": inst.highestNote,
                "lo_note": inst.lowestNote,
                "midi_program": inst.midiProgram,
            }
        return instruments

    def get_m21_inst_by_name(self, name: str) -> Optional[Dict[str, object]]:
        """
        Return a MIDI instrument matching a specific name.
        """
        return {
            k: v
            for k, v in self.m21_inst.items()
            if name.lower().strip() in v["name"].lower()
        }


@dataclass
class SynthPlugin:
    """
    Represents a software instrument plugin available on the system.
    Not sure this is really useful in MuseBox -- probably not -- but
    it is interesting!
    """

    synths: dict = field(
        init=False, default_factory=lambda: SynthPlugin.build_synth_plugins()
    )

    @staticmethod
    def get_base_dirs() -> List[str]:
        """
        Returns a list of standard directories where synth plugins are typically installed.
        This is platform-dependent.
        """
        system = platform.system()
        if system == "Linux":
            return [
                os.path.expanduser("~/.vst"),
                os.path.expanduser("~/.vst3"),
                os.path.expanduser("~/.lv2"),
                "/usr/lib/vst",
                "/usr/local/lib/vst",
                "/usr/lib/vst3",
                "/usr/local/lib/vst3",
                "/usr/lib/lv2",
                "/usr/local/lib/lv2",
            ]
        elif system == "Darwin":  # macOS
            return [
                "/Library/Audio/Plug-Ins/VST",
                "/Library/Audio/Plug-Ins/VST3",
                "/Library/Audio/Plug-Ins/Components",  # AU
                os.path.expanduser("~/Library/Audio/Plug-Ins/VST"),
                os.path.expanduser("~/Library/Audio/Plug-Ins/VST3"),
                os.path.expanduser("~/Library/Audio/Plug-Ins/Components"),
            ]
        elif system == "Windows":
            return [
                os.path.expandvars("%PROGRAMFILES%\\VSTPlugins"),
                os.path.expandvars("%PROGRAMFILES%\\Steinberg\\VSTPlugins"),
                os.path.expandvars("%PROGRAMFILES%\\Common Files\\VST2"),
                os.path.expandvars("%PROGRAMFILES%\\Common Files\\VST3"),
            ]
        else:
            return []

    def build_synth_plugins():
        """
        Scans standard plugin directories for synth plugins.
        """
        base_dirs = SynthPlugin.get_base_dirs()
        synths: dict = {}
        seen_paths = set()

        for base_dir in base_dirs:
            if not os.path.isdir(base_dir):
                continue
            for root, _, files in os.walk(base_dir):
                for f in files:
                    if f.endswith((".so", ".dll", ".dylib")) or any(
                        base_dir.endswith(tag) for tag in ["lv2", "Components"]
                    ):
                        full_path = os.path.join(root, f)
                        if full_path in seen_paths:
                            continue
                        seen_paths.add(full_path)
                        if "/vst3" in root or "\\VST3" in root:
                            plugin_type = "VST3"
                        elif "/vst" in root or "\\VST" in root:
                            plugin_type = "VST2"
                        elif "lv2" in root:
                            plugin_type = "LV2"
                        elif "Components" in root:
                            plugin_type = "AU"
                        else:
                            plugin_type = "Unknown"
                        synths[os.path.splitext(f)[0]] = {
                            "path": full_path,
                            "type": plugin_type,
                        }

        return synths
