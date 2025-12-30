"""
app_timeline.models.epoch

Epoch model for named time periods in the timeline.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import JSON

from .base import Base, DescriptionMixin, PrimaryKeyMixin, TimestampMixin


class Epoch(Base, PrimaryKeyMixin, TimestampMixin, DescriptionMixin):
    """
    Named time periods for organizing timeline events.

    Epochs can overlap and multiple epochs can cover the same time range,
    allowing for different perspectives on history (political, cultural, etc.)

    Example epochs:
    - "Early Recovery Era" (Day 0 - Day 500)
    - "Fatunik Expansion" (Day 100 - Day 800)
    - "First Migration Wave" (Day 150 - Day 400)
    """

    __tablename__ = "epochs"

    # Core fields
    name = Column(String, nullable=False, unique=True, index=True)
    start_astro_day = Column(Integer, nullable=False, index=True)
    end_astro_day = Column(Integer, nullable=False, index=True)
    description = Column(
        Text, nullable=True
    )  # ADR-008: Use DescriptionMixin for programmatic access

    # Flexible metadata for cultural significance, sources, etc.
    # Note: Epoch does not use MetadataMixin (per PR-003a design doc)
    meta_data = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Epoch(id={self.id}, name='{self.name}', "
            f"range=[{self.start_astro_day}, {self.end_astro_day}])>"
        )

    @property
    def duration(self) -> int:
        """Calculate epoch duration in days."""
        return self.end_astro_day - self.start_astro_day

    def contains_day(self, astro_day: int) -> bool:
        """Check if a given day falls within this epoch."""
        return self.start_astro_day <= astro_day <= self.end_astro_day

    def overlaps_with(self, other: "Epoch") -> bool:
        """Check if this epoch overlaps with another epoch."""
        return not (
            self.end_astro_day < other.start_astro_day
            or self.start_astro_day > other.end_astro_day
        )
