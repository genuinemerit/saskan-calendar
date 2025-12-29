"""
app_timeline.services.entity_service

Service layer for Entity operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.entity import Entity
from .base import BaseService


class EntityService(BaseService[Entity]):
    """
    Service for managing Entity records.

    Entities are people, organizations, or groups that participate in events.
    Provides CRUD operations plus entity-specific queries.
    """

    def __init__(self):
        """Initialize the entity service."""
        super().__init__(Entity)

    def create_entity(
        self,
        name: str,
        entity_type: str,
        founded_astro_day: Optional[int] = None,
        dissolved_astro_day: Optional[int] = None,
        description: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Entity:
        """
        Create a new entity with validation.

        :param name: Name for the entity (not required to be unique)
        :param entity_type: Type (e.g., 'person', 'organization', 'faction')
        :param founded_astro_day: When the entity came into existence (optional)
        :param dissolved_astro_day: When the entity ceased to exist (if applicable)
        :param description: Optional description
        :param meta_data: Optional metadata dictionary
        :return: Created entity
        :raises ValueError: If validation fails
        """
        # Validate temporal bounds if both provided
        if (
            founded_astro_day is not None
            and dissolved_astro_day is not None
            and dissolved_astro_day < founded_astro_day
        ):
            raise ValueError(
                f"dissolved_astro_day ({dissolved_astro_day}) must be >= founded_astro_day ({founded_astro_day})"
            )

        return self.create(
            name=name,
            entity_type=entity_type,
            founded_astro_day=founded_astro_day,
            dissolved_astro_day=dissolved_astro_day,
            description=description,
            meta_data=meta_data,
        )

    def get_entities_by_type(
        self, entity_type: str, active_only: bool = True
    ) -> List[Entity]:
        """
        Get all entities of a specific type.

        :param entity_type: Entity type to filter by
        :param active_only: If True, only return active entities
        :return: List of entities of the given type
        """
        return self.list_all(
            filters={"entity_type": entity_type},
            active_only=active_only,
            order_by="name",
        )

    def get_entities_alive_at_day(self, astro_day: int) -> List[Entity]:
        """
        Get all entities that existed at a specific day.

        :param astro_day: The day to query
        :return: List of entities that existed at that day
        """
        stmt = (
            select(Entity)
            .where(
                Entity.founded_astro_day <= astro_day,
                (Entity.dissolved_astro_day.is_(None))
                | (Entity.dissolved_astro_day >= astro_day),
            )
            .order_by(Entity.name)
        )

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_entities_in_range(
        self, start_day: int, end_day: int, must_be_alive_entire_range: bool = False
    ) -> List[Entity]:
        """
        Get entities that existed during a time range.

        :param start_day: Start of the range (inclusive)
        :param end_day: End of the range (inclusive)
        :param must_be_alive_entire_range: If True, entity must exist for entire range;
                                            if False, entity just needs to overlap the range
        :return: List of matching entities
        """
        if must_be_alive_entire_range:
            # Entity must exist for the entire range
            stmt = (
                select(Entity)
                .where(
                    Entity.founded_astro_day <= start_day,
                    (Entity.dissolved_astro_day.is_(None))
                    | (Entity.dissolved_astro_day >= end_day),
                )
                .order_by(Entity.name)
            )
        else:
            # Entity just needs to overlap the range
            stmt = (
                select(Entity)
                .where(
                    Entity.founded_astro_day <= end_day,
                    (Entity.dissolved_astro_day.is_(None))
                    | (Entity.dissolved_astro_day >= start_day),
                )
                .order_by(Entity.name)
            )

        result = self.session.execute(stmt)
        return list(result.scalars().all())
