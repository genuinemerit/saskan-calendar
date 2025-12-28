"""
app_timeline.db.schema

Schema management utilities for creating, dropping, and inspecting database tables.
"""

from __future__ import annotations

from typing import Dict, List

from sqlalchemy import inspect

from ..models import Base
from .connection import get_engine, get_session


def create_all_tables() -> None:
    """
    Create all tables defined in the models.
    This is idempotent - existing tables will not be affected.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_all_tables() -> None:
    """
    Drop all tables defined in the models.
    WARNING: This will delete all data!
    """
    engine = get_engine()
    Base.metadata.drop_all(engine)


def get_table_info() -> Dict[str, Dict]:
    """
    Get information about all tables in the database.

    :return: Dictionary with table names as keys and info as values
    """
    engine = get_engine()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    table_info = {}
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        table_info[table_name] = {
            "columns": [col["name"] for col in columns],
            "column_count": len(columns),
        }

    return table_info


def get_table_row_counts() -> Dict[str, int]:
    """
    Get row counts for all tables.

    :return: Dictionary with table names as keys and row counts as values
    """
    from ..models import (
        Entity,
        Event,
        Province,
        Region,
        Route,
        Settlement,
        SettlementSnapshot,
    )

    session = get_session()
    counts = {}

    try:
        counts["regions"] = session.query(Region).count()
        counts["provinces"] = session.query(Province).count()
        counts["settlements"] = session.query(Settlement).count()
        counts["settlement_snapshots"] = session.query(SettlementSnapshot).count()
        counts["routes"] = session.query(Route).count()
        counts["entities"] = session.query(Entity).count()
        counts["events"] = session.query(Event).count()
    finally:
        session.close()

    return counts


def validate_schema() -> List[str]:
    """
    Validate the database schema.
    Returns a list of validation messages (empty if all is well).

    :return: List of validation messages/warnings
    """
    messages = []
    engine = get_engine()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    expected_tables = {
        "regions",
        "provinces",
        "settlements",
        "settlement_snapshots",
        "routes",
        "entities",
        "events",
    }

    # Check for missing tables
    missing = expected_tables - set(table_names)
    if missing:
        messages.append(f"Missing tables: {', '.join(sorted(missing))}")

    # Check for unexpected tables
    unexpected = set(table_names) - expected_tables
    if unexpected:
        messages.append(f"Unexpected tables: {', '.join(sorted(unexpected))}")

    if not messages:
        messages.append("Schema validation passed - all expected tables present.")

    return messages
