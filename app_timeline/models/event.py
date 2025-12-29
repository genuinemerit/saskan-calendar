"""
app_timeline.models.event

Event model for timeline events.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text

from .base import Base, PrimaryKeyMixin, TimestampMixin


class Event(Base, PrimaryKeyMixin, TimestampMixin):
    """
    Represents a historical event in the timeline.
    Events are immutable historical facts - once created, they should not be modified.
    Use is_deprecated flag to mark events as superseded.
    """

    __tablename__ = "events"

    # When the event occurred (lore time)
    astro_day = Column(Integer, nullable=False, index=True)

    # Event classification
    event_type = Column(String, nullable=False, index=True)

    # Event title/summary
    title = Column(String, nullable=False)

    # Detailed description
    description = Column(Text, nullable=True)

    # Geographic location (optional)
    location_x = Column(Integer, nullable=True)
    location_y = Column(Integer, nullable=True)

    # Related entities (foreign keys)
    settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=True, index=True
    )
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)

    # Deprecation/correction handling
    is_deprecated = Column(Boolean, default=False, nullable=False, index=True)
    superseded_by_id = Column(Integer, ForeignKey("events.id"), nullable=True)

    # Flexible metadata (tags, sources, narrative notes, etc.)
    # Example: {"tags": ["battle", "political"], "source": "Chapter 12", "importance": "high"}
    meta_data = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Event(id={self.id}, astro_day={self.astro_day}, "
            f"type='{self.event_type}', title='{self.title}')>"
        )
