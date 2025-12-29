"""
tests.timeline.test_temporal

Tests for temporal conversion utility functions.
"""

from __future__ import annotations

import pytest

from app_timeline.utils import (
    DAYS_PER_CENTURY,
    DAYS_PER_DECADE,
    DAYS_PER_SHELL,
    DAYS_PER_TURN,
    PULSES_PER_DAY,
    centuries_to_days,
    days_to_centuries,
    days_to_decades,
    days_to_shells,
    days_to_turns,
    decades_to_days,
    format_duration,
    format_lifespan,
    shells_to_days,
    turns_to_days,
)


class TestTemporalConstants:
    """Tests for temporal constants."""

    def test_pulses_per_day(self):
        """Test that PULSES_PER_DAY equals seconds in a day."""
        assert PULSES_PER_DAY == 86400

    def test_days_per_turn(self):
        """Test that DAYS_PER_TURN equals solar year."""
        assert DAYS_PER_TURN == 365.25

    def test_days_per_decade(self):
        """Test that DAYS_PER_DECADE equals 10 turns."""
        assert DAYS_PER_DECADE == 10 * DAYS_PER_TURN

    def test_days_per_century(self):
        """Test that DAYS_PER_CENTURY equals 100 turns."""
        assert DAYS_PER_CENTURY == 100 * DAYS_PER_TURN

    def test_days_per_shell(self):
        """Test that DAYS_PER_SHELL equals 132 turns."""
        assert DAYS_PER_SHELL == 132 * DAYS_PER_TURN


class TestTurnConversions:
    """Tests for turn conversion functions."""

    def test_days_to_turns_exact(self):
        """Test converting exact turn values."""
        assert days_to_turns(365.25) == pytest.approx(1.0)
        assert days_to_turns(730.5) == pytest.approx(2.0)
        assert days_to_turns(3652.5) == pytest.approx(10.0)

    def test_days_to_turns_partial(self):
        """Test converting partial turn values."""
        assert days_to_turns(182.625) == pytest.approx(0.5)
        assert days_to_turns(100) == pytest.approx(0.27379, rel=1e-4)

    def test_turns_to_days_exact(self):
        """Test converting turns to days."""
        assert turns_to_days(1) == 365
        assert turns_to_days(2) == 730
        assert turns_to_days(10) == 3652

    def test_turns_to_days_partial(self):
        """Test converting partial turns to days."""
        assert turns_to_days(0.5) == 182
        assert turns_to_days(1.5) == 547

    def test_round_trip_conversion(self):
        """Test that days->turns->days is consistent."""
        original_days = 1000
        turns = days_to_turns(original_days)
        converted_days = turns_to_days(turns)
        assert abs(converted_days - original_days) <= 1  # Allow 1 day rounding error


class TestDecadeConversions:
    """Tests for decade conversion functions."""

    def test_days_to_decades_exact(self):
        """Test converting exact decade values."""
        assert days_to_decades(3652.5) == pytest.approx(1.0)
        assert days_to_decades(36525) == pytest.approx(10.0)

    def test_days_to_decades_partial(self):
        """Test converting partial decade values."""
        assert days_to_decades(1826.25) == pytest.approx(0.5)

    def test_decades_to_days_exact(self):
        """Test converting decades to days."""
        assert decades_to_days(1) == 3652
        assert decades_to_days(10) == 36525

    def test_decades_to_days_partial(self):
        """Test converting partial decades to days."""
        assert decades_to_days(0.5) == 1826


class TestCenturyConversions:
    """Tests for century conversion functions."""

    def test_days_to_centuries_exact(self):
        """Test converting exact century values."""
        assert days_to_centuries(36525) == pytest.approx(1.0)
        assert days_to_centuries(73050) == pytest.approx(2.0)

    def test_days_to_centuries_partial(self):
        """Test converting partial century values."""
        assert days_to_centuries(18262.5) == pytest.approx(0.5)

    def test_centuries_to_days_exact(self):
        """Test converting centuries to days."""
        assert centuries_to_days(1) == 36525
        assert centuries_to_days(2) == 73050

    def test_centuries_to_days_partial(self):
        """Test converting partial centuries to days."""
        assert centuries_to_days(0.5) == 18262


class TestShellConversions:
    """Tests for shell conversion functions."""

    def test_days_to_shells_exact(self):
        """Test converting exact shell values."""
        assert days_to_shells(48213) == pytest.approx(1.0)
        assert days_to_shells(96426) == pytest.approx(2.0)

    def test_days_to_shells_partial(self):
        """Test converting partial shell values."""
        assert days_to_shells(24106.5) == pytest.approx(0.5)

    def test_shells_to_days_exact(self):
        """Test converting shells to days."""
        assert shells_to_days(1) == 48213
        assert shells_to_days(2) == 96426

    def test_shells_to_days_partial(self):
        """Test converting partial shells to days."""
        assert shells_to_days(0.5) == 24106


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_format_duration_days_only(self):
        """Test formatting durations in days only."""
        assert format_duration(100, use_turns=False) == "100 days"
        assert format_duration(365, use_turns=False) == "365 days"

    def test_format_duration_small_days(self):
        """Test formatting small durations (< 1 turn)."""
        assert format_duration(100) == "100 days"
        assert format_duration(300) == "300 days"

    def test_format_duration_turns(self):
        """Test formatting durations in turns."""
        # 365 days < DAYS_PER_TURN (365.25), so shows as days
        result = format_duration(365)
        assert "days" in result

        # 730 days >= DAYS_PER_TURN, so shows as turns
        result = format_duration(730)
        assert "turn" in result
        assert "2.00" in result or "2.0" in result

        # Test value >= DAYS_PER_TURN
        result = format_duration(366)
        assert "turn" in result
        assert "1.00" in result or "1.0" in result

    def test_format_duration_decades(self):
        """Test formatting durations in decades."""
        # 3652 days < DAYS_PER_DECADE (3652.5), so shows as turns
        result = format_duration(3652)
        assert "turn" in result

        # Test value >= DAYS_PER_DECADE
        result = format_duration(3653)
        assert "decade" in result
        assert "1.00" in result or "1.0" in result

        result = format_duration(7305)
        assert "decade" in result
        assert "2.00" in result or "2.0" in result

    def test_format_duration_centuries(self):
        """Test formatting durations in centuries."""
        result = format_duration(36525)
        assert "centur" in result
        assert "1.00" in result or "1.0" in result

        result = format_duration(73050)
        assert "centur" in result
        assert "2.00" in result or "2.0" in result

    def test_format_duration_precision(self):
        """Test that large values use lower precision."""
        # Small values (< 10) use .2f precision
        # 1826 days is ~5 turns, not 0.5 decades
        result = format_duration(int(DAYS_PER_TURN * 5))  # 5 turns
        assert "5.00" in result or "5.0" in result
        assert "turn" in result

        # Large values (>= 10) use .1f precision
        result = format_duration(int(DAYS_PER_CENTURY * 10))  # 10 centuries
        assert "10.0" in result
        assert "centur" in result


class TestFormatLifespan:
    """Tests for format_lifespan function."""

    def test_format_lifespan_unknown_founding(self):
        """Test formatting lifespan with unknown founding."""
        assert format_lifespan(None, 1000) == "Unknown founding"

    def test_format_lifespan_still_active(self):
        """Test formatting lifespan for still active entity."""
        result = format_lifespan(100, None)
        assert "Day 100" in result
        assert "present" in result

    def test_format_lifespan_dissolved(self):
        """Test formatting lifespan for dissolved entity."""
        result = format_lifespan(0, 500)
        assert "Day 0" in result
        assert "500" in result
        assert "day" in result.lower()

    def test_format_lifespan_includes_duration(self):
        """Test that lifespan includes formatted duration."""
        result = format_lifespan(0, 730)
        assert "Day 0" in result
        assert "730" in result
        assert "turn" in result.lower() or "day" in result.lower()


class TestConversionAccuracy:
    """Tests for conversion accuracy and edge cases."""

    def test_zero_values(self):
        """Test converting zero values."""
        assert days_to_turns(0) == 0.0
        assert turns_to_days(0) == 0
        assert days_to_decades(0) == 0.0
        assert decades_to_days(0) == 0
        assert days_to_centuries(0) == 0.0
        assert centuries_to_days(0) == 0
        assert days_to_shells(0) == 0.0
        assert shells_to_days(0) == 0

    def test_large_values(self):
        """Test converting large values."""
        large_days = 1000000
        assert days_to_turns(large_days) > 0
        assert days_to_centuries(large_days) > 0

        large_turns = 10000
        assert turns_to_days(large_turns) > 0

    def test_fractional_inputs(self):
        """Test that fractional inputs work correctly."""
        assert days_to_turns(365.25) == pytest.approx(1.0)
        assert turns_to_days(1.5) == 547
        assert decades_to_days(0.1) == 365
