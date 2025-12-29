"""
tests.timeline.test_validation

Tests for validation utility functions.
"""

from __future__ import annotations

import pytest

from app_timeline.utils import (
    GRID_X_MAX,
    GRID_X_MIN,
    GRID_Y_MAX,
    GRID_Y_MIN,
    VALID_ENTITY_TYPES,
    VALID_EVENT_TYPES,
    VALID_ROUTE_DIFFICULTIES,
    VALID_ROUTE_TYPES,
    VALID_SETTLEMENT_TYPES,
    validate_date_range,
    validate_entity_type,
    validate_event_type,
    validate_grid_coordinates,
    validate_non_negative,
    validate_positive,
    validate_route_difficulty,
    validate_route_type,
    validate_settlement_type,
)


class TestValidateDateRange:
    """Tests for validate_date_range function."""

    def test_valid_date_range(self):
        """Test that valid date ranges pass."""
        validate_date_range(0, 100)
        validate_date_range(0, 1)
        validate_date_range(100, 1000)

    def test_equal_dates_with_allow_equal(self):
        """Test that equal dates pass when allow_equal=True."""
        validate_date_range(100, 100, allow_equal=True)
        validate_date_range(0, 0, allow_equal=True)

    def test_equal_dates_without_allow_equal(self):
        """Test that equal dates fail when allow_equal=False."""
        with pytest.raises(ValueError, match="must be <"):
            validate_date_range(100, 100, allow_equal=False)

    def test_inverted_date_range(self):
        """Test that inverted ranges fail."""
        with pytest.raises(ValueError, match="must be"):
            validate_date_range(100, 50)

    def test_negative_start_day(self):
        """Test that negative start day fails."""
        with pytest.raises(ValueError, match="Start day cannot be negative"):
            validate_date_range(-1, 100)

    def test_negative_end_day(self):
        """Test that negative end day fails."""
        with pytest.raises(ValueError, match="End day cannot be negative"):
            validate_date_range(0, -1)

    def test_both_negative(self):
        """Test that both negative days fail."""
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_date_range(-10, -5)


class TestValidateGridCoordinates:
    """Tests for validate_grid_coordinates function."""

    def test_valid_coordinates(self):
        """Test that valid coordinates pass."""
        validate_grid_coordinates(1, 1)
        validate_grid_coordinates(20, 15)
        validate_grid_coordinates(GRID_X_MAX, GRID_Y_MAX)
        validate_grid_coordinates(GRID_X_MIN, GRID_Y_MIN)

    def test_x_too_small(self):
        """Test that x < GRID_X_MIN fails."""
        with pytest.raises(ValueError, match="grid_x must be between"):
            validate_grid_coordinates(0, 15)

    def test_x_too_large(self):
        """Test that x > GRID_X_MAX fails."""
        with pytest.raises(ValueError, match="grid_x must be between"):
            validate_grid_coordinates(GRID_X_MAX + 1, 15)

    def test_y_too_small(self):
        """Test that y < GRID_Y_MIN fails."""
        with pytest.raises(ValueError, match="grid_y must be between"):
            validate_grid_coordinates(20, 0)

    def test_y_too_large(self):
        """Test that y > GRID_Y_MAX fails."""
        with pytest.raises(ValueError, match="grid_y must be between"):
            validate_grid_coordinates(20, GRID_Y_MAX + 1)

    def test_both_invalid(self):
        """Test that both invalid coordinates fail."""
        with pytest.raises(ValueError):
            validate_grid_coordinates(0, 0)


class TestValidateSettlementType:
    """Tests for validate_settlement_type function."""

    def test_valid_settlement_types(self):
        """Test that all valid settlement types pass."""
        for settlement_type in VALID_SETTLEMENT_TYPES:
            validate_settlement_type(settlement_type)

    def test_invalid_settlement_type(self):
        """Test that invalid settlement type fails."""
        with pytest.raises(ValueError, match="Invalid settlement_type"):
            validate_settlement_type("invalid")

    def test_case_sensitive(self):
        """Test that validation is case-sensitive."""
        with pytest.raises(ValueError, match="Invalid settlement_type"):
            validate_settlement_type("City")  # Should be "city"


class TestValidateEntityType:
    """Tests for validate_entity_type function."""

    def test_valid_entity_types(self):
        """Test that all valid entity types pass."""
        for entity_type in VALID_ENTITY_TYPES:
            validate_entity_type(entity_type)

    def test_invalid_entity_type(self):
        """Test that invalid entity type fails."""
        with pytest.raises(ValueError, match="Invalid entity_type"):
            validate_entity_type("invalid")


class TestValidateEventType:
    """Tests for validate_event_type function."""

    def test_valid_event_types(self):
        """Test that all valid event types pass."""
        for event_type in VALID_EVENT_TYPES:
            validate_event_type(event_type)

    def test_invalid_event_type(self):
        """Test that invalid event type fails."""
        with pytest.raises(ValueError, match="Invalid event_type"):
            validate_event_type("invalid")


class TestValidateRouteType:
    """Tests for validate_route_type function."""

    def test_valid_route_types(self):
        """Test that all valid route types pass."""
        for route_type in VALID_ROUTE_TYPES:
            validate_route_type(route_type)

    def test_invalid_route_type(self):
        """Test that invalid route type fails."""
        with pytest.raises(ValueError, match="Invalid route_type"):
            validate_route_type("invalid")


class TestValidateRouteDifficulty:
    """Tests for validate_route_difficulty function."""

    def test_valid_route_difficulties(self):
        """Test that all valid route difficulties pass."""
        for difficulty in VALID_ROUTE_DIFFICULTIES:
            validate_route_difficulty(difficulty)

    def test_invalid_route_difficulty(self):
        """Test that invalid route difficulty fails."""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            validate_route_difficulty("invalid")


class TestValidatePositive:
    """Tests for validate_positive function."""

    def test_positive_integer(self):
        """Test that positive integers pass."""
        validate_positive(1, "test_value")
        validate_positive(100, "test_value")

    def test_positive_float(self):
        """Test that positive floats pass."""
        validate_positive(0.1, "test_value")
        validate_positive(99.9, "test_value")

    def test_zero(self):
        """Test that zero fails."""
        with pytest.raises(ValueError, match="test_value must be positive"):
            validate_positive(0, "test_value")

    def test_negative(self):
        """Test that negative values fail."""
        with pytest.raises(ValueError, match="test_value must be positive"):
            validate_positive(-1, "test_value")


class TestValidateNonNegative:
    """Tests for validate_non_negative function."""

    def test_positive_integer(self):
        """Test that positive integers pass."""
        validate_non_negative(1, "test_value")
        validate_non_negative(100, "test_value")

    def test_positive_float(self):
        """Test that positive floats pass."""
        validate_non_negative(0.1, "test_value")
        validate_non_negative(99.9, "test_value")

    def test_zero(self):
        """Test that zero passes."""
        validate_non_negative(0, "test_value")
        validate_non_negative(0.0, "test_value")

    def test_negative(self):
        """Test that negative values fail."""
        with pytest.raises(ValueError, match="test_value must be non-negative"):
            validate_non_negative(-1, "test_value")
        with pytest.raises(ValueError, match="test_value must be non-negative"):
            validate_non_negative(-0.1, "test_value")


class TestValidationConstants:
    """Tests for validation constants."""

    def test_settlement_types_list(self):
        """Test that VALID_SETTLEMENT_TYPES contains expected types."""
        assert "city" in VALID_SETTLEMENT_TYPES
        assert "town" in VALID_SETTLEMENT_TYPES
        assert "village" in VALID_SETTLEMENT_TYPES
        assert "hamlet" in VALID_SETTLEMENT_TYPES
        assert "outpost" in VALID_SETTLEMENT_TYPES

    def test_entity_types_list(self):
        """Test that VALID_ENTITY_TYPES contains expected types."""
        assert "person" in VALID_ENTITY_TYPES
        assert "organization" in VALID_ENTITY_TYPES
        assert "faction" in VALID_ENTITY_TYPES
        assert "dynasty" in VALID_ENTITY_TYPES
        assert "guild" in VALID_ENTITY_TYPES

    def test_event_types_list(self):
        """Test that VALID_EVENT_TYPES contains expected types."""
        assert "founding" in VALID_EVENT_TYPES
        assert "battle" in VALID_EVENT_TYPES
        assert "treaty" in VALID_EVENT_TYPES
        assert "disaster" in VALID_EVENT_TYPES
        assert "migration" in VALID_EVENT_TYPES

    def test_route_types_list(self):
        """Test that VALID_ROUTE_TYPES contains expected types."""
        assert "road" in VALID_ROUTE_TYPES
        assert "trail" in VALID_ROUTE_TYPES
        assert "river" in VALID_ROUTE_TYPES
        assert "sea" in VALID_ROUTE_TYPES

    def test_route_difficulties_list(self):
        """Test that VALID_ROUTE_DIFFICULTIES contains expected difficulties."""
        assert "easy" in VALID_ROUTE_DIFFICULTIES
        assert "moderate" in VALID_ROUTE_DIFFICULTIES
        assert "hard" in VALID_ROUTE_DIFFICULTIES
        assert "extreme" in VALID_ROUTE_DIFFICULTIES

    def test_grid_bounds(self):
        """Test that grid bounds are sensible."""
        assert GRID_X_MIN == 1
        assert GRID_X_MAX == 40
        assert GRID_Y_MIN == 1
        assert GRID_Y_MAX == 30
        assert GRID_X_MIN < GRID_X_MAX
        assert GRID_Y_MIN < GRID_Y_MAX
