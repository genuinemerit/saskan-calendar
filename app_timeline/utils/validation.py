"""
app_timeline.utils.validation

Validation utilities for timeline data.

Provides reusable validation functions for common constraints:
- Date range validation
- Grid coordinate validation
- Enum validation
- Foreign key existence checks
"""

from __future__ import annotations

from typing import Any, Optional  # noqa F401

# Valid enum values
VALID_SETTLEMENT_TYPES = ["city", "town", "village", "hamlet", "outpost"]
VALID_ENTITY_TYPES = ["person", "organization", "faction", "dynasty", "guild"]
VALID_EVENT_TYPES = [
    "founding",
    "battle",
    "treaty",
    "disaster",
    "migration",
    "cultural",
    "economic",
    "political",
]
VALID_ROUTE_TYPES = ["road", "trail", "river", "sea", "air"]
VALID_ROUTE_DIFFICULTIES = ["easy", "moderate", "hard", "extreme"]

# Grid constraints
GRID_X_MIN = 1
GRID_X_MAX = 40
GRID_Y_MIN = 1
GRID_Y_MAX = 30


def validate_date_range(
    start_day: int, end_day: int, allow_equal: bool = False
) -> None:
    """
    Validate that a date range is valid (start <= end).

    :param start_day: Start day
    :param end_day: End day
    :param allow_equal: If True, allow start_day == end_day
    :raises ValueError: If date range is invalid
    """
    if start_day < 0:
        raise ValueError(f"Start day cannot be negative: {start_day}")

    if end_day < 0:
        raise ValueError(f"End day cannot be negative: {end_day}")

    if allow_equal:
        if start_day > end_day:
            raise ValueError(f"Start day ({start_day}) must be <= end day ({end_day})")
    else:
        if start_day >= end_day:
            raise ValueError(f"Start day ({start_day}) must be < end day ({end_day})")


def validate_grid_coordinates(x: Optional[int], y: Optional[int]) -> None:
    """
    Validate grid coordinates are within valid range.

    :param x: Grid X coordinate (None if not specified)
    :param y: Grid Y coordinate (None if not specified)
    :raises ValueError: If coordinates are out of range
    """
    if x is not None:
        if not (GRID_X_MIN <= x <= GRID_X_MAX):
            raise ValueError(
                f"grid_x must be between {GRID_X_MIN} and {GRID_X_MAX}, got {x}"
            )

    if y is not None:
        if not (GRID_Y_MIN <= y <= GRID_Y_MAX):
            raise ValueError(
                f"grid_y must be between {GRID_Y_MIN} and {GRID_Y_MAX}, got {y}"
            )


def validate_settlement_type(settlement_type: str) -> None:
    """
    Validate settlement type is a valid value.

    :param settlement_type: Settlement type to validate
    :raises ValueError: If settlement type is invalid
    """
    if settlement_type not in VALID_SETTLEMENT_TYPES:
        raise ValueError(
            f"Invalid settlement_type '{settlement_type}'. "
            f"Must be one of: {', '.join(VALID_SETTLEMENT_TYPES)}"
        )


def validate_entity_type(entity_type: str) -> None:
    """
    Validate entity type is a valid value.

    :param entity_type: Entity type to validate
    :raises ValueError: If entity type is invalid
    """
    if entity_type not in VALID_ENTITY_TYPES:
        raise ValueError(
            f"Invalid entity_type '{entity_type}'. "
            f"Must be one of: {', '.join(VALID_ENTITY_TYPES)}"
        )


def validate_event_type(event_type: str) -> None:
    """
    Validate event type is a valid value.

    :param event_type: Event type to validate
    :raises ValueError: If event type is invalid
    """
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event_type '{event_type}'. "
            f"Must be one of: {', '.join(VALID_EVENT_TYPES)}"
        )


def validate_route_type(route_type: str) -> None:
    """
    Validate route type is a valid value.

    :param route_type: Route type to validate
    :raises ValueError: If route type is invalid
    """
    if route_type not in VALID_ROUTE_TYPES:
        raise ValueError(
            f"Invalid route_type '{route_type}'. "
            f"Must be one of: {', '.join(VALID_ROUTE_TYPES)}"
        )


def validate_route_difficulty(difficulty: str) -> None:
    """
    Validate route difficulty is a valid value.

    :param difficulty: Route difficulty to validate
    :raises ValueError: If difficulty is invalid
    """
    if difficulty not in VALID_ROUTE_DIFFICULTIES:
        raise ValueError(
            f"Invalid difficulty '{difficulty}'. "
            f"Must be one of: {', '.join(VALID_ROUTE_DIFFICULTIES)}"
        )


def validate_positive(value: int | float, field_name: str = "value") -> None:
    """
    Validate that a value is positive.

    :param value: Value to validate
    :param field_name: Name of field for error message
    :raises ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{field_name} must be positive, got {value}")


def validate_non_negative(value: int | float, field_name: str = "value") -> None:
    """
    Validate that a value is non-negative (>= 0).

    :param value: Value to validate
    :param field_name: Name of field for error message
    :raises ValueError: If value is negative
    """
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")
