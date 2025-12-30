"""
app_timeline.models.base

Base classes and mixins for SQLAlchemy models.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base

# Create the declarative base for all models
Base = declarative_base()


class TimestampMixin:
    """
    Mixin that adds created_at timestamp to models.
    Records when the database record was created (system time, not lore time).
    """

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class PrimaryKeyMixin:
    """Mixin that adds an integer primary key id column."""

    id = Column(Integer, primary_key=True, autoincrement=True)


class TemporalBoundsMixin:
    """
    Mixin for entities that exist within temporal bounds in the lore timeline.
    Uses astro_day as the unit of time.

    Both fields are nullable to allow for cases where temporal bounds are unknown
    or not applicable (e.g., geographic regions).
    """

    founded_astro_day = Column(Integer, nullable=True, index=True)
    dissolved_astro_day = Column(Integer, nullable=True, index=True)


class DescriptionMixin:
    """
    Mixin for description field management (ADR-008).

    Provides methods for updating, clearing, and checking description fields.
    Description fields are TEXT columns for human-readable summaries and notes.
    """

    def update_description(self, text: Optional[str]) -> Optional[str]:
        """
        Update description text.

        Args:
            text: New description text, or None to clear

        Returns:
            Updated description
        """
        self.description = text
        return self.description

    def clear_description(self) -> None:
        """Remove description (set to NULL)."""
        self.description = None

    def has_description(self) -> bool:
        """Check if entity has a description."""
        return bool(self.description)


class MetadataMixin:
    """
    Mixin for metadata field management with flat structure validation (ADR-008).

    Enforces flat key-value structure for metadata (no nesting/arrays).
    Provides operations: merge, remove, replace, clear.
    """

    @staticmethod
    def _validate_flat_structure(data: Dict[str, Any]) -> None:
        """
        Validate that metadata is a flat key-value structure (no nesting/arrays).

        Args:
            data: Dictionary to validate

        Raises:
            ValueError: If data contains nested objects, arrays, or invalid types
        """
        for key, value in data.items():
            if isinstance(value, dict):
                raise ValueError(
                    f"Nested objects not allowed in metadata. Key '{key}' contains object."
                )
            if isinstance(value, (list, tuple)):
                raise ValueError(
                    f"Arrays not allowed in metadata. Key '{key}' contains array."
                )
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise ValueError(
                    f"Invalid value type for key '{key}': {type(value).__name__}. "
                    f"Only str, int, float, bool, None allowed."
                )

    def update_metadata(
        self, updates: Dict[str, Any], mode: str = "merge"
    ) -> Dict[str, Any]:
        """
        Update metadata with specified mode ('merge' or 'replace').

        Args:
            updates: Dictionary of key-value pairs to apply
            mode: 'merge' (default) or 'replace'

        Returns:
            Updated metadata dictionary

        Raises:
            ValueError: If mode is invalid or updates contain nested/complex structures
        """
        if mode not in ("merge", "replace"):
            raise ValueError(f"Invalid mode: {mode}. Use 'merge' or 'replace'")

        self._validate_flat_structure(updates)

        if mode == "replace":
            self.meta_data = updates
        else:  # merge
            current = self.meta_data or {}
            current.update(updates)
            self.meta_data = current

        return self.meta_data

    def merge_metadata(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method: merge updates into existing metadata."""
        return self.update_metadata(updates, mode="merge")

    def remove_metadata_keys(self, keys: List[str]) -> Dict[str, Any]:
        """
        Remove specific keys from metadata.

        Args:
            keys: List of keys to remove

        Returns:
            Updated metadata dictionary
        """
        if not self.meta_data:
            return {}
        for key in keys:
            self.meta_data.pop(key, None)
        return self.meta_data

    def clear_metadata(self) -> None:
        """Remove all metadata (set to None)."""
        self.meta_data = None

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific metadata value with optional default.

        Args:
            key: Metadata key to retrieve
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        if not self.meta_data:
            return default
        return self.meta_data.get(key, default)

    def has_metadata_key(self, key: str) -> bool:
        """
        Check if a metadata key exists.

        Args:
            key: Metadata key to check

        Returns:
            True if key exists in metadata
        """
        return bool(self.meta_data and key in self.meta_data)
