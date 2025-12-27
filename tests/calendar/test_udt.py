import pytest
from app_calendar import universal_date_translator


@pytest.mark.parametrize("day", [0, 799875, 1455000])
def test_universal_output_keys(day):
    udt = universal_date_translator(day)
    assert "Rosetta (Canonical)" in udt
    assert "Fatunik Calendar" in udt
    assert "Lunar A Calendar" in udt
    assert "Lunar B Calendar" in udt
    assert "Moon Phases" in udt
    assert "Wanderers and Events" in udt
    assert "Galactic Time (Pulsar Clock)" in udt
    assert "Sky Context" in udt
