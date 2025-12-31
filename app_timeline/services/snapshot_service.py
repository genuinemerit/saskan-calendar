"""
app_timeline.services.snapshot_service

Service layer for SettlementSnapshot operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.settlement import SettlementSnapshot
from .base import BaseService


class SnapshotService(BaseService[SettlementSnapshot]):
    """
    Service for managing SettlementSnapshot records.

    Snapshots capture settlement state (population, resources) at specific points in time.
    Provides CRUD operations plus snapshot-specific queries.
    """

    def __init__(self):
        """Initialize the snapshot service."""
        super().__init__(SettlementSnapshot)

    def create_snapshot(
        self,
        settlement_id: int,
        astro_day: int,
        population_total: int,
        snapshot_type: str = "simulation",
        granularity: str = "year",
        population_by_species: Optional[dict] = None,
        population_by_habitat: Optional[dict] = None,
        cultural_composition: Optional[dict] = None,
        economic_data: Optional[dict] = None,
        meta_data: Optional[dict] = None,
    ) -> SettlementSnapshot:
        """
        Create a new settlement snapshot with validation.

        :param settlement_id: ID of the settlement
        :param astro_day: Day this snapshot represents
        :param population_total: Total population (required)
        :param snapshot_type: Type of snapshot (simulation/historical/estimated)
        :param granularity: Data granularity (year/month/day)
        :param population_by_species: Population breakdown by species
        :param population_by_habitat: Population breakdown by habitat
        :param cultural_composition: Cultural/social composition
        :param economic_data: Economic/production data
        :param meta_data: Optional metadata dictionary
        :return: Created snapshot
        :raises ValueError: If validation fails
        """
        # Validate settlement exists
        from .settlement_service import SettlementService

        with SettlementService() as settlement_service:
            settlement = settlement_service.get_by_id(settlement_id)
            if settlement is None:
                raise ValueError(f"Settlement with ID {settlement_id} does not exist")

        # Check for duplicate snapshot (same settlement + day)
        existing = self.get_snapshot_at_day(settlement_id, astro_day)
        if existing is not None:
            raise ValueError(
                f"Snapshot already exists for settlement {settlement_id} "
                f"at day {astro_day} (ID: {existing.id})"
            )

        return self.create(
            settlement_id=settlement_id,
            astro_day=astro_day,
            population_total=population_total,
            snapshot_type=snapshot_type,
            granularity=granularity,
            population_by_species=population_by_species,
            population_by_habitat=population_by_habitat,
            cultural_composition=cultural_composition,
            economic_data=economic_data,
            meta_data=meta_data,
        )

    def get_snapshots_for_settlement(
        self, settlement_id: int, active_only: bool = True
    ) -> List[SettlementSnapshot]:
        """
        Get all snapshots for a specific settlement, ordered by day.

        :param settlement_id: ID of the settlement
        :param active_only: If True, only return active snapshots
        :return: List of snapshots ordered by astro_day
        """
        return self.list_all(
            filters={"settlement_id": settlement_id},
            active_only=active_only,
            order_by="astro_day",
        )

    def get_snapshot_at_day(
        self, settlement_id: int, astro_day: int
    ) -> Optional[SettlementSnapshot]:
        """
        Get the snapshot for a settlement at a specific day.

        :param settlement_id: ID of the settlement
        :param astro_day: The day to query
        :return: Snapshot or None if not found
        """
        stmt = select(SettlementSnapshot).where(
            SettlementSnapshot.settlement_id == settlement_id,
            SettlementSnapshot.astro_day == astro_day,
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_snapshots_in_range(
        self, settlement_id: int, start_day: int, end_day: int, active_only: bool = True
    ) -> List[SettlementSnapshot]:
        """
        Get snapshots for a settlement within a time range.

        :param settlement_id: ID of the settlement
        :param start_day: Start of the range (inclusive)
        :param end_day: End of the range (inclusive)
        :param active_only: Ignored (snapshots don't have is_active field)
        :return: List of snapshots in the range, ordered by day
        """
        stmt = (
            select(SettlementSnapshot)
            .where(
                SettlementSnapshot.settlement_id == settlement_id,
                SettlementSnapshot.astro_day >= start_day,
                SettlementSnapshot.astro_day <= end_day,
            )
            .order_by(SettlementSnapshot.astro_day)
        )

        # Note: Snapshots don't have is_active field, so active_only is ignored

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_latest_snapshot(
        self, settlement_id: int, before_day: Optional[int] = None
    ) -> Optional[SettlementSnapshot]:
        """
        Get the most recent snapshot for a settlement.

        :param settlement_id: ID of the settlement
        :param before_day: If provided, get latest snapshot before this day
        :return: Latest snapshot or None if none exist
        """
        stmt = (
            select(SettlementSnapshot)
            .where(SettlementSnapshot.settlement_id == settlement_id)
            .order_by(SettlementSnapshot.astro_day.desc())
        )

        if before_day is not None:
            stmt = stmt.where(SettlementSnapshot.astro_day < before_day)

        result = self.session.execute(stmt)
        return result.scalars().first()
