"""
app_timeline.utils.temporal

Temporal unit conversion utilities for the Saskan timeline system.

The Saskan timeline uses astro_day (day count) as the fundamental unit.
This module provides conversions to higher-level temporal concepts.

Temporal Units:
- pulse: 1 second (86,400 pulses per day)
- day: 1 astro_day
- turn: 365.25 days (synonym for solar year)
- decade: 10 turns (3,652.5 days)
- century: 100 turns (36,525 days)
- shell: 132 turns (48,213 days - average Terpin lifespan)
"""

from __future__ import annotations

# Temporal unit constants (in days)
PULSES_PER_DAY = 86400
DAYS_PER_TURN = 365.25
DAYS_PER_DECADE = 3652.5  # 10 turns
DAYS_PER_CENTURY = 36525  # 100 turns
DAYS_PER_SHELL = 48213  # 132 turns (Terpin lifespan)


def days_to_turns(days: int | float) -> float:
    """
    Convert astro_days to turns (years).

    :param days: Number of days
    :return: Equivalent number of turns
    """
    return days / DAYS_PER_TURN


def turns_to_days(turns: int | float) -> int:
    """
    Convert turns (years) to astro_days.

    :param turns: Number of turns
    :return: Equivalent number of days (rounded to integer)
    """
    return int(turns * DAYS_PER_TURN)


def days_to_decades(days: int | float) -> float:
    """
    Convert astro_days to decades.

    :param days: Number of days
    :return: Equivalent number of decades
    """
    return days / DAYS_PER_DECADE


def decades_to_days(decades: int | float) -> int:
    """
    Convert decades to astro_days.

    :param decades: Number of decades
    :return: Equivalent number of days (rounded to integer)
    """
    return int(decades * DAYS_PER_DECADE)


def days_to_centuries(days: int | float) -> float:
    """
    Convert astro_days to centuries.

    :param days: Number of days
    :return: Equivalent number of centuries
    """
    return days / DAYS_PER_CENTURY


def centuries_to_days(centuries: int | float) -> int:
    """
    Convert centuries to astro_days.

    :param centuries: Number of centuries
    :return: Equivalent number of days (rounded to integer)
    """
    return int(centuries * DAYS_PER_CENTURY)


def days_to_shells(days: int | float) -> float:
    """
    Convert astro_days to shells (Terpin lifespans).

    :param days: Number of days
    :return: Equivalent number of shells
    """
    return days / DAYS_PER_SHELL


def shells_to_days(shells: int | float) -> int:
    """
    Convert shells to astro_days.

    :param shells: Number of shells
    :return: Equivalent number of days (rounded to integer)
    """
    return int(shells * DAYS_PER_SHELL)


def format_duration(days: int, use_turns: bool = True) -> str:
    """
    Format a duration in days as a human-readable string.

    :param days: Number of days
    :param use_turns: If True, use turns/decades/centuries; if False, use only days
    :return: Formatted string (e.g., "1.5 turns", "2 centuries", "500 days")
    """
    if not use_turns or days < DAYS_PER_TURN:
        return f"{days} days"

    # Use the largest appropriate unit
    if days >= DAYS_PER_CENTURY:
        centuries = days_to_centuries(days)
        return (
            f"{centuries:.2f} centuries"
            if centuries < 10
            else f"{centuries:.1f} centuries"
        )
    elif days >= DAYS_PER_DECADE:
        decades = days_to_decades(days)
        return f"{decades:.2f} decades" if decades < 10 else f"{decades:.1f} decades"
    else:
        turns = days_to_turns(days)
        return f"{turns:.2f} turns" if turns < 10 else f"{turns:.1f} turns"


def format_lifespan(founded_day: int | None, dissolved_day: int | None) -> str:
    """
    Format a lifespan (founded to dissolved) as a human-readable string.

    :param founded_day: Day founded (None if unknown)
    :param dissolved_day: Day dissolved (None if still active)
    :return: Formatted string (e.g., "Day 0 → 500 (1.37 turns)", "Day 100 → present")
    """
    if founded_day is None:
        return "Unknown founding"

    if dissolved_day is None:
        return f"Day {founded_day} → present"

    duration = dissolved_day - founded_day
    duration_str = format_duration(duration)
    return f"Day {founded_day} → {dissolved_day} ({duration_str})"
