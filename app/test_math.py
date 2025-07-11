# -*- coding: utf-8 -*-

from pprint import pprint as pp
import core as cal
import numpy as np


def smooth_decay_split(V, D):
    """
    Split a value V into D smoothly transitioning values using cosine decay.
    The result is ordered in descending magnitude (toward zero), and the values
    are rounded to two decimal places. The total sum is compensated to exactly V.

    Parameters:
        V (float): Total value to distribute (positive or negative)
        D (int): Number of values (must be between 3 and 21)

    Returns:
        list of float: D values summing exactly to V, ordered by magnitude
    """
    if D < 3 or D > 21:
        raise ValueError("D must be between 3 and 21")

    sign = 1 if V >= 0 else -1
    abs_V = abs(V)

    # Create decreasing cosine weights and normalize
    weights = np.cos(np.linspace(0, np.pi / 2, D))
    weights /= weights.sum()
    raw_values = weights * abs_V

    # Round each value and compensate the first element
    rounded = [round(val, 2) for val in raw_values]
    diff = round(abs_V - sum(rounded), 2)
    rounded[0] += diff  # adjust the largest value

    # Apply sign to all values and return
    values = [sign * val for val in rounded]
    return values


def compute_phase(p_direction: str,
                  p_duration: int,
                  p_magnitude: int) -> None:
    """
    @param p_direction: str - Direction of the chaos event, either 'B' or 'F'.
    @param p_duration: int - Duration of the chaos event in days.
    @param p_magnitude: int - Magnitude of the chaos event.
    if offset <= 0.03 or offset >= 0.97:
        name = "Grin Without Cause, Laughter in the Dust"
        notes = "A toothy curve of craters, askew. Surprising luck. Unwanted guests."
        omen = "Beware striking deals; they favor the fool."
    elif offset > 0.03 and offset < 0.23:
        name = "The Black Wink is Not an Eye"
        notes = "A darkened divot shaped like a closed eye. Speak softly."
        omen = "Secrets withheld will twist in the throat."
    elif offset >= 0.23 and offset <= 0.27:
        name = "The Tilted Mask, Half Jest, Half Spite"
        notes = "Shadows seem misaligned with the expected arc. Servants rise, masters fall."
        omen = "A good time for gambling or revolution."
    elif offset > 0.27 and offset < 0.47:
        name = "The Crooked Maw of the Devourer of Patterns"
        notes = "Jagged valley, illusion of a scream. Interruptions, madness."
        omen = "Lose something; find something better or worse."
    elif offset >= 0.47 and offset <= 0.53:
        name = "Vein of Fire, a Fissure in the Ice"
        notes = "Rare glowing vein. Upheaval, literal and social."
        omen = "Watch the mountain roots; some will walk."
    elif offset > 0.53 and offset < 0.73:
        name = "The Jester of Perpetual Challenge"
        notes = "Crescent shadow bends like an arched brow. Days of duels, dares, and dancing."
        omen = "Speak plainly or be tricked."
    elif offset >= 0.73 and offset <= 0.77:
        name = "The Bleeding Curve, The Smile That Wounds"
        notes = "Faint reddish tint on the terminator line. Bloodlettings or fevers."
        omen = "A time of confession and consequence."
    elif offset > 0.77 and offset < 0.97:
        name = "The Shattered Wheel, Never Whole"
        notes = "Craters misaligned as if part of a broken circle. Chaotic shifts."
        omen = "Nothing holds and no pact binds when Kanka resets her spin."
    return (name, notes, omen)
    @return: None - Prints the adjusted moon phase offsets for the chaos event.
    """
    astro_date = 40  # Date of the chaos event
    duration = p_duration
    # Magnitude and direction of the chaos event
    magnitude = round((1 / p_magnitude), 2)
    magnitude = magnitude * -1 if p_direction == "B" else magnitude
    decay = smooth_decay_split(magnitude, duration)
    print("duration", duration,
          "| magnitude", magnitude,
          "| decay", decay)
    offsets: dict = {}
    for astro in range(astro_date, astro_date + duration):
        moon = cal.get_moon_phases(astro)['Kanka']
        offsets[astro] =\
            {"offset": moon['phase_offset'],
             "period": round(float(moon["rotation_period"]), 2),
             "phase": moon['phase'],
             "faces": moon['face_name'] +
             " | " + moon['face_notes'] + " | " + moon['face_omen']}
    for day, (astro, data) in enumerate(offsets.items()):
        adj_offset = \
            round(offsets[astro]['offset'] + decay[day], 2)
        adj_offset = 1.0 + adj_offset if adj_offset < 0.0 else \
            adj_offset
        # N.B. -- If the offset is not changed, then we do not
        # need to write data to the chaos record.
        if adj_offset != data['offset']:
            offsets[astro]['offset'] = adj_offset
            offsets[astro]['phase'] =\
                "Strange " + cal.get_revolution_data(astro, data['period'])[3]
            faces = cal.get_kanka_faces(adj_offset)
            faces = " | ".join(faces)
            faces = faces.replace("Grin", "Grimace").replace("Wink", "Stare")
            faces = faces.replace("Eye", "Edge").replace("Laughter", "Tears")
            faces = faces.replace("Jest", "Cry").replace("Spite", "Spike")
            faces = faces.replace("Crooked", "Closed").replace("Patterns", "Stars")
            faces = faces.replace("Fire", "Chasm").replace("Fissure", "Flame")
            faces = faces.replace("Ice", "Opening").replace("Tilted", "Broken")
            faces = faces.replace("Jester", "Demon").replace("Challenge", "Change")
            faces = faces.replace("Bleeding", "Smashed").replace("Smile", "Frown")
            faces = faces.replace("Wheel", "Bones").replace("Cause", "Meaning")
            offsets[astro]['face'] = faces
    pp((offsets))


if __name__ == "__main__":
    for dirt, dur, mag in (("B", 9, 2),
                           ("F", 11, 3),
                           ("B", 13, 4),
                           ("F", 21, 6)):
        compute_phase(dirt, dur, mag)
