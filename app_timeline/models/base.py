"""
app_timeline.models.base

Base classes and mixins for SQLAlchemy models.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base

# Create the declarative base for all models
Base = declarative_base()


class TimestampMixin:
    """
    Mixin that adds created_at timestamp to models.
    Records when the database record was created (system time, not lore time).
    """

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class PrimaryKeyMixin:
    """Mixin that adds an integer primary key id column."""

    id = Column(Integer, primary_key=True, autoincrement=True)


class TemporalBoundsMixin:
    """
    Mixin for entities that exist within temporal bounds in the lore timeline.
    Uses astro_day as the unit of time.
    """

    founded_astro_day = Column(Integer, nullable=False, index=True)
    dissolved_astro_day = Column(Integer, nullable=True, index=True)
