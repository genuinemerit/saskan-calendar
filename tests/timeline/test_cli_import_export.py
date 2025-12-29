"""
tests.timeline.test_cli_import_export

Tests for CLI import/export commands.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from app_timeline.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path):
    """Setup test environment with clean database."""
    # Initialize database
    runner.invoke(app, ["db", "init"])

    yield tmp_path

    # Cleanup
    runner.invoke(app, ["db", "drop", "--yes"])


class TestExportCommand:
    """Tests for export command."""

    def test_export_all_entities(self, tmp_path):
        """Test exporting all entity types."""
        # Create test data
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
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )

        # Export
        output_file = tmp_path / "export.json"
        result = runner.invoke(app, ["io", "export", str(output_file)])

        assert result.exit_code == 0
        assert "Exported" in result.stdout
        assert output_file.exists()

        # Verify JSON structure
        with open(output_file) as f:
            data = json.load(f)

        assert "epochs" in data
        assert "regions" in data
        # Note: May have more than expected if database has residual data
        assert len(data["epochs"]) >= 1
        assert len(data["regions"]) >= 1
        # Verify our test data is present
        epoch_names = [e["name"] for e in data["epochs"]]
        assert "Test Epoch" in epoch_names

    def test_export_single_entity_type(self, tmp_path):
        """Test exporting a single entity type."""
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
        runner.invoke(
            app, ["data", "add-region", "--name", "Test Region", "--no-interactive"]
        )

        output_file = tmp_path / "epochs_only.json"
        result = runner.invoke(
            app, ["io", "export", str(output_file), "--type", "epochs"]
        )

        assert result.exit_code == 0

        with open(output_file) as f:
            data = json.load(f)

        assert "epochs" in data
        assert "regions" not in data
        assert len(data["epochs"]) == 1

    def test_export_with_inactive_records(self, tmp_path):
        """Test exporting with inactive records included."""
        # Create and delete a region
        runner.invoke(
            app, ["data", "add-region", "--name", "Active Region", "--no-interactive"]
        )
        runner.invoke(
            app, ["data", "add-region", "--name", "Inactive Region", "--no-interactive"]
        )
        runner.invoke(app, ["update", "delete-region", "2", "--yes"])

        # Export without inactive
        output_file = tmp_path / "active_only.json"
        result = runner.invoke(app, ["io", "export", str(output_file)])

        with open(output_file) as f:
            data = json.load(f)

        assert len(data["regions"]) == 1
        assert data["regions"][0]["name"] == "Active Region"

        # Export with inactive
        output_file_all = tmp_path / "all.json"
        result = runner.invoke(
            app, ["io", "export", str(output_file_all), "--include-inactive"]
        )

        with open(output_file_all) as f:
            data_all = json.load(f)

        assert len(data_all["regions"]) == 2

    def test_export_empty_database(self, tmp_path):
        """Test exporting from empty database."""
        output_file = tmp_path / "empty.json"
        result = runner.invoke(app, ["io", "export", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        # All entity lists should be empty
        assert all(len(v) == 0 for v in data.values())


class TestImportCommand:
    """Tests for import command."""

    def test_import_valid_data(self, tmp_path):
        """Test importing valid JSON data."""
        # Create test data file
        test_data = {
            "epochs": [
                {
                    "name": "Imported Epoch",
                    "start_astro_day": 0,
                    "end_astro_day": 500,
                    "description": "Test import",
                    "meta_data": None,
                }
            ],
            "regions": [{"name": "Imported Region", "meta_data": None}],
        }

        input_file = tmp_path / "import.json"
        with open(input_file, "w") as f:
            json.dump(test_data, f)

        # Import
        result = runner.invoke(app, ["io", "import", str(input_file)])

        assert result.exit_code == 0
        assert "Import complete" in result.stdout
        assert "Created: 2" in result.stdout

        # Verify data
        list_result = runner.invoke(app, ["list", "epochs"])
        assert "Imported Epoch" in list_result.stdout

    def test_import_dry_run(self, tmp_path):
        """Test import dry-run mode."""
        test_data = {
            "epochs": [
                {
                    "name": "Test Epoch",
                    "start_astro_day": 0,
                    "end_astro_day": 100,
                    "description": None,
                    "meta_data": None,
                }
            ]
        }

        input_file = tmp_path / "import.json"
        with open(input_file, "w") as f:
            json.dump(test_data, f)

        result = runner.invoke(app, ["io", "import", str(input_file), "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would create epoch: Test Epoch" in result.stdout

        # Verify nothing was actually created
        list_result = runner.invoke(app, ["list", "epochs"])
        assert "Test Epoch" not in list_result.stdout

    def test_import_skip_existing(self, tmp_path):
        """Test import with skip-existing flag."""
        # Create existing data
        runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Existing Epoch",
                "--start",
                "0",
                "--end",
                "100",
                "--no-interactive",
            ],
        )

        # Prepare import data with same epoch
        test_data = {
            "epochs": [
                {
                    "name": "Existing Epoch",
                    "start_astro_day": 0,
                    "end_astro_day": 200,
                    "description": "Different description",
                    "meta_data": None,
                },
                {
                    "name": "New Epoch",
                    "start_astro_day": 100,
                    "end_astro_day": 200,
                    "description": None,
                    "meta_data": None,
                },
            ]
        }

        input_file = tmp_path / "import.json"
        with open(input_file, "w") as f:
            json.dump(test_data, f)

        result = runner.invoke(
            app, ["io", "import", str(input_file), "--skip-existing"]
        )

        assert result.exit_code == 0
        assert "Created: 1" in result.stdout
        assert "Skipped: 1" in result.stdout

    def test_import_nonexistent_file(self, tmp_path):
        """Test importing from non-existent file."""
        result = runner.invoke(
            app, ["io", "import", str(tmp_path / "nonexistent.json")]
        )

        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_import_invalid_json(self, tmp_path):
        """Test importing invalid JSON."""
        input_file = tmp_path / "invalid.json"
        with open(input_file, "w") as f:
            f.write("{ invalid json }")

        result = runner.invoke(app, ["io", "import", str(input_file)])

        assert result.exit_code == 1
        assert "Invalid JSON" in result.stdout


class TestRoundTripImportExport:
    """Tests for export-then-import round trip."""

    def test_round_trip_preserves_data(self, tmp_path):
        """Test that export then import preserves all data."""
        # Create comprehensive test data
        runner.invoke(
            app,
            [
                "data",
                "add-epoch",
                "--name",
                "Round Trip Epoch",
                "--start",
                "0",
                "--end",
                "1000",
                "--description",
                "Test",
                "--no-interactive",
            ],
        )
        runner.invoke(
            app,
            ["data", "add-region", "--name", "Round Trip Region", "--no-interactive"],
        )
        runner.invoke(
            app,
            [
                "data",
                "add-province",
                "--name",
                "Round Trip Province",
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
                "Round Trip City",
                "--type",
                "city",
                "--province",
                "1",
                "--grid-x",
                "10",
                "--grid-y",
                "20",
                "--no-interactive",
            ],
        )

        # Export
        export_file = tmp_path / "export.json"
        runner.invoke(app, ["io", "export", str(export_file)])

        # Drop database
        runner.invoke(app, ["db", "drop", "--yes"])
        runner.invoke(app, ["db", "init"])

        # Import
        result = runner.invoke(app, ["io", "import", str(export_file)])
        assert result.exit_code == 0

        # Verify all data preserved
        epochs = runner.invoke(app, ["list", "epochs"])
        assert "Round Trip Epoch" in epochs.stdout

        regions = runner.invoke(app, ["list", "regions"])
        assert "Round Trip Region" in regions.stdout

        provinces = runner.invoke(app, ["list", "provinces"])
        assert "Round Trip Province" in provinces.stdout

        settlements = runner.invoke(app, ["list", "settlements"])
        assert "Round Trip City" in settlements.stdout
        assert "(10, 20)" in settlements.stdout
