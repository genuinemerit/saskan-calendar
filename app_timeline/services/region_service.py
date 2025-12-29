"""
app_timeline.services.region_service

Service layer for Region operations.
"""

from __future__ import annotations

from typing import Optional

from ..models.province import Region
from .base import BaseService


class RegionService(BaseService[Region]):
    """
    Service for managing Region records.

    Regions are top-level geographic areas that contain provinces.
    Provides CRUD operations for region management.
    """

    def __init__(self):
        """Initialize the region service."""
        super().__init__(Region)

    def create_region(self, name: str, meta_data: Optional[dict] = None) -> Region:
        """
        Create a new region with validation.

        :param name: Unique name for the region
        :param meta_data: Optional metadata dictionary (can include description, etc.)
        :return: Created region
        :raises ValueError: If validation fails
        """
        # Check for duplicate name
        existing = self.get_by_name(name)
        if existing is not None:
            raise ValueError(
                f"Region with name '{name}' already exists (ID: {existing.id})"
            )

        return self.create(name=name, meta_data=meta_data)

    def get_active_regions(self):
        """
        Get all active regions, ordered by name.

        :return: List of active regions
        """
        return self.list_all(active_only=True, order_by="name")
