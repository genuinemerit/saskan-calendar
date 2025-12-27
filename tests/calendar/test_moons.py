import pytest
from app import get_moon_phases


@pytest.mark.parametrize("day", [0, 15, 33, 100])
def test_endor_phase_fraction_in_bounds(day):
    phase = get_moon_phases(day)["Endor"]
    assert 0.0 <= phase["Fraction"] <= 1.0
    assert phase["Phase"] in {
        "New",
        "Waxing Crescent",
        "First Quarter",
        "Waxing Gibbous",
        "Full",
        "Waning Gibbous",
        "Last Quarter",
        "Waning Crescent",
    }


@pytest.mark.parametrize("day", [0, 16, 33])
def test_moon_keys_present(day):
    phases = get_moon_phases(day)
    for moon, info in phases.items():
        assert "Phase" in info
        assert "Fraction" in info
