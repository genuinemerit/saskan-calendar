"""
Tests for timeline CLI data commands.

Tests the add/create commands for timeline data operations.
"""

import pytest
from typer.testing import CliRunner

from app_timeline.cli import app
from app_timeline.db.schema import drop_all_tables, create_all_tables

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Reset database before each test."""
    drop_all_tables()
    create_all_tables()
    yield
    # Cleanup after test
    drop_all_tables()


class TestEpochCommands:
    """Tests for epoch-related CLI commands."""

    def test_add_epoch_basic(self):
        """Test adding a basic epoch."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Test Epoch",
                "--start",
                "0",
                "--end",
                "100",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created epoch 'Test Epoch'" in result.stdout
        assert "ID: 1" in result.stdout

    def test_add_epoch_with_description(self):
        """Test adding epoch with description."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Test Epoch",
                "--start",
                "0",
                "--end",
                "100",
                "--description",
                "Test description",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created epoch 'Test Epoch'" in result.stdout

    def test_add_epoch_invalid_range(self):
        """Test that invalid date range fails."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Invalid Epoch",
                "--start",
                "100",
                "--end",
                "50",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_add_epoch_duplicate_name(self):
        """Test that duplicate names are rejected."""
        # Create first epoch
        runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Test Epoch",
                "--start",
                "0",
                "--end",
                "100",
                "--no-interactive",
            ],
        )

        # Try to create duplicate
        result = runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Test Epoch",
                "--start",
                "200",
                "--end",
                "300",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 1
        assert "already exists" in result.stdout


class TestRegionCommands:
    """Tests for region-related CLI commands."""

    def test_add_region_basic(self):
        """Test adding a basic region."""
        result = runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        assert result.exit_code == 0
        assert "Created region 'Test Region'" in result.stdout
        assert "ID: 1" in result.stdout


class TestProvinceCommands:
    """Tests for province-related CLI commands."""

    def test_add_province_basic(self):
        """Test adding a basic province."""
        # Create region first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created province 'Test Province'" in result.stdout
        assert "in region 1" in result.stdout

    def test_add_province_invalid_region(self):
        """Test that invalid region ID fails."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "999",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 1
        assert "does not exist" in result.stdout


class TestSettlementCommands:
    """Tests for settlement-related CLI commands."""

    def test_add_settlement_basic(self):
        """Test adding a basic settlement."""
        # Create region and province first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "Test City",
                "--type",
                "city",
                "--province",
                "1",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created city 'Test City'" in result.stdout

    def test_add_settlement_with_grid(self):
        """Test adding settlement with grid coordinates."""
        # Create region and province first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "Test City",
                "--type",
                "city",
                "--province",
                "1",
                "--grid-x",
                "20",
                "--grid-y",
                "15",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Grid (20, 15)" in result.stdout

    def test_add_settlement_invalid_grid(self):
        """Test that invalid grid coordinates fail."""
        # Create region and province first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "Test City",
                "--type",
                "city",
                "--province",
                "1",
                "--grid-x",
                "50",  # Invalid - should be 1-40
                "--grid-y",
                "15",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 1
        assert "grid_x must be between 1 and 40" in result.stdout


class TestEntityCommands:
    """Tests for entity-related CLI commands."""

    def test_add_entity_basic(self):
        """Test adding a basic entity."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-entity",
                "--name",
                "Test Person",
                "--type",
                "person",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created person 'Test Person'" in result.stdout

    def test_add_entity_with_dates(self):
        """Test adding entity with temporal bounds."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-entity",
                "--name",
                "Test Person",
                "--type",
                "person",
                "--founded",
                "0",
                "--dissolved",
                "1000",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created person 'Test Person'" in result.stdout
        assert "Day 0" in result.stdout


class TestEventCommands:
    """Tests for event-related CLI commands."""

    def test_add_event_basic(self):
        """Test adding a basic event."""
        result = runner.invoke(
            app,
            [
                "data",
                "add-event",
                "--title",
                "Test Event",
                "--type",
                "battle",
                "--day",
                "100",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created battle event 'Test Event'" in result.stdout
        assert "Day 100" in result.stdout

    def test_add_event_with_relations(self):
        """Test adding event with settlement and entity references."""
        # Create region, province, settlement, and entity
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "Test City",
                "--type",
                "city",
                "--province",
                "1",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-entity",
                "--name",
                "Test Person",
                "--type",
                "person",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-event",
                "--title",
                "Test Event",
                "--type",
                "founding",
                "--day",
                "100",
                "--settlement",
                "1",
                "--entity",
                "1",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created founding event 'Test Event'" in result.stdout


class TestSnapshotCommands:
    """Tests for snapshot-related CLI commands."""

    def test_add_snapshot_basic(self):
        """Test adding a basic snapshot."""
        # Create region, province, and settlement first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "Test City",
                "--type",
                "city",
                "--province",
                "1",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-snapshot",
                "--settlement",
                "1",
                "--day",
                "100",
                "--population",
                "5000",
                "--no-interactive",
            ],
        )
        assert result.exit_code == 0
        assert "Created snapshot for settlement 1" in result.stdout
        assert "at day 100" in result.stdout
        assert "5,000" in result.stdout


class TestRouteCommands:
    """Tests for route-related CLI commands."""

    def test_add_route_basic(self):
        """Test adding a basic route."""
        # Create region, province, and two settlements first
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Test Province",
                "--region",
                "1",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "City A",
                "--type",
                "city",
                "--province",
                "1",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-settlement",
                "--name",
                "City B",
                "--type",
                "city",
                "--province",
                "1",
                "--no-interactive",
            ],
        )

        result = runner.invoke(
            app,
            [
                "data",
                "add-route",
                "--from",
                "1",
                "--to",
                "2",
                "--distance",
                "50.5",
                "--no-interactive",
            ],
        )
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")
        assert result.exit_code == 0
        assert "Created route (ID: 1)" in result.stdout
        assert "From: Settlement 1 → Settlement 2" in result.stdout
        assert "50.5 km" in result.stdout
