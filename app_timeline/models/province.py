"""
app_timeline.models.province

Province and Region models.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .base import (
    Base,
    DescriptionMixin,
    MetadataMixin,
    PrimaryKeyMixin,
    TemporalBoundsMixin,
    TimestampMixin,
)


class Region(
    Base,
    PrimaryKeyMixin,
    TemporalBoundsMixin,
    TimestampMixin,
    DescriptionMixin,
    MetadataMixin,
):
    """
    Represents a geographic region that binds together multiple provinces.
    Regions are higher-level administrative/geographic groupings.
    """

    __tablename__ = "regions"

    # Basic attributes
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)  # ADR-008

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Flexible metadata (geographic features, cultural notes, etc.)
    # ADR-008: Use DescriptionMixin/MetadataMixin for programmatic access
    meta_data = Column(JSON, nullable=True)

    # Relationships
    provinces = relationship(
        "Province", back_populates="region", cascade="all, delete-orphan"
    )
    snapshots = relationship("RegionSnapshot", back_populates="region")

    def __repr__(self) -> str:
        return f"<Region(id={self.id}, name='{self.name}', is_active={self.is_active})>"


class Province(
    Base,
    PrimaryKeyMixin,
    TemporalBoundsMixin,
    TimestampMixin,
    DescriptionMixin,
    MetadataMixin,
):
    """
    Represents a province in the Saskan Lands.
    Usually centered around a single Ring Town (with exceptions).
    """

    __tablename__ = "provinces"

    # Basic attributes
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)  # ADR-008

    # Administrative relationships
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, index=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Flexible metadata (borders, capital settlement, cultural notes, etc.)
    # Example: {"capital": "Ingar", "ring_towns": ["Ingar", "Talmar"]}
    # ADR-008: Use DescriptionMixin/MetadataMixin for programmatic access
    meta_data = Column(JSON, nullable=True)

    # Relationships
    region = relationship("Region", back_populates="provinces")
    settlements = relationship("Settlement", back_populates="province")
    snapshots = relationship("ProvinceSnapshot", back_populates="province")

    def __repr__(self) -> str:
        return (
            f"<Province(id={self.id}, name='{self.name}', is_active={self.is_active})>"
        )
