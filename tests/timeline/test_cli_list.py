"""
tests.timeline.test_cli_list

Tests for CLI list/query commands.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from app_timeline.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_data():
    """Setup test data before each test."""
    # Initialize database
    runner.invoke(app, ["db", "init"])

    # Create test data for list commands
    # Add epoch
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

    # Add region
    runner.invoke(
        app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
    )

    # Add province
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

    # Add settlements
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
            "--grid-x",
            "10",
            "--grid-y",
            "10",
            "--no-interactive",
        ],
    )
    runner.invoke(
        app,
        [
            "data",
            "add-settlement",
            "--name",
            "Test Town",
            "--type",
            "town",
            "--province",
            "1",
            "--no-interactive",
        ],
    )

    # Add entity
    runner.invoke(
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
            "--no-interactive",
        ],
    )

    # Add event
    runner.invoke(
        app,
        [
            "data",
            "add-event",
            "--title",
            "Test Event",
            "--type",
            "founding",
            "--day",
            "50",
            "--settlement",
            "1",
            "--entity",
            "1",
            "--no-interactive",
        ],
    )

    # Add route
    runner.invoke(
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
            "--type",
            "road",
            "--no-interactive",
        ],
    )

    # Add snapshot
    runner.invoke(
        app,
        [
            "data",
            "add-snapshot",
            "--settlement",
            "1",
            "--day",
            "50",
            "--population",
            "1000",
            "--no-interactive",
        ],
    )

    yield

    # Cleanup after test
    runner.invoke(app, ["db", "drop", "--yes"])


class TestEpochListCommands:
    """Tests for epoch list commands."""

    def test_list_epochs(self):
        """Test listing all epochs."""
        result = runner.invoke(app, ["list", "epochs"])
        assert result.exit_code == 0
        assert "Test Epoch" in result.stdout
        # Note: May show more than 1 if database has residual data
        assert "found" in result.stdout

    def test_list_epochs_empty(self):
        """Test listing epochs when none exist."""
        # Drop and reinit to get empty database
        runner.invoke(app, ["db", "drop", "--yes"])
        runner.invoke(app, ["db", "init"])

        result = runner.invoke(app, ["list", "epochs"])
        assert result.exit_code == 0
        assert "No epochs found" in result.stdout


class TestRegionListCommands:
    """Tests for region list commands."""

    def test_list_regions(self):
        """Test listing all regions."""
        result = runner.invoke(app, ["list", "regions"])
        assert result.exit_code == 0
        assert "Test Region" in result.stdout
        assert "1 found" in result.stdout


class TestProvinceListCommands:
    """Tests for province list commands."""

    def test_list_provinces(self):
        """Test listing all provinces."""
        result = runner.invoke(app, ["list", "provinces"])
        assert result.exit_code == 0
        assert "Test Province" in result.stdout
        assert "1 found" in result.stdout

    def test_list_provinces_by_region(self):
        """Test listing provinces filtered by region."""
        result = runner.invoke(app, ["list", "provinces", "--region", "1"])
        assert result.exit_code == 0
        assert "Test Province" in result.stdout
        assert "1 found" in result.stdout


class TestSettlementListCommands:
    """Tests for settlement list commands."""

    def test_list_settlements(self):
        """Test listing all settlements."""
        result = runner.invoke(app, ["list", "settlements"])
        assert result.exit_code == 0
        assert "Test City" in result.stdout
        assert "Test Town" in result.stdout
        assert "2 found" in result.stdout

    def test_list_settlements_by_type(self):
        """Test listing settlements filtered by type."""
        result = runner.invoke(app, ["list", "settlements", "--type", "city"])
        assert result.exit_code == 0
        assert "Test City" in result.stdout
        assert "Test Town" not in result.stdout
        assert "1 found" in result.stdout

    def test_list_settlements_by_province(self):
        """Test listing settlements filtered by province."""
        result = runner.invoke(app, ["list", "settlements", "--province", "1"])
        assert result.exit_code == 0
        assert "Test City" in result.stdout
        assert "2 found" in result.stdout


class TestEntityListCommands:
    """Tests for entity list commands."""

    def test_list_entities(self):
        """Test listing all entities."""
        result = runner.invoke(app, ["list", "entities"])
        assert result.exit_code == 0
        assert "Test Person" in result.stdout
        assert "1 found" in result.stdout

    def test_list_entities_by_type(self):
        """Test listing entities filtered by type."""
        result = runner.invoke(app, ["list", "entities", "--type", "person"])
        assert result.exit_code == 0
        assert "Test Person" in result.stdout
        assert "1 found" in result.stdout

    def test_list_entities_by_day(self):
        """Test listing entities alive at a specific day."""
        result = runner.invoke(app, ["list", "entities", "--day", "50"])
        assert result.exit_code == 0
        assert "Test Person" in result.stdout
        assert "1 found" in result.stdout


class TestEventListCommands:
    """Tests for event list commands."""

    def test_list_events(self):
        """Test listing all events."""
        result = runner.invoke(app, ["list", "events"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout

    def test_list_events_by_type(self):
        """Test listing events filtered by type."""
        result = runner.invoke(app, ["list", "events", "--type", "founding"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout

    def test_list_events_by_day(self):
        """Test listing events at a specific day."""
        result = runner.invoke(app, ["list", "events", "--day", "50"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout

    def test_list_events_by_settlement(self):
        """Test listing events filtered by settlement."""
        result = runner.invoke(app, ["list", "events", "--settlement", "1"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout

    def test_list_events_by_entity(self):
        """Test listing events filtered by entity."""
        result = runner.invoke(app, ["list", "events", "--entity", "1"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout

    def test_list_events_by_range(self):
        """Test listing events within a date range."""
        result = runner.invoke(app, ["list", "events", "--start", "0", "--end", "100"])
        assert result.exit_code == 0
        assert "Test Event" in result.stdout
        assert "1 found" in result.stdout


class TestRouteListCommands:
    """Tests for route list commands."""

    def test_list_routes(self):
        """Test listing all routes."""
        result = runner.invoke(app, ["list", "routes"])
        assert result.exit_code == 0
        assert "50.5" in result.stdout
        assert "1 found" in result.stdout

    def test_list_routes_by_settlement(self):
        """Test listing routes filtered by settlement."""
        result = runner.invoke(app, ["list", "routes", "--settlement", "1"])
        assert result.exit_code == 0
        assert "50.5" in result.stdout
        assert "1 found" in result.stdout

    def test_list_routes_by_type(self):
        """Test listing routes filtered by type."""
        result = runner.invoke(app, ["list", "routes", "--type", "road"])
        assert result.exit_code == 0
        assert "road" in result.stdout
        assert "1 found" in result.stdout


class TestSnapshotListCommands:
    """Tests for snapshot list commands."""

    def test_list_snapshots(self):
        """Test listing snapshots for a settlement."""
        result = runner.invoke(app, ["list", "snapshots", "--settlement", "1"])
        assert result.exit_code == 0
        assert "1,000" in result.stdout
        assert "1 found" in result.stdout

    def test_list_snapshots_by_range(self):
        """Test listing snapshots within a date range."""
        result = runner.invoke(
            app,
            ["list", "snapshots", "--settlement", "1", "--start", "0", "--end", "100"],
        )
        assert result.exit_code == 0
        assert "1,000" in result.stdout
        assert "1 found" in result.stdout

    def test_list_snapshots_empty(self):
        """Test listing snapshots for settlement with none."""
        result = runner.invoke(app, ["list", "snapshots", "--settlement", "2"])
        assert result.exit_code == 0
        assert "No snapshots found" in result.stdout
