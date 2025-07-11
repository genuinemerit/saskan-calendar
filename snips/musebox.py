@dataclass(frozen=True)
class NoteSet:
    """
    Defines standard note durations, rests, dotted values, and tuplets.

    Durations are based on music21's quarterLength system:
    - quarter note = 1.0
    - half note = 2.0
    - eighth note = 0.5
    - etc.

    Tuplets are defined as:
        Tuplet(actual, normal)
    Where:
    - `actual` = number of notes to play
    - `normal` = number of notes you'd normally expect in the same space

    Examples:
    - Tuplet(3, 2): 3 notes in the time of 2 — a standard triplet
    - Tuplet(5, 2): 5 notes in the time of 2 — a quintuplet
    """
    note: dict = field(init=False, default_factory=lambda: NoteSet.build_notes())

    @staticmethod
    def build_notes():
        note = {ntype: {} for ntype in
                ('plain', 'rest', 'dotted', 'triplet', 'quintuplet', 'septuplet')}

        base_durations = {
            'breve': 8.0, 'whole': 4.0, 'half': 2.0,
            'quarter': 1.0, 'eighth': 0.5, '16th': 0.25,
            '32nd': 0.125, '64th': 0.0625
        }

        for name, dur_val in base_durations.items():
            dur_plain = m21.duration.Duration(dur_val)
            note['plain'][name] = dur_plain
            note['rest'][name] = m21.note.Rest(quarterLength=dur_val)
            note['dotted'][name] = m21.duration.Duration(dur_val * 1.5)

            # Create tuplets as separate Duration objects
            for kind, ratio in {
                'triplet': (3, 2),
                'quintuplet': (5, 2),
                'septuplet': (7, 2)
            }.items():
                d = m21.duration.Duration(dur_val)
                d.appendTuplet(m21.duration.Tuplet(*ratio))
                note[kind][name] = d

        return note

    def display_notes(self):
        """
        Display each category of note durations in separate tables.
        """
        output = ""
        for category, notes in self.note.items():
            headers = ['Note Name', 'Duration (quarterLength)']
            rows = []
            for name, dur in notes.items():
                ql = dur.quarterLength if hasattr(dur, 'quarterLength') else '?'
                rows.append([name, ql])
            output += f"\n{category.upper()}:\n"
            output += tabulate(rows, headers=headers, tablefmt='grid')
            output += "\n"
        return output

