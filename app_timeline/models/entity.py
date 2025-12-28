"""
app_timeline.models.entity

Entity model for people, organizations, groups, and collectives.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, JSON, String, Text

from .base import Base, PrimaryKeyMixin, TemporalBoundsMixin, TimestampMixin


class Entity(Base, PrimaryKeyMixin, TemporalBoundsMixin, TimestampMixin):
    """
    Represents an entity (person, organization, group, collective) in the timeline.
    Entities can be referenced by events and can have relationships with settlements.
    """

    __tablename__ = "entities"

    # Basic attributes
    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)  # person, organization, group, collective

    # Description/biography
    description = Column(Text, nullable=True)

    # Temporal bounds use founded_astro_day for birth/formation, dissolved_astro_day for death/dissolution
    # These come from TemporalBoundsMixin

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Flexible metadata
    # For persons: {"species": "huum", "birth_place": "Ingar", "roles": ["warrior", "leader"]}
    # For organizations: {"type": "military", "size": "large", "allegiance": "Fatunik"}
    meta_data = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Entity(id={self.id}, name='{self.name}', "
            f"type='{self.entity_type}', is_active={self.is_active})>"
        )
