"""
app_timeline.models.event

Event model for timeline events.
"""

from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, JSON, String, Text

from .base import Base, PrimaryKeyMixin, TimestampMixin


class Event(Base, PrimaryKeyMixin, TimestampMixin):
    """
    Represents a historical event in the timeline.
    Events are immutable historical facts - once created, they should not be modified.
    Use is_deprecated flag to mark events as superseded.

    Geographic Association:
    An event must be associated with exactly ONE of: region, province, or settlement.
    The CHECK constraint ensures mutual exclusivity.
    """

    __tablename__ = "events"

    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN region_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN province_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN settlement_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="event_location_exclusivity"
        ),
    )

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
    # Geographic association: exactly one of region_id, province_id, or settlement_id
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, index=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True, index=True)
    settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=True, index=True
    )
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
