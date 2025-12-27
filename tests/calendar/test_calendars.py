import pytest
from pprint import pprint as pp
from app_calendar import (
    AstroCalendar,
    FatunikCalendar,
)  # StrictLunarCalendar, LunarSolarCalendar


@pytest.mark.parametrize(
    "astro_day, expected_turn, expected_turn_day, expected_season",
    [
        (-4567, 0, 0, "Stillness"),
        (0, 0, 0, "Stillness"),
        (270, 0, 270, "Withering"),
        (366, 1, 0, "Stillness"),
        (4536, 12, 153, "Greening"),
        (45360, 124, 69, "Stillness"),
        (182717, 500, 92, "Greening"),  # Start of the Lunar calendars
        (365472, 1000, 222, "Blazing"),  # Start of the Fatunik calendar
        (387652, 1061, 121, "Greening"),
        (452431, 1238, 251, "Blazing"),
        (513400, 1405, 223, "Blazing"),
    ],
)
def test_astro_date(astro_day, expected_turn, expected_turn_day, expected_season):
    astro = AstroCalendar(astro_day)
    astro_date = astro.get_astro_date()
    pp((astro_date))
    assert astro_date["Astro"]["turn"] == expected_turn
    assert astro_date["Astro"]["turn_day"] == expected_turn_day
    assert astro_date["Astro"]["season"]["name"] == expected_season


@pytest.mark.parametrize(
    "day, expected_label",
    [
        (0, "Pre-Fatunik Epoch"),
        (-4533, "Pre-Fatunik Epoch"),
        (365471, "Pre-Fatunik Epoch"),
        (365472, ""),
        (883847, ""),
        (9993432, ""),
    ],
)
def test_fatunik_turn_labels(day, expected_label):
    """
    FATUNIK_EPOCH_DAY = 365472
    @TODO: Add tests for seaosonal events
    """
    fatcal = FatunikCalendar(day)
    fat_date = fatcal.get_date()
    pp(fat_date)
    assert fat_date["Fatunik"]["label"] == expected_label


@pytest.mark.parametrize(
    "astro_day, expected_turn, expected_month, "
    + "day_of_month, expected_season, is_leap_turn, expected_label, "
    + "expected_event",
    [
        (365472, 1, 1, 1, "Blazing", False, "", "Fatune Day"),
        (365478, 1, 2, 1, "Blazing", False, "", ""),
        (365508, 1, 3, 1, "Blazing", False, "", ""),
        (365538, 1, 4, 1, "Withering", False, "", ""),  # Needs tweaking
        (365568, 1, 5, 1, "Withering", False, "", ""),
        (365837, 2, 1, 1, "Blazing", False, "", ""),
        (366202, 3, 1, 1, "Blazing", False, "", ""),
        (366567, 4, 1, 1, "Blazing", True, "", ""),
    ],
)
def test_fatunik_date(
    astro_day,
    expected_turn,
    expected_month,
    day_of_month,
    expected_season,
    is_leap_turn,
    expected_label,
    expected_event,
):
    """
    FATUNIK_EPOCH_DAY = 365472
    @TODO: Add tests for seaosonal events
    """
    fatcal = FatunikCalendar(astro_day)
    fat_date = fatcal.get_date()
    pp(fat_date)
    assert fat_date["Fatunik"]["turn"] == expected_turn
    assert fat_date["Fatunik"]["month_number"] == expected_month
    assert fat_date["Fatunik"]["month_day"] == day_of_month
    assert fat_date["Fatunik"]["season"]["name"] == expected_season
    assert fat_date["Fatunik"]["is_leap_turn"] == is_leap_turn
    assert fat_date["Fatunik"]["label"] == expected_label
    assert fat_date["Fatunik"]["season"]["event"] == expected_event


"""
@pytest.mark.parametrize("day", [0, 397419, 1455000])
def test_lunar_a_output(day):
    cal = StrictLunarCalendar(day)
    d = cal.get_date()
    assert "Turn" in d
    assert "Month" in d
    assert "Day" in d
    assert "epoch_relative" in d
    assert "label" in d


@pytest.mark.parametrize("day", [0, 397419, 1455000])
def test_lunar_b_output(day):
    cal = LunarSolarCalendar(day)
    d = cal.get_date()
    assert "Turn" in d
    assert "Month" in d
    assert "Day" in d
    assert "Leap Turn" in d
    assert "epoch_relative" in d
    assert "label" in d
"""
