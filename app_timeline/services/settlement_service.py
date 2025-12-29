"""
app_timeline.services.settlement_service

Service layer for Settlement operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.settlement import Settlement
from .base import BaseService


class SettlementService(BaseService[Settlement]):
    """
    Service for managing Settlement records.

    Settlements are located within provinces and can have snapshots over time.
    Provides CRUD operations plus settlement-specific queries.
    """

    def __init__(self):
        """Initialize the settlement service."""
        super().__init__(Settlement)

    def create_settlement(
        self,
        name: str,
        province_id: Optional[int],
        settlement_type: str,
        location_x: Optional[float] = None,
        location_y: Optional[float] = None,
        grid_x: Optional[int] = None,
        grid_y: Optional[int] = None,
        area_sq_km: Optional[float] = None,
        meta_data: Optional[dict] = None,
    ) -> Settlement:
        """
        Create a new settlement with validation.

        :param name: Unique name for the settlement
        :param province_id: Optional ID of the parent province
        :param settlement_type: Type (e.g., 'city', 'town', 'village')
        :param location_x: Precise X coordinate in km
        :param location_y: Precise Y coordinate in km
        :param grid_x: Grid column (1-40)
        :param grid_y: Grid row (1-30)
        :param area_sq_km: Settlement area in square kilometers
        :param meta_data: Optional metadata dictionary (can include description, etc.)
        :return: Created settlement
        :raises ValueError: If validation fails
        """
        # Check for duplicate name
        existing = self.get_by_name(name)
        if existing is not None:
            raise ValueError(
                f"Settlement with name '{name}' already exists (ID: {existing.id})"
            )

        # Validate province exists if provided
        if province_id is not None:
            from .province_service import ProvinceService

            with ProvinceService() as province_service:
                province = province_service.get_by_id(province_id)
                if province is None:
                    raise ValueError(f"Province with ID {province_id} does not exist")

        # Validate grid coordinates if provided
        if grid_x is not None and not (1 <= grid_x <= 40):
            raise ValueError(f"grid_x must be between 1 and 40, got {grid_x}")
        if grid_y is not None and not (1 <= grid_y <= 30):
            raise ValueError(f"grid_y must be between 1 and 30, got {grid_y}")

        return self.create(
            name=name,
            province_id=province_id,
            settlement_type=settlement_type,
            location_x=location_x,
            location_y=location_y,
            grid_x=grid_x,
            grid_y=grid_y,
            area_sq_km=area_sq_km,
            meta_data=meta_data,
        )

    def get_settlements_by_province(
        self, province_id: int, active_only: bool = True
    ) -> List[Settlement]:
        """
        Get all settlements in a specific province.

        :param province_id: ID of the province
        :param active_only: If True, only return active settlements
        :return: List of settlements in the province
        """
        return self.list_all(
            filters={"province_id": province_id},
            active_only=active_only,
            order_by="name",
        )

    def get_settlements_by_type(
        self, settlement_type: str, active_only: bool = True
    ) -> List[Settlement]:
        """
        Get all settlements of a specific type.

        :param settlement_type: Settlement type to filter by
        :param active_only: If True, only return active settlements
        :return: List of settlements of the given type
        """
        return self.list_all(
            filters={"settlement_type": settlement_type},
            active_only=active_only,
            order_by="name",
        )

    def get_settlements_in_grid_area(
        self, min_x: int, max_x: int, min_y: int, max_y: int, active_only: bool = True
    ) -> List[Settlement]:
        """
        Get settlements within a grid area.

        :param min_x: Minimum grid X (1-40)
        :param max_x: Maximum grid X (1-40)
        :param min_y: Minimum grid Y (1-30)
        :param max_y: Maximum grid Y (1-30)
        :param active_only: If True, only return active settlements
        :return: List of settlements in the grid area
        """
        stmt = select(Settlement).where(
            Settlement.grid_x.isnot(None),
            Settlement.grid_y.isnot(None),
            Settlement.grid_x >= min_x,
            Settlement.grid_x <= max_x,
            Settlement.grid_y >= min_y,
            Settlement.grid_y <= max_y,
        )

        if active_only:
            stmt = stmt.where(Settlement.is_active == True)

        stmt = stmt.order_by(Settlement.name)

        result = self.session.execute(stmt)
        return list(result.scalars().all())
