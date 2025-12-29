"""
app_timeline.utils

Utility modules for the timeline application.
"""

from .temporal import (
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
from .validation import (
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

__all__ = [
    # Temporal constants
    "PULSES_PER_DAY",
    "DAYS_PER_TURN",
    "DAYS_PER_DECADE",
    "DAYS_PER_CENTURY",
    "DAYS_PER_SHELL",
    # Temporal conversion functions
    "days_to_turns",
    "turns_to_days",
    "days_to_decades",
    "decades_to_days",
    "days_to_centuries",
    "centuries_to_days",
    "days_to_shells",
    "shells_to_days",
    "format_duration",
    "format_lifespan",
    # Validation constants
    "VALID_SETTLEMENT_TYPES",
    "VALID_ENTITY_TYPES",
    "VALID_EVENT_TYPES",
    "VALID_ROUTE_TYPES",
    "VALID_ROUTE_DIFFICULTIES",
    "GRID_X_MIN",
    "GRID_X_MAX",
    "GRID_Y_MIN",
    "GRID_Y_MAX",
    # Validation functions
    "validate_date_range",
    "validate_grid_coordinates",
    "validate_settlement_type",
    "validate_entity_type",
    "validate_event_type",
    "validate_route_type",
    "validate_route_difficulty",
    "validate_positive",
    "validate_non_negative",
]
