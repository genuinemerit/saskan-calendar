"""
app_timeline.services.base

Base service class providing common CRUD operations and patterns.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.connection import get_session
from ..models.base import Base

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """
    Base service class for CRUD operations.

    Provides common patterns for:
    - Creating records
    - Retrieving by ID or name
    - Listing with filters
    - Updating records
    - Soft deleting records

    Each model-specific service should inherit from this class.
    """

    def __init__(self, model_class: Type[ModelType]):
        """
        Initialize the service with a specific model class.

        :param model_class: SQLAlchemy model class (e.g., Epoch, Settlement)
        """
        self.model_class = model_class
        self._session: Optional[Session] = None

    @property
    def session(self) -> Session:
        """Get or create a database session."""
        if self._session is None:
            self._session = get_session()
        return self._session

    def close(self) -> None:
        """Close the database session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def __enter__(self) -> BaseService[ModelType]:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close session."""
        self.close()

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.

        :param kwargs: Field values for the new record
        :return: Created model instance
        :raises ValueError: If creation fails validation
        """
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to create {self.model_class.__name__}: {e}")

    def get_by_id(self, record_id: int) -> Optional[ModelType]:
        """
        Retrieve a record by its primary key ID.

        :param record_id: Primary key value
        :return: Model instance or None if not found
        """
        return self.session.get(self.model_class, record_id)

    def get_by_name(self, name: str) -> Optional[ModelType]:
        """
        Retrieve a record by name field.

        :param name: Name to search for
        :return: Model instance or None if not found
        :raises AttributeError: If model doesn't have a 'name' field
        """
        if not hasattr(self.model_class, "name"):
            raise AttributeError(
                f"{self.model_class.__name__} does not have a 'name' field"
            )

        stmt = select(self.model_class).where(self.model_class.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def list_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        active_only: bool = True,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        List all records with optional filtering.

        :param filters: Dictionary of field:value filters to apply
        :param active_only: If True, only return records where is_active=True
        :param order_by: Field name to order results by
        :return: List of model instances
        """
        stmt = select(self.model_class)

        # Apply is_active filter if model has the field
        if active_only and hasattr(self.model_class, "is_active"):
            stmt = stmt.where(self.model_class.is_active == True)

        # Apply custom filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    stmt = stmt.where(getattr(self.model_class, field) == value)

        # Apply ordering
        if order_by and hasattr(self.model_class, order_by):
            stmt = stmt.order_by(getattr(self.model_class, order_by))

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update(self, record_id: int, **kwargs) -> Optional[ModelType]:
        """
        Update an existing record.

        :param record_id: Primary key of record to update
        :param kwargs: Field values to update
        :return: Updated model instance or None if not found
        :raises ValueError: If update fails
        """
        instance = self.get_by_id(record_id)
        if instance is None:
            return None

        try:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            self.session.commit()
            self.session.refresh(instance)
            return instance
        except Exception as e:
            self.session.rollback()
            raise ValueError(
                f"Failed to update {self.model_class.__name__} {record_id}: {e}"
            )

    def delete(self, record_id: int, soft: bool = True) -> bool:
        """
        Delete a record (soft delete by default).

        :param record_id: Primary key of record to delete
        :param soft: If True, set is_active=False; if False, hard delete
        :return: True if deleted, False if not found
        :raises ValueError: If delete fails
        """
        instance = self.get_by_id(record_id)
        if instance is None:
            return False

        try:
            if soft and hasattr(instance, "is_active"):
                # Soft delete
                instance.is_active = False
                self.session.commit()
            else:
                # Hard delete
                self.session.delete(instance)
                self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(
                f"Failed to delete {self.model_class.__name__} {record_id}: {e}"
            )

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching optional filters.

        :param filters: Dictionary of field:value filters to apply
        :return: Count of matching records
        """
        stmt = select(self.model_class)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    stmt = stmt.where(getattr(self.model_class, field) == value)

        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))
