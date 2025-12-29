"""
Tests for database connection and schema management.
"""

from sqlalchemy.orm import Session

from app_timeline.db import (
    create_all_tables,
    drop_all_tables,
    get_engine,
    get_table_info,
    get_table_row_counts,
    validate_schema,
)


class TestDatabaseConnection:
    """Tests for database connection utilities."""

    def test_get_engine(self, test_config):
        """Test engine creation."""
        engine = get_engine()
        assert engine is not None
        assert str(engine.url).startswith("sqlite:///")

    def test_engine_singleton(self, test_config):
        """Test that get_engine returns the same instance."""
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2


class TestSchemaManagement:
    """Tests for schema management utilities."""

    def test_create_all_tables(self, test_config):
        """Test table creation."""
        create_all_tables()

        table_info = get_table_info()
        assert len(table_info) == 7

        expected_tables = {
            "regions",
            "provinces",
            "settlements",
            "settlement_snapshots",
            "routes",
            "entities",
            "events",
        }
        assert set(table_info.keys()) == expected_tables

    def test_table_row_counts(self, test_db, db_session: Session):
        """Test row count retrieval."""
        counts = get_table_row_counts()

        # All tables should exist with zero rows
        assert counts["regions"] == 0
        assert counts["provinces"] == 0
        assert counts["settlements"] == 0
        assert counts["settlement_snapshots"] == 0
        assert counts["routes"] == 0
        assert counts["entities"] == 0
        assert counts["events"] == 0

    def test_validate_schema_success(self, test_db):
        """Test schema validation with all tables present."""
        messages = validate_schema()

        assert len(messages) == 1
        assert "passed" in messages[0].lower()

    def test_validate_schema_missing_tables(self, test_config):
        """Test schema validation with missing tables."""
        # Don't create tables, validation should fail
        messages = validate_schema()

        assert len(messages) > 0
        assert any("missing" in msg.lower() for msg in messages)

    def test_drop_all_tables(self, test_db):
        """Test dropping all tables."""
        # Verify tables exist first
        table_info_before = get_table_info()
        assert len(table_info_before) == 7

        # Drop tables
        drop_all_tables()

        # Verify tables are gone
        table_info_after = get_table_info()
        assert len(table_info_after) == 0
