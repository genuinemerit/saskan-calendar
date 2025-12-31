"""
app_timeline.services.province_service

Service layer for Province operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.province import Province
from .base import BaseService


class ProvinceService(BaseService[Province]):
    """
    Service for managing Province records.

    Provinces belong to regions and contain settlements.
    Provides CRUD operations plus province-specific queries.
    """

    def __init__(self):
        """Initialize the province service."""
        super().__init__(Province)

    def create_province(
        self,
        name: str,
        region_id: Optional[int] = None,
        description: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Province:
        """
        Create a new province with validation.

        :param name: Unique name for the province
        :param region_id: Optional ID of the parent region
        :param description: Optional description of the province
        :param meta_data: Optional metadata dictionary
        :return: Created province
        :raises ValueError: If validation fails
        """
        # Check for duplicate name
        existing = self.get_by_name(name)
        if existing is not None:
            raise ValueError(
                f"Province with name '{name}' already exists (ID: {existing.id})"
            )

        # Validate region exists if provided
        if region_id is not None:
            from .region_service import RegionService

            with RegionService() as region_service:
                region = region_service.get_by_id(region_id)
                if region is None:
                    raise ValueError(f"Region with ID {region_id} does not exist")

        return self.create(
            name=name, region_id=region_id, description=description, meta_data=meta_data
        )

    def get_provinces_by_region(
        self, region_id: int, active_only: bool = True
    ) -> List[Province]:
        """
        Get all provinces in a specific region.

        :param region_id: ID of the region
        :param active_only: If True, only return active provinces
        :return: List of provinces in the region
        """
        return self.list_all(
            filters={"region_id": region_id}, active_only=active_only, order_by="name"
        )
