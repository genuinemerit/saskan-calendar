"""
app_timeline.services.region_snapshot_service

Service layer for RegionSnapshot operations with interpolation support.
PR-003a: Macro-scale simulation infrastructure.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select

from ..models.region_snapshot import RegionSnapshot
from .base import BaseService


class RegionSnapshotService(BaseService[RegionSnapshot]):
    """
    Service for managing RegionSnapshot records.

    Provides CRUD operations plus snapshot-specific queries including:
    - Temporal queries (get snapshot at specific day)
    - Filtering by snapshot type and granularity
    - Interpolation between sparse snapshots
    - Nearest snapshot queries

    PR-003a: Supports macro-scale demographic simulation.
    """

    def __init__(self):
        """Initialize the region snapshot service."""
        super().__init__(RegionSnapshot)

    def create_snapshot(
        self,
        region_id: int,
        astro_day: int,
        population_total: int,
        snapshot_type: str = "simulation",
        granularity: str = "year",
        population_by_species: Optional[dict] = None,
        population_by_habitat: Optional[dict] = None,
        cultural_composition: Optional[dict] = None,
        economic_data: Optional[dict] = None,
        meta_data: Optional[dict] = None,
    ) -> RegionSnapshot:
        """
        Create a new region snapshot with validation.

        :param region_id: ID of the region
        :param astro_day: Day this snapshot represents
        :param population_total: Total population (required)
        :param snapshot_type: Type of snapshot (census, simulation, estimate, etc.)
        :param granularity: Temporal granularity (year, decade, century, etc.)
        :param population_by_species: Population breakdown by species
        :param population_by_habitat: Population breakdown by habitat
        :param cultural_composition: Cultural/social composition
        :param economic_data: Economic/production data
        :param meta_data: Optional metadata dictionary
        :return: Created snapshot
        :raises ValueError: If validation fails
        """
        # Validate region exists
        from .region_service import RegionService

        with RegionService() as region_service:
            region = region_service.get_by_id(region_id)
            if region is None:
                raise ValueError(f"Region with ID {region_id} does not exist")

        # Validate astro_day and population
        if astro_day < 0:
            raise ValueError(f"astro_day must be >= 0, got {astro_day}")
        if population_total < 0:
            raise ValueError(f"population_total must be >= 0, got {population_total}")

        # Check for duplicate snapshot (same region + day)
        existing = self.get_snapshot_at_day(region_id, astro_day)
        if existing is not None:
            raise ValueError(
                f"Snapshot already exists for region {region_id} "
                f"at day {astro_day} (ID: {existing.id})"
            )

        return self.create(
            region_id=region_id,
            astro_day=astro_day,
            snapshot_type=snapshot_type,
            granularity=granularity,
            population_total=population_total,
            population_by_species=population_by_species,
            population_by_habitat=population_by_habitat,
            cultural_composition=cultural_composition,
            economic_data=economic_data,
            meta_data=meta_data,
        )

    def get_snapshots_for_region(
        self,
        region_id: int,
        start_day: Optional[int] = None,
        end_day: Optional[int] = None,
        snapshot_type: Optional[str] = None,
        granularity: Optional[str] = None,
    ) -> List[RegionSnapshot]:
        """
        Get all snapshots for a specific region, ordered by day.

        :param region_id: ID of the region
        :param start_day: Optional start day filter
        :param end_day: Optional end day filter
        :param snapshot_type: Optional filter by snapshot type
        :param granularity: Optional filter by granularity
        :return: List of snapshots ordered by astro_day
        """
        stmt = select(RegionSnapshot).where(RegionSnapshot.region_id == region_id)

        if start_day is not None:
            stmt = stmt.where(RegionSnapshot.astro_day >= start_day)
        if end_day is not None:
            stmt = stmt.where(RegionSnapshot.astro_day <= end_day)
        if snapshot_type is not None:
            stmt = stmt.where(RegionSnapshot.snapshot_type == snapshot_type)
        if granularity is not None:
            stmt = stmt.where(RegionSnapshot.granularity == granularity)

        stmt = stmt.order_by(RegionSnapshot.astro_day)

        return list(self.session.execute(stmt).scalars().all())

    def get_snapshot_at_day(
        self, region_id: int, astro_day: int
    ) -> Optional[RegionSnapshot]:
        """
        Get exact snapshot at a specific day for a region.

        :param region_id: ID of the region
        :param astro_day: Day to retrieve
        :return: Snapshot if exists, None otherwise
        """
        stmt = select(RegionSnapshot).where(
            RegionSnapshot.region_id == region_id,
            RegionSnapshot.astro_day == astro_day,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_nearest_snapshot(
        self, region_id: int, astro_day: int, before: bool = True
    ) -> Optional[RegionSnapshot]:
        """
        Get nearest snapshot to a given day.

        :param region_id: ID of the region
        :param astro_day: Target day
        :param before: If True, find nearest before target; if False, find nearest after
        :return: Nearest snapshot or None
        """
        stmt = select(RegionSnapshot).where(RegionSnapshot.region_id == region_id)

        if before:
            stmt = stmt.where(RegionSnapshot.astro_day <= astro_day)
            stmt = stmt.order_by(RegionSnapshot.astro_day.desc())
        else:
            stmt = stmt.where(RegionSnapshot.astro_day >= astro_day)
            stmt = stmt.order_by(RegionSnapshot.astro_day.asc())

        return self.session.execute(stmt).scalars().first()

    def get_interpolated(
        self, region_id: int, astro_day: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get interpolated snapshot data for a given day.

        Returns a dictionary with interpolated values, not a RegionSnapshot object.
        Per PR-003a design:
        - Linear interpolation for population_total
        - Linear interpolation per component for species/habitat breakdowns
        - Use nearest snapshot for JSON fields (cultural_composition, economic_data)

        :param region_id: ID of the region
        :param astro_day: Target day for interpolation
        :return: Dict with interpolated data, or None if no data available
        """
        # Get nearest snapshots before and after
        before = self.get_nearest_snapshot(region_id, astro_day, before=True)
        after = self.get_nearest_snapshot(region_id, astro_day, before=False)

        # Edge cases
        if not before and not after:
            return None  # No data available
        if not before:
            return self._snapshot_to_dict(after)  # Before first snapshot
        if not after:
            return self._snapshot_to_dict(before)  # After last snapshot
        if before.id == after.id:
            return self._snapshot_to_dict(before)  # Exact match

        # Linear interpolation
        t = (astro_day - before.astro_day) / (after.astro_day - before.astro_day)

        interpolated = {
            "region_id": region_id,
            "astro_day": astro_day,
            "snapshot_type": "interpolated",
            "granularity": before.granularity,
            "population_total": int(
                before.population_total
                + t * (after.population_total - before.population_total)
            ),
            "interpolation_info": {
                "before_day": before.astro_day,
                "after_day": after.astro_day,
                "before_id": before.id,
                "after_id": after.id,
                "interpolation_factor": t,
            },
        }

        # Interpolate species breakdown if both have it
        if before.population_by_species and after.population_by_species:
            interpolated["population_by_species"] = self._interpolate_dict(
                before.population_by_species, after.population_by_species, t
            )
        else:
            interpolated["population_by_species"] = before.population_by_species

        # Interpolate habitat breakdown if both have it
        if before.population_by_habitat and after.population_by_habitat:
            interpolated["population_by_habitat"] = self._interpolate_dict(
                before.population_by_habitat, after.population_by_habitat, t
            )
        else:
            interpolated["population_by_habitat"] = before.population_by_habitat

        # For JSON fields, use nearest (before) per PR-003a design
        interpolated["cultural_composition"] = before.cultural_composition
        interpolated["economic_data"] = before.economic_data
        interpolated["meta_data"] = before.meta_data

        return interpolated

    # Helper methods

    def _snapshot_to_dict(self, snapshot: RegionSnapshot) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "id": snapshot.id,
            "region_id": snapshot.region_id,
            "astro_day": snapshot.astro_day,
            "snapshot_type": snapshot.snapshot_type,
            "granularity": snapshot.granularity,
            "population_total": snapshot.population_total,
            "population_by_species": snapshot.population_by_species,
            "population_by_habitat": snapshot.population_by_habitat,
            "cultural_composition": snapshot.cultural_composition,
            "economic_data": snapshot.economic_data,
            "meta_data": snapshot.meta_data,
        }

    def _interpolate_dict(
        self, dict_before: Dict[str, int], dict_after: Dict[str, int], t: float
    ) -> Dict[str, int]:
        """
        Linearly interpolate between two dicts with numeric values.

        :param dict_before: Dictionary with values at earlier time
        :param dict_after: Dictionary with values at later time
        :param t: Interpolation factor (0.0 = before, 1.0 = after)
        :return: Interpolated dictionary
        """
        result = {}
        all_keys = set(dict_before.keys()) | set(dict_after.keys())

        for key in all_keys:
            val_before = dict_before.get(key, 0)
            val_after = dict_after.get(key, 0)
            result[key] = int(val_before + t * (val_after - val_before))

        return result
