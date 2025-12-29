"""
app_timeline.services.epoch_service

Service layer for Epoch operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.epoch import Epoch
from .base import BaseService


class EpochService(BaseService[Epoch]):
    """
    Service for managing Epoch records.

    Provides CRUD operations plus epoch-specific queries:
    - Finding epochs containing a specific day
    - Finding overlapping epochs
    - Listing epochs by time range
    """

    def __init__(self):
        """Initialize the epoch service."""
        super().__init__(Epoch)

    def get_epochs_containing_day(self, astro_day: int) -> List[Epoch]:
        """
        Find all epochs that contain a specific day.

        :param astro_day: The day to search for
        :return: List of epochs containing the day
        """
        stmt = select(Epoch).where(
            Epoch.start_astro_day <= astro_day, Epoch.end_astro_day >= astro_day
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_overlapping_epochs(self, epoch_id: int) -> List[Epoch]:
        """
        Find all epochs that overlap with a given epoch.

        :param epoch_id: ID of the epoch to check
        :return: List of overlapping epochs (excluding the epoch itself)
        """
        epoch = self.get_by_id(epoch_id)
        if epoch is None:
            return []

        # Find epochs where ranges overlap
        stmt = (
            select(Epoch)
            .where(
                Epoch.id != epoch_id,
                Epoch.start_astro_day <= epoch.end_astro_day,
                Epoch.end_astro_day >= epoch.start_astro_day,
            )
            .order_by(Epoch.start_astro_day)
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_epochs_in_range(
        self, start_day: int, end_day: int, fully_contained: bool = False
    ) -> List[Epoch]:
        """
        Find epochs within or overlapping a time range.

        :param start_day: Start of the range (inclusive)
        :param end_day: End of the range (inclusive)
        :param fully_contained: If True, only return epochs fully within the range;
                                if False, return epochs that overlap the range
        :return: List of matching epochs
        """
        if fully_contained:
            # Epoch must be fully contained within the range
            stmt = (
                select(Epoch)
                .where(
                    Epoch.start_astro_day >= start_day, Epoch.end_astro_day <= end_day
                )
                .order_by(Epoch.start_astro_day)
            )
        else:
            # Epoch overlaps the range in any way
            stmt = (
                select(Epoch)
                .where(
                    Epoch.start_astro_day <= end_day, Epoch.end_astro_day >= start_day
                )
                .order_by(Epoch.start_astro_day)
            )

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def create_epoch(
        self,
        name: str,
        start_astro_day: int,
        end_astro_day: int,
        description: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Epoch:
        """
        Create a new epoch with validation.

        :param name: Unique name for the epoch
        :param start_astro_day: Start day (inclusive)
        :param end_astro_day: End day (inclusive)
        :param description: Optional description
        :param meta_data: Optional metadata dictionary
        :return: Created epoch
        :raises ValueError: If validation fails
        """
        # Validate time range
        if end_astro_day < start_astro_day:
            raise ValueError(
                f"end_astro_day ({end_astro_day}) must be >= start_astro_day ({start_astro_day})"
            )

        # Check for duplicate name
        existing = self.get_by_name(name)
        if existing is not None:
            raise ValueError(
                f"Epoch with name '{name}' already exists (ID: {existing.id})"
            )

        return self.create(
            name=name,
            start_astro_day=start_astro_day,
            end_astro_day=end_astro_day,
            description=description,
            meta_data=meta_data,
        )
