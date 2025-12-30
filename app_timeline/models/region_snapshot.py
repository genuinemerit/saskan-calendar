"""
app_timeline.models.region_snapshot

RegionSnapshot model for time-series demographic data at regional level.
PR-003a: Macro-scale simulation support.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, MetadataMixin, PrimaryKeyMixin, TimestampMixin


class RegionSnapshot(Base, PrimaryKeyMixin, TimestampMixin, MetadataMixin):
    """
    Time-series demographic snapshot for a region.

    Captures population and demographic data at the regional level for
    macro-scale simulation, particularly useful for pre-settlement eras.

    PR-003a: Supports variable snapshot frequency and interpolation queries.
    """

    __tablename__ = "region_snapshots"

    # Foreign keys
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)

    # Temporal
    astro_day = Column(Integer, nullable=False, index=True)

    # Provenance and granularity tracking (PR-003a)
    snapshot_type = Column(String, nullable=False, default="simulation", index=True)
    granularity = Column(String, nullable=False, default="year", index=True)

    # Core demographic data
    population_total = Column(Integer, nullable=False)

    # Population breakdown by species (JSON)
    # Example: {"huum": 10000, "sint": 2000, "mixed": 500}
    population_by_species = Column(JSON, nullable=True)

    # Population breakdown by habitat (JSON)
    # Example: {"on_ground": 10000, "under_ground": 2500}
    population_by_habitat = Column(JSON, nullable=True)

    # Cultural and economic data (JSON)
    # Example: {"languages": {"Fatuni": 8000, "Juuj": 4500}, ...}
    cultural_composition = Column(JSON, nullable=True)

    # Economic/production data (JSON)
    # Example: {"primary_industries": ["agriculture", "mining"], ...}
    economic_data = Column(JSON, nullable=True)

    # Flexible metadata for additional snapshot-specific data
    # ADR-008: Use MetadataMixin for programmatic access
    meta_data = Column(JSON, nullable=True)

    # Relationships
    region = relationship("Region", back_populates="snapshots")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "population_total >= 0",
            name="check_region_snapshot_population_positive",
        ),
        CheckConstraint(
            "astro_day >= 0", name="check_region_snapshot_astro_day_nonnegative"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<RegionSnapshot(id={self.id}, region_id={self.region_id}, "
            f"astro_day={self.astro_day}, population={self.population_total}, "
            f"type={self.snapshot_type}, granularity={self.granularity})>"
        )
