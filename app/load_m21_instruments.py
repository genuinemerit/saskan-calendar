from music21 import instrument
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Music21Instrument:
    m21_class_name: str
    instrument_name: str
    family: str
    midi_program: Optional[int] = None


def load_music21_instruments() -> List[Music21Instrument]:
    """
    Introspects music21's instrument module to extract all available instrument classes.
    Returns a list of Music21Instrument records.
    """
    instruments = []
    seen_names = set()

    for name, cls in instrument.__dict__.items():
        if not isinstance(cls, type):
            continue
        if not issubclass(cls, instrument.Instrument):
            continue
        if cls is instrument.Instrument:
            continue

        try:
            inst = cls()
            key = (cls.__name__, inst.instrumentName)
            if key in seen_names:
                continue
            seen_names.add(key)

            instruments.append(Music21Instrument(
                m21_class_name=cls.__name__,
                instrument_name=inst.instrumentName,
                family=inst.instrumentFamily,
                midi_program=inst.midiProgram
            ))
        except Exception:
            continue  # Skip if instantiation fails

    return sorted(instruments, key=lambda i: (i.family, i.instrument_name))


if __name__ == "__main__":
    all_instruments = load_music21_instruments()
    for inst in all_instruments:
        print(f"{inst.family:<15} | " +
              f"{inst.instrument_name:<30} | " +
              f"{inst.m21_class_name:<25} | MIDI: {inst.midi_program}")
