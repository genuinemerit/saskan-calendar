"""
app_timeline.models.route

Route model for connections between settlements.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String

from .base import Base, PrimaryKeyMixin, TemporalBoundsMixin, TimestampMixin


class Route(Base, PrimaryKeyMixin, TemporalBoundsMixin, TimestampMixin):
    """
    Represents a route/connection between two settlements.
    Routes have direction (origin -> destination) but may be bidirectional in practice.
    """

    __tablename__ = "routes"

    # Route endpoints
    origin_settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=False, index=True
    )
    destination_settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=False, index=True
    )

    # Route characteristics
    distance_km = Column(Float, nullable=True)
    difficulty = Column(
        String, nullable=True
    )  # Reference to route_difficulties in config

    # Route type/classification
    route_type = Column(String, nullable=True)  # e.g., "trail", "road", "river", "sea"

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Flexible metadata (terrain notes, hazards, travel time estimates, etc.)
    # Example: {"terrain": "mountain pass", "seasonal_access": "spring-fall", "hazards": ["bandits"]}
    meta_data = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Route(id={self.id}, origin_id={self.origin_settlement_id}, "
            f"dest_id={self.destination_settlement_id}, distance={self.distance_km}km)>"
        )
