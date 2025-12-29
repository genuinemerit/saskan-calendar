"""
app_timeline.services.route_service

Service layer for Route operations.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from ..models.route import Route
from .base import BaseService


class RouteService(BaseService[Route]):
    """
    Service for managing Route records.

    Routes connect two settlements with distance and travel time information.
    Provides CRUD operations plus route-specific queries.
    """

    def __init__(self):
        """Initialize the route service."""
        super().__init__(Route)

    def create_route(
        self,
        origin_settlement_id: int,
        destination_settlement_id: int,
        distance_km: Optional[float] = None,
        route_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Route:
        """
        Create a new route with validation.

        :param origin_settlement_id: ID of the origin settlement
        :param destination_settlement_id: ID of the destination settlement
        :param distance_km: Distance in kilometers
        :param route_type: Type of route (e.g., 'road', 'trail', 'river')
        :param difficulty: Route difficulty
        :param meta_data: Optional metadata dictionary
        :return: Created route
        :raises ValueError: If validation fails
        """
        # Validate settlements exist
        from .settlement_service import SettlementService

        with SettlementService() as settlement_service:
            origin = settlement_service.get_by_id(origin_settlement_id)
            if origin is None:
                raise ValueError(
                    f"Settlement with ID {origin_settlement_id} does not exist"
                )

            destination = settlement_service.get_by_id(destination_settlement_id)
            if destination is None:
                raise ValueError(
                    f"Settlement with ID {destination_settlement_id} does not exist"
                )

        # Validate settlements are different
        if origin_settlement_id == destination_settlement_id:
            raise ValueError("Route must connect two different settlements")

        # Validate distance is positive if provided
        if distance_km is not None and distance_km <= 0:
            raise ValueError(f"Distance must be positive, got {distance_km}")

        return self.create(
            origin_settlement_id=origin_settlement_id,
            destination_settlement_id=destination_settlement_id,
            distance_km=distance_km,
            route_type=route_type,
            difficulty=difficulty,
            meta_data=meta_data,
        )

    def get_routes_for_settlement(
        self, settlement_id: int, active_only: bool = True
    ) -> List[Route]:
        """
        Get all routes connected to a specific settlement.

        :param settlement_id: ID of the settlement
        :param active_only: If True, only return active routes
        :return: List of routes connected to the settlement
        """
        stmt = select(Route).where(
            (Route.origin_settlement_id == settlement_id)
            | (Route.destination_settlement_id == settlement_id)
        )

        if active_only:
            stmt = stmt.where(Route.is_active == True)

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_route_between_settlements(
        self, origin_id: int, destination_id: int
    ) -> Optional[Route]:
        """
        Find a route between two settlements.

        :param origin_id: ID of the origin settlement
        :param destination_id: ID of the destination settlement
        :return: Route connecting the settlements or None if not found
        """
        stmt = select(Route).where(
            (Route.origin_settlement_id == origin_id)
            & (Route.destination_settlement_id == destination_id)
        )

        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_routes_by_type(
        self, route_type: str, active_only: bool = True
    ) -> List[Route]:
        """
        Get all routes of a specific type.

        :param route_type: Route type to filter by
        :param active_only: If True, only return active routes
        :return: List of routes of the given type
        """
        return self.list_all(
            filters={"route_type": route_type}, active_only=active_only, order_by="name"
        )
