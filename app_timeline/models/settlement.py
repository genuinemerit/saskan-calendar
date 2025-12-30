"""
app_timeline.models.settlement

Settlement and SettlementSnapshot models.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import (
    Base,
    MetadataMixin,
    PrimaryKeyMixin,
    TemporalBoundsMixin,
    TimestampMixin,
)


class Settlement(Base, PrimaryKeyMixin, TemporalBoundsMixin, TimestampMixin):
    """
    Represents a settlement (ring town, market town, hamlet, village, camp, etc.)
    in the Saskan Lands timeline.
    """

    __tablename__ = "settlements"

    # Basic attributes
    name = Column(String, nullable=False, unique=True, index=True)
    settlement_type = Column(String, nullable=False, index=True)

    # Geographic location
    # Precise coordinates (in km from origin)
    location_x = Column(Float, nullable=True)
    location_y = Column(Float, nullable=True)

    # Grid-based location (40x30 grid, each cell = 50 sq km)
    # Grid coordinates: x (1-40 columns), y (1-30 rows)
    grid_x = Column(Integer, nullable=True)
    grid_y = Column(Integer, nullable=True)

    # Physical attributes
    area_sq_km = Column(Float, nullable=True)  # Settlement area in square kilometers

    # Administrative relationships
    parent_settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=True, index=True
    )
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True, index=True)

    # Status flags
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_autonomous = Column(Boolean, default=False, nullable=False)

    # Flexible metadata storage (JSON)
    # Can store: cultural notes, species composition estimates, tags, etc.
    meta_data = Column(JSON, nullable=True)

    # Relationships
    parent = relationship(
        "Settlement",
        remote_side="Settlement.id",
        backref="satellites",
        foreign_keys=[parent_settlement_id],
    )
    province = relationship("Province", back_populates="settlements")
    snapshots = relationship(
        "SettlementSnapshot", back_populates="settlement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Settlement(id={self.id}, name='{self.name}', "
            f"type='{self.settlement_type}', is_active={self.is_active})>"
        )


class SettlementSnapshot(Base, PrimaryKeyMixin, TimestampMixin, MetadataMixin):
    """
    Time-series snapshot of a settlement's demographics and characteristics
    at a specific point in the timeline.

    PR-003a: Added snapshot_type and granularity fields for consistency
    with regional/provincial snapshots.
    """

    __tablename__ = "settlement_snapshots"

    # Which settlement this snapshot describes
    settlement_id = Column(
        Integer, ForeignKey("settlements.id"), nullable=False, index=True
    )

    # When in the lore timeline this snapshot represents
    astro_day = Column(Integer, nullable=False, index=True)

    # PR-003a: Provenance and granularity tracking
    snapshot_type = Column(String, nullable=False, default="simulation", index=True)
    granularity = Column(String, nullable=False, default="year", index=True)

    # Population totals
    population_total = Column(Integer, nullable=False)

    # Population breakdown by species (JSON)
    # Example: {"huum": 5000, "sint": 200, "mixed": 50}
    population_by_species = Column(JSON, nullable=True)

    # Population breakdown by habitat (JSON)
    # Example: {"on_ground": 5000, "under_ground": 250}
    population_by_habitat = Column(JSON, nullable=True)

    # Cultural/social composition (JSON)
    # Example: {"language": "Fatuni", "primary_religion": "X", "tribes": ["A", "B"]}
    cultural_composition = Column(JSON, nullable=True)

    # Economic/production data (JSON) - for future use
    # Example: {"primary_industry": "agriculture", "trade_goods": ["grain", "textiles"]}
    economic_data = Column(JSON, nullable=True)

    # Flexible metadata for additional snapshot-specific data
    meta_data = Column(JSON, nullable=True)

    # Relationships
    settlement = relationship("Settlement", back_populates="snapshots")

    def __repr__(self) -> str:
        return (
            f"<SettlementSnapshot(id={self.id}, settlement_id={self.settlement_id}, "
            f"astro_day={self.astro_day}, population={self.population_total})>"
        )
