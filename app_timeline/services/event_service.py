"""
app_timeline.services.event_service

Service layer for Event operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.event import Event
from .base import BaseService


class EventService(BaseService[Event]):
    """
    Service for managing Event records.

    Events are occurrences at specific times, optionally involving entities and settlements.
    Provides CRUD operations plus event-specific queries.
    """

    def __init__(self):
        """Initialize the event service."""
        super().__init__(Event)

    def create_event(
        self,
        title: str,
        event_type: str,
        astro_day: int,
        region_id: Optional[int] = None,
        province_id: Optional[int] = None,
        settlement_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Event:
        """
        Create a new event with validation.

        An event must be associated with exactly ONE of: region, province, or settlement.

        :param title: Title for the event
        :param event_type: Type (e.g., 'battle', 'founding', 'treaty')
        :param astro_day: When the event occurred
        :param region_id: Optional region where event occurred
        :param province_id: Optional province where event occurred
        :param settlement_id: Optional settlement where event occurred
        :param entity_id: Optional entity involved in the event
        :param description: Optional description
        :param meta_data: Optional metadata dictionary
        :return: Created event
        :raises ValueError: If validation fails
        """
        # Validate exactly one geographic association
        location_count = sum([
            region_id is not None,
            province_id is not None,
            settlement_id is not None
        ])
        if location_count != 1:
            raise ValueError(
                "Event must be associated with exactly ONE of: region, province, or settlement"
            )

        # Validate region if provided
        if region_id is not None:
            from .region_service import RegionService

            with RegionService() as region_service:
                region = region_service.get_by_id(region_id)
                if region is None:
                    raise ValueError(f"Region with ID {region_id} does not exist")

        # Validate province if provided
        if province_id is not None:
            from .province_service import ProvinceService

            with ProvinceService() as province_service:
                province = province_service.get_by_id(province_id)
                if province is None:
                    raise ValueError(f"Province with ID {province_id} does not exist")

        # Validate settlement if provided
        if settlement_id is not None:
            from .settlement_service import SettlementService

            with SettlementService() as settlement_service:
                settlement = settlement_service.get_by_id(settlement_id)
                if settlement is None:
                    raise ValueError(
                        f"Settlement with ID {settlement_id} does not exist"
                    )

        # Validate entity if provided
        if entity_id is not None:
            from .entity_service import EntityService

            with EntityService() as entity_service:
                entity = entity_service.get_by_id(entity_id)
                if entity is None:
                    raise ValueError(f"Entity with ID {entity_id} does not exist")

        return self.create(
            title=title,
            event_type=event_type,
            astro_day=astro_day,
            region_id=region_id,
            province_id=province_id,
            settlement_id=settlement_id,
            entity_id=entity_id,
            description=description,
            meta_data=meta_data,
        )

    def get_events_by_type(
        self, event_type: str, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events of a specific type.

        :param event_type: Event type to filter by
        :param active_only: If True, only return non-deprecated events
        :return: List of events of the given type
        """
        stmt = (
            select(Event)
            .where(Event.event_type == event_type)
            .order_by(Event.astro_day)
        )
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_for_region(
        self, region_id: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events that occurred at a specific region.

        :param region_id: ID of the region
        :param active_only: If True, only return non-deprecated events
        :return: List of events at the region
        """
        stmt = (
            select(Event)
            .where(Event.region_id == region_id)
            .order_by(Event.astro_day)
        )
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_for_province(
        self, province_id: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events that occurred at a specific province.

        :param province_id: ID of the province
        :param active_only: If True, only return non-deprecated events
        :return: List of events at the province
        """
        stmt = (
            select(Event)
            .where(Event.province_id == province_id)
            .order_by(Event.astro_day)
        )
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_for_settlement(
        self, settlement_id: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events that occurred at a specific settlement.

        :param settlement_id: ID of the settlement
        :param active_only: If True, only return non-deprecated events
        :return: List of events at the settlement
        """
        stmt = (
            select(Event)
            .where(Event.settlement_id == settlement_id)
            .order_by(Event.astro_day)
        )
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_for_entity(
        self, entity_id: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events involving a specific entity.

        :param entity_id: ID of the entity
        :param active_only: If True, only return non-deprecated events
        :return: List of events involving the entity
        """
        stmt = (
            select(Event).where(Event.entity_id == entity_id).order_by(Event.astro_day)
        )
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_at_day(
        self, astro_day: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events that occurred on a specific day.

        :param astro_day: The day to query
        :param active_only: If True, only return non-deprecated events
        :return: List of events on that day
        """
        stmt = select(Event).where(Event.astro_day == astro_day).order_by(Event.title)
        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_in_range(
        self, start_day: int, end_day: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get events within a time range.

        :param start_day: Start of the range (inclusive)
        :param end_day: End of the range (inclusive)
        :param active_only: If True, only return active events
        :return: List of events in the range
        """
        stmt = (
            select(Event)
            .where(Event.astro_day >= start_day, Event.astro_day <= end_day)
            .order_by(Event.astro_day, Event.title)
        )

        if active_only:
            stmt = stmt.where(Event.is_deprecated == False)

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_events_in_epoch(
        self, epoch_id: int, active_only: bool = True
    ) -> List[Event]:
        """
        Get all events that occurred during a specific epoch.

        :param epoch_id: ID of the epoch
        :param active_only: If True, only return active events
        :return: List of events during the epoch
        """
        from .epoch_service import EpochService

        with EpochService() as epoch_service:
            epoch = epoch_service.get_by_id(epoch_id)
            if epoch is None:
                raise ValueError(f"Epoch with ID {epoch_id} does not exist")

            return self.get_events_in_range(
                epoch.start_astro_day, epoch.end_astro_day, active_only=active_only
            )
