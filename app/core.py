"""
Saskan_Calendar 0.1.0.a - Core Simulation Engine
Includes: Calendar systems, moon phases, wanderers, star context, date translator
This is a simplified but valid core to bootstrap the prototype package.

The Saskan Calendars are fictional calendar systems for the world of Saskantinon.
It is designed to be used in a variety of applications, including games,
  simulations, and storytelling.
The core solar cycle is a 365.25-day year of the planet Gavor around the star Fatune.
There are eight moons orbiting Gavor, each with its own cycle.
A variety of lunar and solar calendars are derived from these cycles.
In this world we say "turn" rather than "year".

Dev notes:
- Add lunar size, distance, and other properties to the moon phases.
- Consider the starting point of the lunar positions. Where were they
    at the start of the Rosetta epoch? What is currently implied?
- Include in-line comments for each function and class.
- Add type hints for all functions and classes.
- Add docstrings for all functions and classes.
- Add error handling for invalid inputs.
- Add unit tests for all functions and classes.
- Add a command-line interface for the package.
- Replace ambiguous names with more descriptive ones.
- Record a database of meaningful dates in the Saskan Lore.
  - Start with JSON. Later, consider a database.
"""

import json
import math
import numpy as np
import random
import method_files as mf  # noqa F401

from typing import Union  # , Dict
from pprint import pprint as pp     # noqa F401

FM = mf.FileMethods()

"""
The Astronomical Solar calendar is a true solar calendar, one revolution of Gavor
around Fatune, the sun. Its epoch start corresponds to the arrival of the Agency
following a Cataclysm, which occurred about 500 turns prior to their arrival.
The astro epoch start occurs about 6000 turns prior to the game start, about
1000 years prior to the start of the Lunar A and B calendars, about 1000 years
prior to the start of the Terpin solar calendar, and about 2000 years prior
to the start of the Fatunik solar calendar.

The Solar calendar has months, seasons, turns (years), days and pulses (seconds).
By an astounding coincidence, ;-) there is a  galactic pulsar which has a period of
exactly one Gavoran second, and a Gavoran day is exactly 86400 seconds, just like on
Earth. This makes the Astro Solar calendar convenient for timekeeping.

Seasons are also computed based on the true solar year, and they are defined based
on a northern hemisphere perspective:  Greening (Spring), Blazing (Summer),
Withering (Fall), and Stillness (Winter).

Day 1 of the Astro Solar calendar is the first day of the first turn (year), and is
counted as 1 (not zero) The first turn (year) is the first full turn of Gavor
around Fatune and is likewise counted as 1 (not zero).

The initial pulse of the Astro Solar epoch is set to 0 and is assumed to have occured
at midnight at an arbitrarily-chosen place in the Saskan Lands. If counting pulses
within a day, then count of 0 is the first pulse of the day, and the count of 86399 is
the last pulse of the day, with pulses 80400 coinciding with the midnight or 0 pulse of
the next day.

Some calculations need to be in relationship to the Astro Solar epoch start. In that
case, we refer to Astro Days and Astro Pulses, that is, an ever-increasing count of
days and pulses since the Astro epoch start.

Other calculations are done in reference to the true solar year, which is how we
determine seasons and some alignments of wanderers (fixed stars, otther planets, etc.).
In those cases, we refer to Solar Days and Solar Pulses, that is, a cyclic count of
days and pulses within the current solar year, which is 365.2422 days, or 31,556,926
pulses.

Solar months are used only to calculate the visible houses of the equinox. The study
of the movement of the stars is a controversial topic in the Saskan Lands; there is
no official calendar of the stars, but various cults and groups do study the stars
and keep track of the visible houses of the equinox, which is to say the constellations
visibble in the sky at different times of the year from the Saskan Lands. The Houses
are defined as a set of 12 contellations, tied precisely to the Solar months. In this
sense the "Houses" are a kind of calendar. In fact, a very precise one that does not
require adjustments for leap years. But it is tracked only by observation, not (yet)
by calculation.
"""
ASTRO_EPOCH_PULSE = 0
ASTRO_EPOCH_DAY = 1
DAYS_PER_SOLAR_TURN = 365.2422
PULSES_PER_SOLAR_DAY = 86400
DAYS_PER_SOLAR_MONTH = DAYS_PER_SOLAR_TURN / 12
PULSES_PER_SOLAR_MONTH = math.floor(PULSES_PER_SOLAR_DAY * DAYS_PER_SOLAR_MONTH)
PULSES_PER_SOLAR_TURN = math.floor(DAYS_PER_SOLAR_TURN * PULSES_PER_SOLAR_DAY)
"""
two solar calendars are used in the Saskan Lands: the Terpin and the Fatunik.

The Terpin Calendar, used by the Terpin people and their followers in the southern
provinces, takes a very long view on how to adjust for the fact that a true solar
year is float, not an integer.  The Terpin turn (year) is 365 days long. Then every
132 years, a 32-day Festival Season is inserted to bring the calendar back in synch.
Except every 35th Festival Cycle (every 4,620 years), the Festival lasts only 31 days.
Although its adjustments are very long-term, it is easy to use and over long periods,
always adjusts back to the true solar year.

The Terpin Calendar uses 12 months of 30 days each, with a 5-day Festival Season in
non-leap years. Every 132 years, 32 days are added to the Festival Season, making it
37 days long, except every 35th Festival Cycle, when only 31 days are added to the
Festival Season, making it 36 days long. The Terpin Calendar starts in the Spring,
with the Festival Season being the first month of the year. Ideally, the first day
of the first month of the first Terpin year, about 1,000 turns after Year 1 of the
Astro Solar Calendar, is a day with maximum number of full moons (6 ?).

The Fatunik Calendar, used by the Fatunik and Rider people and their followers in
the northern provinces, is a more complex calendar that uses a leap day every 4
years, except every 100 years, when the leap day is skipped, and every 400 years,
when the leap day is added back. The Fatunik turn (year) is 365 days long, except
every 4th year, when it is 366 days long, excepting every 100th year, when it is
365 days long, and every 400th year, when it is 366 days long. The Fatunik Calendar
uses 12 months of 30 days each, with a 5-day Festival Season in non-leap years and
a 6-day Festival Season in leap years. The Festival Season is the first month of
the year, and it starts on the first day of the Summer Solstice, or close to it.
Ideally, the first day of the first month of the first Fatunik year, about 2,742 turns
after Year 1 of the Astro Solar Calendar, begins on a day with maxinum number of
new moons (6 ?).
"""
FATUNIK_EPOCH_DAY = 365434      # current estimate
"""
There are 8 moons. See moons_data.json for details.

Twelve distinct lunar calendars are in use the Saskan Lands. One for each of the 8 moons,
a unified Terpin lunar calendar that uses an average of all the moons's cycles. And
three lunar calendars that track lunar cycles which coincide with each other, in other
words, have full moons on the same day relatively frequently.

All lunar calendars are based on approximately the same Epoch start as the Terpin
Solar calendar, which is about 1,000 turns after the Astro Solar epoch start. But each
one has its own lunar epoch start, which is based on the first full moon, or full moon
conjunction, after the Spring equinox, which is the first day of the Terpin Solar calendar.
"""
LUNAR_EPOCH_DAY = 182718      # current estimate
LUNAR_MONTH_AVG_DAYS = 28     # this is rounded. needs to be adjusted


def ordinal(n: int) -> str:
    """
    @param n: The number to convert to an ordinal word.
    @return: str - the ordinal word or number with "th" suffix.
    """
    ordinals = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    return ordinals[n - 1] if 1 <= n <= 6 else f"{n}th"


def sanitize_pulse_count_epoch(p_seconds: int) -> int:
    """
    @p_seconds: The pulse count is a positive integer.
    Galactic pulse count is equal to a second in a solar day, even though
    Saskans don't use seconds.
    @return: int - the sanitized pulse count, clamped to 1 to n.
    """
    pulse = 1 if p_seconds < 1 else p_seconds
    pulse = int(round(pulse, 0))  # Ensure it's an integer
    return pulse


def sanitize_pulse_count_day(p_seconds: int) -> int:
    """
    @p_seconds: The pulse count is a positive integer.
    Galactic pulse count is equal to a second in a solar day, even though
    Saskans don't use seconds.
    @return: int - the sanitized pulse count, clamped to 1 to 86400.
    """
    pulse = max(1, min(p_seconds, PULSES_PER_SOLAR_DAY))
    pulse = int(round(pulse, 0))  # Ensure it's an integer
    return pulse


def sanitize_astro_day(p_day: float) -> float:
    """
    @p_day: The astro day param is a float.
    An astro day is a day in the Astronomical calendar, which is based on
    Gavor's true orbit around Fatune, the sun. It increases infinitely,
    by one, every Gavoran rotation (solar day).
    Clamp astro day to valid range not < 1.0 and round to 4 decimals.
    @return: float - the sanitized astro day,  clamped to valid range
        not < 1.0 and rounded to 4 decimals.
    """
    astro_day = round(p_day, 4)
    astro_day = float(max(1.0, astro_day))
    return astro_day


def sanitize_solar_turn(p_turn) -> int:
    """
    @param p_turn: The solar turn param is a positive integer.
    A solar turn is a year in the Astronomical calendar, which is based on
    Gavor's true orbit around Fatune, the sun.
    @return: int - the sanitized solar turn, clamped to valid range not < 1.
    """
    solar_turn = int(round(max(1, p_turn)))
    return solar_turn


def sanitize_solar_day(p_day: float) -> float:
    """
    @param p_day: The solar day param is a float.
    A true solar day is a day in a solar year based on Gavor's true orbit
    around Fatune, the sun. Unlike the astro day, which increases infinitely,
    the solar day is reset to 1.0 at the start of each solar year.
    This function does NOT convert astro days to solar days,
    it only sanitizes the input solar day value.
    @return: float - the sanitized solar day, clamped to valid range and rounded.
    """
    solar_day = round(p_day, 4)
    solar_day = float(max(1.0, min(solar_day, 365.2422)))
    return solar_day


def get_astro_day_from_pulse(p_pulse: int) -> float:
    """
    @param p_pulse: Integer number of pulses since astro epoch start.
    For the current scenario, the astro epoch start is at pulse 0.
    @return: The sanitized astro day. Number of astro days since
        astronomical epoch start.
    """
    pulses_since_epoch = abs(p_pulse) - ASTRO_EPOCH_PULSE
    astro_day = sanitize_astro_day(pulses_since_epoch / PULSES_PER_SOLAR_DAY)
    return astro_day


def get_pulses_into_solar_day(p_astro_day: float) -> int:
    """
    @param p_astro_day: float in form D.DDDD.
    Based on the fractional portion, compute integer number of galactic pulses
    (seconds) that have elapsed since start (midnight) of that day.  In other
    words, determine what time it is as a number of elapsed seconds since midnight.
    Each solar day has 86,400 pulses.
    Note that this function ignores the astro day integer portion,
    @return: integer number of galactic pulses (seconds) elapsed since start of the day.
    """
    astro_day = sanitize_astro_day(p_astro_day)
    fractional = astro_day % 1  # Get decimal portion
    pulses_into_day = int(round(fractional * PULSES_PER_SOLAR_DAY))
    return pulses_into_day


def get_pulses_to_astro_day(p_astro_day: float) -> int:
    """
    @param astro_day:  float number of an astro day.
    In this lore, a galactic pulse is exactly one true solar second, per
        our earthling definition of a second.
    @return: The integer count of galactic pulses since astro epoch start
        (which is at pulse 0, astro day 1.0) until the start (midnight) of the
        specified astro day.
    """
    astro_day = sanitize_astro_day(p_astro_day)
    fractional = astro_day % 1  # Get decimal portion
    pulses_to_day = (ASTRO_EPOCH_PULSE +
                     int(round((astro_day * PULSES_PER_SOLAR_DAY) +
                               (fractional * PULSES_PER_SOLAR_DAY) -
                               PULSES_PER_SOLAR_DAY)))
    return pulses_to_day


def get_solar_day_from_pulse(p_pulse: int) -> float:
    """
    @param pulse_count: Integer pulses since astro epoch start.
    Given the total number of galactic pulses since the astro epoch began,
    return the current solar day, a float between 1.0000 and 365.2422.
    Note that this function does NOT provide the astro turn (year).
    @return: Solar day float, sanitized.
    """
    pulse = sanitize_pulse_count_epoch(p_pulse)
    PULSES_PER_TURN = PULSES_PER_SOLAR_DAY * DAYS_PER_SOLAR_TURN
    pulses_into_turn = pulse % PULSES_PER_TURN
    solar_day = pulses_into_turn / PULSES_PER_SOLAR_DAY + 1.0
    solar_day = sanitize_solar_day(solar_day)
    return solar_day


def get_solar_month(p_solar_day: float) -> int:
    """
    @param p_solar_day: float in range 1.0 to 365.2422
    Given a solar day (1.0 to 365.2422), return the solar month float,
     from 1.0 to 12.9999. Each month is of equal length: 365.2422 / 12 ≈ 30.43685 days.
    The solar month is used to define the visible houses of the equinox.
    Its decimal portion indicates how far into the month we are, or in terms of
    the precision of the Houses, a more precise indicator of where to see them in
    the sky, and which ones are rising or setting at that time of month.
    @return: float = solar month, 1.0 to 12.9999
    """
    solar_day = sanitize_solar_day(p_solar_day)
    solar_month = round(((solar_day - 1) / DAYS_PER_SOLAR_MONTH) + 1, 2)
    return solar_month


def get_astro_turn(p_astro_day: float) -> int:
    """
    @param p_astro_day: float number of an astro day.
    An astro day increments infinitely rather than being reset at 365.2422 the
    end of a solar year. It is a count of days (plantary roations) since
    astro epoch start. Note that this function provides an integer turn (year).
    :return: Integer solar turn (year) number, starting from 1.
    """
    astro_day = sanitize_astro_day(p_astro_day)
    astro_turn = int(round(astro_day // DAYS_PER_SOLAR_TURN)) + 1
    astro_turn = sanitize_solar_turn(astro_turn)
    return astro_turn


def get_solar_season(p_solar_day: float) -> dict:
    """
    @param p_solar_day: float number of a day in a solar year
    Return name of the solar season and, if applicable special event.
    Events are the first day of a season (equinox or solstice) and
        the mid-season dates.
    A seasonal event is computed as occuring within a half-day event window
      of the precise astronomical event.
    @return: dict {"solar_season": str, "solar_event": str}
    """
    solar_day = sanitize_solar_day(p_solar_day)
    season_length = DAYS_PER_SOLAR_TURN / 4  # ≈ 91.31055
    event_window = 0.45  # ± quarter day = ~20-hour window
    # Adjusted seasonal boundaries
    still_start = 1.0
    green_start = still_start + season_length
    blaze_start = green_start + season_length
    wither_start = blaze_start + season_length
    end_of_year = still_start + DAYS_PER_SOLAR_TURN
    seasons = {
        "Stillness": {
            "range": (still_start, green_start),
            "events": [
                ("Darkening", math.ceil(still_start)),
                ("Deep Still", round(still_start + season_length / 2, 4)),
            ]
        },
        "Greening": {
            "range": (green_start, blaze_start),
            "events": [
                ("Green Day", math.ceil(green_start)),
                ("Leafcrest", round(green_start + season_length / 2, 4)),
            ]
        },
        "Blazing": {
            "range": (blaze_start, wither_start),
            "events": [
                ("Fatune Day", math.ceil(blaze_start)),
                ("High Blaze", round(blaze_start + season_length / 2, 4)),
            ]
        },
        "Withering": {
            "range": (wither_start, end_of_year),
            "events": [
                ("Harvest Festival", math.ceil(wither_start)),
                ("Mid-Wane", round(wither_start + season_length / 2, 4)),
            ]
        }
    }
    season_dict = {"solar_season": "", "solar_event": ""}
    for season_name, info in seasons.items():
        start, end = info["range"]
        if start <= solar_day < end:
            season_dict["solar_season"] = season_name
            for event_name, event_day in info["events"]:
                if abs(solar_day - event_day) <= event_window:
                    season_dict["solar_event"] = event_name
                    break
            break
    return season_dict


#  Pick up refactoring here...

def get_astro_events(p_astro_day: float) -> list:
    """
    @param p_astro_day: float number of an astronomical day
    Return a list of astronomical events for the given day.
    The events are defined in astro_events.json file.
    The events are based on the true solar progression over epoch and are not
    affected by moon phases.
    @return: list of dicts with event names.
    """
    events = []
    astro_day = sanitize_astro_day(p_astro_day)
    astro_day = str(int(round(astro_day, 0)))
    astro_events = FM.get_json_file("./astro_events.json")
    if astro_day in list(astro_events.keys()):
        events = astro_events[astro_day]
    return events


def get_moon_phases(p_astro_day: float) -> dict:
    """
    @param solar_day: float number of an astronomical day since epoch start.
    Calculate the moon phases and faces for the given day.
    Assume that all moons were "Full" and "Standard" on solar day 1.0.
    See moons_data.json for details on each moon.
    :return: dict with moon names as keys and their phases and faces as values."""

    def set_revolution_data(moon: dict) -> tuple:
        """ Compute revolution period and phase """
        rev_period = round(float(moon["period_days"]), 2)
        rev_day = ((astro_day - 1.0) % rev_period) + 1.0
        rev_day = 1.0 if rev_day == rev_period else\
            round(rev_day - 1, 2)
        offset = round(rev_day / rev_period, 2)
        if offset <= 0.03 or offset >= 0.97:
            rev_phase = "Full"
        elif offset > 0.03 and offset < 0.23:
            rev_phase = "Waning Gibbous"
        elif offset >= 0.23 and offset <= 0.27:
            rev_phase = "Waning Half Moon"
        elif offset > 0.27 and offset < 0.47:
            rev_phase = "Waning Crescent"
        elif offset >= 0.47 and offset <= 0.53:
            rev_phase = "New"
        elif offset > 0.53 and offset < 0.73:
            rev_phase = "Waxing Crescent"
        elif offset >= 0.73 and offset <= 0.77:
            rev_phase = "Waxing Half Moon"
        elif offset > 0.77 and offset < 0.97:
            rev_phase = "Waxing Gibbous"
        return (rev_period, rev_day, offset, rev_phase)

    def set_jembor_faces(offset: float) -> tuple:
        """ Set Jembor's unique rotation face names """
        if offset <= 0.03 or offset >= 0.97:
            name = "Veiborn, the Hidden One"
            notes = "Jembor rises with no markings visible."
            omen = "Secrets yet to unfold.  Read silent augurs."
        elif offset > 0.03 and offset < 0.23:
            name = "Mirror Drift, a Seer of Doubles"
            notes = "A shimmered visage reflecting another world."
            omen = "Twins, echoes, and deceptive signs."
        elif offset >= 0.23 and offset <= 0.27:
            name = "Sable Crown, Sovereign of Stillness"
            notes = "Regal and motionless. Auspicious births."
            omen = "Abdications. Rising of cloistered powers."
        elif offset > 0.27 and offset < 0.47:
            name = "Wyrmrest, the Sleeping Beast"
            notes = "Ridges give impression of scales or coils."
            omen = "Latent energy. Stirring of old memories."
        elif offset >= 0.47 and offset <= 0.53:
            name = "Ashen Gate, a Threshold of Shadows"
            notes = "A darkened rim, marked by a pale cleft."
            omen = "A portal. The hinge between worlds."
        elif offset > 0.53 and offset < 0.73:
            name = "The Weeping Stone, Tears of Cold Fire"
            notes = "Light patterns create a shining streak."
            omen = "Grief, release, and haunted songs."
        elif offset >= 0.73 and offset <= 0.77:
            name = "Eye of the Hollow, the Watcher Beyond"
            notes = "A dark circle on pale stone."
            omen = "Jembor is watching Gavor."
        elif offset > 0.77 and offset < 0.97:
            name = "The Pale Harrow, Bringer of Reckoning"
            notes = "The bright face, visible even at dawn."
            omen = "Omens of judgment, trials, or retribution."
        return (name, notes, omen)

    def set_kanka_faces(offset: float) -> tuple:
        """
        Set Kanaka's unique rotation face names,
        >> and adjust offset for its chaotic rotations <<
        """
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

    def set_rotation_data(moon: dict) -> tuple:
        # Compute rotation period and face
        rot_period = round(float(moon["rotation_period_days"]), 2)
        rot_day = rev_day + 1.0 if rot_period == rev_period else\
            ((astro_day - 1.0) % rot_period) + 1.0
        rot_day = 1.0 if rot_day == rot_period else\
            round(rot_day - 1.0, 2)
        name = "Standard"
        notes = moon["notes"]
        omen = ""
        if moon["rotation_type"] != "Synchronous":
            offset = round(rot_day / rot_period, 2)
            if moon["name"] == "Jembor":
                (name, notes, omen) =\
                    set_jembor_faces(offset)
            elif moon["name"] == "Kanka":
                (name, notes, omen) =\
                    set_kanka_faces(offset)
        return (rot_period, rot_day, name, notes, omen)

    def set_moon_return_values(phases: dict) -> dict:
        # also compute apparent/relative size
        phases[moon["name"]]["color"] = moon["apparent_color"]
        phases[moon["name"]]["revolution_period"] = rev_period
        phases[moon["name"]]["revolution_day"] = rev_day
        phases[moon["name"]]["phase_offset"] = offset
        phases[moon["name"]]["phase"] = rev_phase
        phases[moon["name"]]["rotation_type"] = moon["rotation_type"]
        phases[moon["name"]]["rotation_period"] = rot_period
        phases[moon["name"]]["rotation_day"] = rot_day
        phases[moon["name"]]["face_name"] = name
        phases[moon["name"]]["face_notes"] = notes
        phases[moon["name"]]["face_omen"] = omen
        return phases

    astro_day = sanitize_astro_day(p_astro_day)
    moon_defs = FM.get_json_file("./moons_data.json")
    phases = {"astro_day": astro_day}
    for moon in moon_defs:
        phases[moon["name"]] = {}
        (rev_period, rev_day, offset, rev_phase) =\
            set_revolution_data(moon)
        (rot_period, rot_day, name, notes, omen) =\
            set_rotation_data(moon)
        phases = set_moon_return_values(phases)

    return phases


def seed_kanka_chaos(p_years: int = 10000) -> None:
    """
    @param p_years: int - years to seed Kanka's chaotic rotations.
    The values for chaotic rotations are genreated for a span of
        10,000 astronomical years, or other input value.
    Run this function only as part of environment setup.
    Each record has the following fields:

        The day in the Astronomical calendar. Implication is that
        the chaos lasts for 24 hours (full day). When a choatic
        event is defined, it occurs "suddenly" as start of 1st day,
        the result of seismic or volcanic activity.  It slowly
        readjusts over the next n days, and then resets to the
        standard Kanka rotation (spin). The duration of the
        chaos is proportional to the magnitude of the event.
            (astro_day) - key: 5,    # imp[ies entire day, not just a pulse
            "magnitude": 6,         # 1 (minor) to 10 (cataclysmic)
            "event": "volcanic eruption", # "volcanic eruption", "earthquake", etc.
            "event_day": 1,  # the day of triggering event, or its aftermath
            "direction": "forward", # "forward" or "backward"
            "duration_days": 3,     # roughly mag * 1.5
            "note": "Brimstone Maw seen at dusk in the east"
    }
    Output: Rewrite the kanka_spin.json file.
    """

    def generate_intervals() -> list:
        """
        Generate random interval for Kanka's chaotic rotation,
        covering 10,000 years.
        The interval is a float between 3660 and 36500 days,
        representing the number of days between chaotic events.
        The interval is an integer number of days.
        """
        chaos_days: list = []
        current_day = 1
        end_day = 10000 * DAYS_PER_SOLAR_TURN  # 10,000 years
        while current_day < end_day:
            interval = random.randint(3660, 36500)  # 10 to 100 years
            current_day += interval
            if current_day < end_day:
                chaos_days.append(current_day)
        return chaos_days

    def chaos_trigger_recs(k_record, chaos_days: list) -> list:
        """
        Generate chaos triggering records for Kanka's chaotic rotations.
        """
        k_data: dict = {}
        for day in chaos_days:
            krec = k_record.copy()
            astro_day = round(day, 4)
            krec["magnitude"] = random.randint(1, 10)
            krec["event"] = random.choice([
                "volcanic eruption",
                "earthquake",
                "seismic shift",
                "ash storm",
                "fire rain",
                "lava flow"
            ])
            krec["event_day"] = 1.0
            krec["direction"] = random.choice(["forward", "backward"])
            krec["duration_days"] =\
                random.randint(int(round(krec["magnitude"] * 1.5)),
                               int(round(krec["magnitude"] * 2.5)))
            krec["note"] = random.choice([
                "Brimstone Maw seen at dusk in the east",
                "The sky darkened with ash and fire",
                "A sudden quake shook the land",
                "The ground split open, revealing molten rock",
                "A fiery glow lit the horizon at dawn",
                "The air was thick with sulfur and smoke"
            ])
            k_data[astro_day] = krec.copy()
        return k_data

    k_file = "./kanka_spin.json"
    if FM.is_file_or_dir(k_file):
        FM.delete_file(k_file)
    chaos_days = generate_intervals()
    k_record = {"magnitude": 0,
                "direction": "",
                "duration_days": 0,
                "note": ""}
    chaos_data = chaos_trigger_recs(k_record, chaos_days)
    # Next -- augment chaos_data with aftermath impacts to Kanka's rotation.
    # The aftermath is a gradual return to the standard rotation:
    # - the first day is the event trigger day, when the chaotic spin
    #  forward or backward beging. At the apex of the duration, whhich is
    #  the mid-point of the duration days, the chaotic spin is at it maximum
    #  effect, and during the rest of the duration, it gradually returns to the
    #  standard rotation. There is no permanet change to Kanka's rotation, we
    #  always return to the point where Kanka would normally be on the day after
    #  the last duration day. This implies that the face of Kanka during the
    #  chaotic period is a function of its face on the day of the event and
    #  its face on the day after the last duration day, both of whhich are
    #  predictable using the get_moon_phases function.
    #  The fun part is figuring out how to represent the chaotic
    #  rotation in the data. We can use the same structure as the
    #  get_moon_phases function....
    """
        phases[moon["name"]]["rotation_type"] = moon["rotation_type"]
        phases[moon["name"]]["rotation_period"] = rot_period
        phases[moon["name"]]["rotation_day"] = rot_day
        phases[moon["name"]]["face_name"] = name
        phases[moon["name"]]["face_notes"] = notes
        phases[moon["name"]]["face_omen"] = omen
    """
    # ... because we will be subtituting for what the get_moon_phases function
    # would return for Kanka during the chaotic period.
    # The kanka_spin data will be updated with the fields listed above, with
    # values added to the record for the event day, and more records written
    # for each day of the duration.
    # This way, the get_moon_phases function can simply read for the astro_day
    # and return the appropriate data, including the extra chaotic data.
    FM.write_file(k_file, json.dumps(chaos_data))


def count_moon_phases(moon_data: dict) -> dict:
    """
    Count the number of moons in 'New' and 'Full' phases.
    :param moon_data: dict of moon name -> {'fraction': float, 'phase': str}
    :return: dict with counts of 'New' and 'Full' phases
    """
    from collections import Counter
    phase_counter = Counter(moon['phase'] for moon in moon_data.values())
    return {
        "New Moons": phase_counter.get("New", 0),
        "Full Moons": phase_counter.get("Full", 0)
    }


def find_full_moons(solar_year_start: int,
                    solar_year_end: int,
                    full_moons_count: int) -> dict:
    """
    List full moons in a given solar year range, for days when there is a
      specified number of them (zero to 8).
    :param solar_year_start: The starting solar day of the year (int).
    :param solar_year_end: The ending solar day of the year (int).
    :param full_moons_count: Exact number of full moons expected.
    :return: A dict solar days within the range that have the specified
            minimum number of full moons, a list of moons that are full.
    @TODO: Tweak to alternatively find new moons within a range
    """
    year_start = sanitize_solar_turn(solar_year_start)
    year_end = sanitize_solar_turn(solar_year_end)

    # print(f"Finding full moons from {year_start} to {year_end} ")

    # There are 8 moons, so max full moons is 8, min is 0.
    full_moons_count = max(0, min(8, int(full_moons_count)))

    # print(f"Looking for {full_moons_count} full moons in the range.")

    # A solar year is 365.2422 days long.
    # Compute the first day of specified year:
    day_start = round((year_start - 1) * DAYS_PER_SOLAR_TURN + 1, 4)
    # Compute the last day of specified year-end:
    day_end = round(year_end * DAYS_PER_SOLAR_TURN, 4)

    # print(f"Searching from day {day_start} to {day_end}")

    moon_days = []

    step = 1.0
    # Include stop by adding step and filtering
    days = np.arange(day_start, day_end + step, step)
    days = days[days <= day_end]  # Trim if over
    for astro_day in np.round(days, 4):
        pulses = get_pulses_from_astro_day(astro_day)
        solar_day = get_solar_day_from_pulse(pulses)
        moons = get_moon_phases(solar_day)
        m_count = count_moon_phases(moons)
        print(f"astro_day: {astro_day}, solar_day: {solar_day}, {get_astro_turn(astro_day)}")
        if m_count["Full Moons"] == full_moons_count:
            moon_days.append([astro_day,
                              solar_day,
                              get_solar_month(solar_day),
                              get_astro_turn(astro_day)])

    return ({"count": full_moons_count, "start": solar_year_start, "end": solar_year_end},
            {"full moon days": moon_days})


def get_star_context(solar_day: float) -> dict:
    """
    Get the star context for a given day.
    The House of the Equinox is a set of 12 constellations visible
        at different times of the year.
    This minimal implementation provides:
    - set of named constellations visible in a given solar month
    - 12 "fixed stars" visible in the season(s) to which the day belongs
    4 stars are visible in each season, and they are named:
    - Ilyrun, the Pole Star, is sacred to navigators and mystics.
        “The eye that never - closes.”
    - Kresh is known as “The Hinge” or “The Ladle” depending on the tradition.
    - Marnok is “The Claw Below” and often used as a marker for north-bound travel.
    - Sethera is “The Gathering Star” and sometimes mistaken for a wandering one.

    :param day: The day number in the true solar calendar. Sanitized.
    :return: A dictionary containing the House of the Equinox and
              fixed stars visible on that day.
    @TODO: Add lore regarding the House of the Equinox and the fixed stars.
    """
    solar_day = sanitize_solar_day(solar_day)
    solar_month = get_solar_month(solar_day)["solar_month"] - 1  # 0-indexed
    house = [
        "The Ember Gate",
        "The Twin Horns",
        "The Hollow Root",
        "The Loom of Krenna",
        "The Silver Wheel",
        "The Broken Staff",
        "The Thorned Veil",
        "The Watchers of Stillness",
        "The Burning Mirror",
        "The Chain of Four",
        "The Lantern Grove",
        "The Stone Circle",
    ][solar_month]
    fixed_stars = [
        ("Aghur", "Stillness", "in the north-northeast, low above the frostline"),
        ("Thalona", "Greening", "in the east, just above the sowing fields"),
        ("Mirrest", "Blazing", "in the south-southeast, blazing over the old hills"),
        ("Krenna", "Withering", "in the west, near the horizon where the sun lingers"),
        ("Tursin", "Greening", "in the northeast, halfway to the pole star"),
        ("Boreth", "Stillness", "high in the northern sky, just east of the North Watch"),
        ("Zomel", "Blazing", "low in the southwest, near the veil of clouds"),
        ("Ethranel", "Withering", "in the east-northeast, just before dawn"),
        ("Velkora", "Greening", "in the west-northwest, between the Split Peaks"),
        ("Saurnak", "Blazing", "in the south, tucked near the Lantern Grove"),
        ("Droven", "Stillness", "rising in the east with the third bell of night"),
        ("Henmae", "Withering", "in the west-southwest, red and near the harvest haze"),
        # Pole Star and its Minions, visible in all seasons
        ("Ilyrun", "All", "the Pole Star, unwavering in the true north"),
        ("Kresh", "All", "to the left of Ilyrun, rising and dipping like a kettle"),
        ("Marnok", "All", "below Ilyrun, clawing at the trees of the high north"),
        ("Sethera", "All", "to the right of Ilyrun, where wanderers sometimes gather"),
    ]
    season = get_solar_season(solar_day)["solar_season"]
    visible = [(n, d) for n, s, d in fixed_stars if (s == season or s == "All")]
    return {"Constellation": house, "Fixed Stars": visible}


def get_saskan_time_from_pulse(pulse_count: int) -> dict:
    """
    Convert galactic pulse (0–86399) to Saskan time:
    - 6 Watches (4 hours each)
    - 8 Bells per Watch (30 minutes each)
    - 6 Wayts per Bell (5 minutes each)
    For now, no attempt is made to account for local time differences.
    @param pulse_count: int from 0 to 86399 (seconds since local midnight)
    @return: dict with 'spoken_time', 'written_time', 'earth_time'
    """
    pulse_count = sanitize_pulse_count(pulse_count)
    # Earth time (24-hour format)
    hours = pulse_count // 3600
    minutes = (pulse_count % 3600) // 60
    seconds = pulse_count % 60
    earth_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    # Watch: 4 hours = 14,400 pulses
    watch_number = pulse_count // 14400 + 1  # 1-based
    watch_start = (watch_number - 1) * 14400
    pulses_into_watch = pulse_count - watch_start
    # Bell: 1800 pulses (30 minutes)
    bell_number = pulses_into_watch // 1800 + 1  # 1-based
    bell_start = (bell_number - 1) * 1800
    pulses_into_bell = pulses_into_watch - bell_start
    # Wayt: 300 pulses (5 minutes)
    wayt_number = (pulses_into_bell // 300) + 1  # 1–6
    # Spoken time
    spoken = f"{bell_number}-bell-{wayt_number} of the {ordinal(watch_number)} Watch"
    written = f"{watch_number}/{bell_number}:{wayt_number}"

    return {
        "spoken_time": spoken,
        "written_time": written,
        "earth_time": earth_time,
    }


class Wanderer:
    """
    A class representing a wanderer (planet) in the Saskan calendar system.
    The wanderer has a name, an orbital period, and a phase, which are provided
    as parameters during instantiation and stored as attributes. The class
    has methods to calculate:
    - position of the wanderer in its orbit
    - visbility - if it is visible tonight based on its position
    :param name: (required) The name of the wanderer.
    :param period: (required) The orbital period of the wanderer in days.
    :param phase: (optional) The phase of the wanderer (default is 0.0).
    :return: None. Use this class to instantiate a wanderer object.
    See get_wanderers() function for an example of how to use this class.

    """
    def __init__(self, name, period, phase=0.0):
        self.name = name
        self.period = period
        self.phase = phase

    def pos(self, solar_day):
        """
        @param d: The current day in the true solar calendar.
        solar_day	The current solar day

        Other values (from the Wanderer object) are:
        period	Orbital period of the wanderer (in days)
        phase	Initial phase offset (where the planet starts at day 0)
        % 1	Wraps the result into a range between 0.0 and 1.0

        @return: The position of the wanderer in its orbit as a float
        The result is a value:
        0.0 → aligned with Fatune (in conjunction, "behind" Fatune)
        0.25 → quarter orbit away (roughly at greatest elongation)
        0.5 → opposite side of the sky (at opposition, best visibility)
        0.75 → returning toward Fatune
        1.0 ≡ 0.0 (back in conjunction again)

        Think of it like normalized orbital longitude (a simplified angle), where:
        0.0 or 1.0 = aligned with Fatune = obscured
        0.5 = opposite side = brightest, best viewing
        """
        return (solar_day / self.period + self.phase) % 1

    def vis(self, w_pos):
        """
        @param w_pos: The position of the wanderer in its orbit (0.0 to 1.0).
        The wanderer is visible only if it’s at least 10% away
          from direct conjunction with Fatune.
        If it’s too close to Fatune from the observer’s view on Gavor, we assume it’s:
                Lost in the solar glare
                Not visible in the night sky
        The range (0.1, 0.9) means:
            80% of the orbit is potentially visible
            20% (0.0–0.1 and 0.9–1.0) is blocked by sunlight
        @return: True if the wanderer is visible tonight, False otherwise.
        """
        return 0.1 < w_pos < 0.9


def get_wanderers(solar_day: float) -> dict:
    """
    @param solar_day: The day number in the true solar calendar.
    Create a list of wanderers (planets) with their orbital periods and phases.
    Calculate their positions and visibility for the given day.
    The "Spark" is Saskan lore for an unusual event near one of the moons.
      The reality is that it is an extraterrestrial object docked
        in geosynchronous orbit on the dark side of the moon,
        but occasionally wanders into a visible location.
    The "Rare Comet" is another special event that occurs with low probability.
    @return: A dictionary containing the wanderers' names, their
             orbital phases, and whether they are visible tonight.
    """
    # Define wanderers. Name, orbital period in solar days:
    wolist = [
        Wanderer("Aesthra", 88),
        Wanderer("Lethra", 88, 0.5),
        Wanderer("Beyarus", 225),
        Wanderer("Dramond", 365.2422),
        Wanderer("Thurnak", 687),
        Wanderer("Zelven", 4380),
        Wanderer("Kreetha", 10585),
    ]
    # Get phase and visibility for each wanderer for the given solar day
    wdict = {
        wobj.name: {"Phase": round(wobj.pos(solar_day), 4),
                    "Visible": wobj.vis(wobj.pos(solar_day))}
        for wobj in wolist
    }
    # Get visibility of the Spark and Rare Comet
    random.seed(solar_day + 42)
    wdict["The Spark"] = {"Phase": "n/a", "Visible": random.random() < 0.01}
    random.seed(solar_day + 1337)
    if random.random() < 0.0003:
        wdict["A Rare Comet"] = {"Phase": "n/a", "Visible": True}
    return wdict


def count_visible_wanderers(wanderers: dict) -> int:
    """
    Count how many wanderers are visible.
    :param wanderers: A dictionary of wanderer data, each containing a 'Visible' boolean key.
    :return: Integer count of wanderers where 'Visible' is True.
    """
    visible_count = sum(1 for info in wanderers.values() if info.get("Visible") is True)
    return {"visible_wanderers": visible_count}


class FatunikCalendar:
    """
    Compute the date in the Fatunik calendar system.
    The Fatunik calendar is a strictly solar calendar, but is organized into 13
    months. The first month is a short month of 5 days (or 6 days in leap years).
    All remaining months are 30 days long. Calendar begins on Summer Solstice.
    Note that the Solstice is the first day of Summer, not Mid-Summer as is sometimes
      stated int the lore. If I want it be Mid-Summer Day, then I will need to add
      mid-season events to the get_solar_season function.
    Fatunik (solar) months and days are numbered starting at 1.
    :param: days: the number of days since the Astro epoch, counting from zero.
    :return: dict (turn, turn-day, month, month-day, leap year, astro info)
    @TODO: Add month names, perhaps based on a language param.
    """
    def __init__(self, astro_day):
        """
        :param astro_day: (int) number of days since epoch start.
        Negative values get set to zero by the AstroCalendar class.
        """
        self.astro = AstroCalendar(astro_day)
        self.fat_astro_day = self.astro.get_astro_date()["astro_day"]

    def get_date(self):
        flabel = "Pre-Fatunik Epoch"
        fyr = -1
        fyr_dy = -1
        fmo = -1
        fmo_dy = -1
        fleap = False

        def calendar_date(astro_day):
            # Each 4-year cycle = 1461 days
            full_cycles = astro_day // 1461
            day_in_cycle = astro_day % 1461

            if day_in_cycle < 365:
                year_in_cycle = 0
                day_of_year = day_in_cycle + 1
            elif day_in_cycle < 730:
                year_in_cycle = 1
                day_of_year = day_in_cycle - 365 + 1
            elif day_in_cycle < 1095:
                year_in_cycle = 2
                day_of_year = day_in_cycle - 730 + 1
            else:
                year_in_cycle = 3
                day_of_year = day_in_cycle - 1095 + 1

            calendar_year = full_cycles * 4 + year_in_cycle + 1
            is_leap_year = (year_in_cycle == 3)

            return calendar_year, day_of_year, is_leap_year

        if self.fat_astro_day >= FATUNIK_EPOCH_DAY:
            flabel = "Fatunik Epoch"
            fyr, fyr_dy, fleap = calendar_date(self.fat_astro_day - FATUNIK_EPOCH_DAY)
            mo1_max = 6 if fleap else 5  # First month has 5 or 6 days
            # If within the first month, set month to 1 and day to fyr_dy.
            if fyr_dy <= mo1_max:
                fmo = 1
                fmo_dy = fyr_dy
            else:
                # After the short first month, there are always 12 months of 30 days,
                #   whether it is a leap year or not.
                adjust_dy = fyr_dy - mo1_max
                fmo = (adjust_dy - 1) // 30 + 2
                fmo_dy = (adjust_dy - 1) % 30 + 1

        return {"fatunik_turn": fyr,
                "fatunik_turn_day": fyr_dy,
                "fatunik_month_number": fmo,
                "fatunik_month_day": fmo_dy,
                "is_leap_turn": fleap,
                "label": flabel} | self.astro.get_astro_date()


class StrictLunarCalendar:
    """
    A strict lunar calendar that does not account for leap years.
    As a result, the year slides through the seasons.
    It is based on the lunar month average and the lunar epoch-start day.
    Also referred to as the Lunar A calendar system or the
        "Traditional Terpin Lunar Calendar".
    :param: days: the number of days since the Rosetta epoch.
    :return: dict (turn, month, day)
    """
    def __init__(self, ros_day):
        self.rosdy = ros_day

    def get_date(self):
        dros = self.rosdy - LUNAR_EPOCH_DAY        # days since lunar epoch start
        lyr = int(dros // (LUNAR_MONTH_AVG * 12))  # lunar year (turn)
        ldtz = dros % (LUNAR_MONTH_AVG * 12)       # lunar day from zero
        lmo = int(ldtz // LUNAR_MONTH_AVG) + 1     # lunar month from one
        ldy = int(ldtz % LUNAR_MONTH_AVG) + 1      # lunar day from one
        return {"turn": lyr,
                "month": lmo,
                "day": ldy}


class LunarSolarCalendar:
    """
    A lunar/solar calendar accounts for leap years by adjusting the
      lunar yearś slide through the seasons periodically.
    The leap year is every 5 years, and the leap month is
        added to the end of the year.
    Like the Lunar A calendar, it is based on the lunar month average
        and the lunar epoch-start day.
    Also referred to as the Lunar B calendar system or the
        "Reformed Terpin Lunar Calendar".
    :param: days: the number of days since the Rosetta epoch.
    :return: dict (turn, month, day, is_leap)
    """
    def __init__(self, ros_day):
        self.rosdy = ros_day

    def get_date(self):
        dros = self.rosdy - LUNAR_EPOCH_DAY  # days since lunar epoch start
        lyr = int(dros // 365.25)
        lleap = lyr % 5 == 0            # is lunar leap year
        days = LUNAR_MONTH_AVG * 12 + (LUNAR_MONTH_AVG if lleap else 0)
        lyr = int(dros // days)         # lunar year (turn)
        ldtz = dros % days              # lunar day from zero
        lmo = int(ldtz // LUNAR_MONTH_AVG) + 1
        ldy = int(ldtz % LUNAR_MONTH_AVG) + 1
        return {"turn": lyr,
                "month": lmo,
                "day": ldy,
                "is_leap": lleap}


def universal_date_translator(day: int, time: Union[int, float] = 12.0):
    """
    Translate a given day and time into various calendar systems.
    :param day: The day number in the Rosetta calendar.
        Cannot be less than 0.
    :param time: The time of Rosetta day in hours (0-24).
        Default is 12.0 (noon).
        If time is less than 0 or greater than 24, it will be set to 12.0.
        0 is midnight, 6 is dawn, 12 is noon, 18 is dusk.
    :return: A dictionary containing the date in various calendar systems.
      The dictionary includes:
        - Rosetta (Canonical)
        - Fatunik Calendar
        - Lunar A Calendar
        - Lunar B Calendar
        - Moon Phases
        - Wanderers and Events
        - Galactic Time (Pulsar Clock)
        - Sky Context
    """
    canon = AstroCalendar(day)
    """
    fat = FatunikCalendar(day - 1 if time < 6 else day)
    la = StrictLunarCalendar(day - 1 if time < 18 else day)
    lb = LunarSolarCalendar(day - 1 if time < 18 else day)
    """
    return {
        "Rosetta": {
            "Day": day,
            "Hour": f"{time:02.0f}:00",
            "Turn": canon.get_turn_day()["ros_turn"],
            "Day in Turn": canon.get_turn_day()["ros_day_cnt"],
            "Season": canon.get_solar_season(),
        },
        # "Fatunik Calendar": fat.get_date(),
        # "Lunar A Calendar": la.get_date(),
        # "Lunar B Calendar": lb.get_date(),
        # "Moon Phases": get_moon_phases(day),
        # "Wanderers and Events": get_wanderers(day),
        # "Galactic Time (Pulsar Clock)": {
        #    "Pulse Count": ASTRO_EPOCH_PULSE + int(day * PULSES_PER_DAY)
        # "Sky Context": get_star_context(day),
    }
