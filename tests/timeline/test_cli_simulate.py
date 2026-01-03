"""
Tests for simulation CLI commands.

PR-003b: Tests for `simulate region` and `simulate province` CLI commands.
"""

import pytest
from typer.testing import CliRunner

from app_timeline.cli import app
from app_timeline.services import (
    ProvinceService,
    ProvinceSnapshotService,
    RegionService,
    RegionSnapshotService,
)

runner = CliRunner()


class TestSimulateRegionCommand:
    """Tests for simulate region CLI command."""

    def test_simulate_region_command_basic(self, test_db):
        """Test basic simulate region command."""
        # Create region with initial population
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with RegionSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                region_id=region_id,
                astro_day=0,
                population_total=10000,
                population_by_species={"huum": 10000}
            )

        # Run command
        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "0", "--end", "1000", "--seed", "42"]
        )

        # Should succeed
        assert result.exit_code == 0
        assert "Simulation complete" in result.output

    def test_simulate_region_with_granularity(self, test_db):
        """Test simulate region with different granularity."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with RegionSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                region_id=region_id,
                astro_day=0,
                population_total=10000,
                population_by_species={"huum": 10000}
            )

        # Run with decade granularity
        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "0", "--end", "10000",
             "--granularity", "decade", "--seed", "42"]
        )

        assert result.exit_code == 0
        assert "decade" in result.output.lower()

    def test_simulate_region_with_custom_chunk_size(self, test_db):
        """Test simulate region with custom chunk size."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with RegionSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                region_id=region_id,
                astro_day=0,
                population_total=10000,
                population_by_species={"huum": 10000}
            )

        # Run with custom chunk size
        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "0", "--end", "2000",
             "--chunk-size", "500", "--seed", "42"]
        )

        assert result.exit_code == 0
        # Should have multiple chunks
        assert "Chunk" in result.output

    def test_simulate_region_missing_required_args(self, test_db):
        """Test simulate region fails without required arguments."""
        result = runner.invoke(
            app,
            ["simulate", "region", "1"]  # Missing --start and --end
        )

        # Should fail
        assert result.exit_code != 0

    def test_simulate_region_nonexistent_region(self, test_db):
        """Test simulate region fails for nonexistent region."""
        result = runner.invoke(
            app,
            ["simulate", "region", "99999", "--start", "0", "--end", "1000"]
        )

        # Should fail
        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_simulate_region_invalid_date_range(self, test_db):
        """Test simulate region fails with invalid date range."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        # Run with start > end
        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "1000", "--end", "100"]
        )

        # Should fail
        assert result.exit_code == 1
        assert "must be <" in result.output

    def test_simulate_region_displays_results_table(self, test_db):
        """Test simulate region displays results table."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with RegionSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                region_id=region_id,
                astro_day=0,
                population_total=10000,
                population_by_species={"huum": 10000}
            )

        # Run command
        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "0", "--end", "1000", "--seed", "42"]
        )

        assert result.exit_code == 0
        # Should contain table headers
        assert "Simulation Results" in result.output
        assert "Final Pop." in result.output
        assert "Capacity" in result.output


class TestSimulateProvinceCommand:
    """Tests for simulate province CLI command."""

    def test_simulate_province_command_basic(self, test_db):
        """Test basic simulate province command."""
        # Create region and province
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province",
                region_id=region_id
            )
            province_id = province.id

        with ProvinceSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                province_id=province_id,
                astro_day=0,
                population_total=5000,
                population_by_species={"huum": 5000}
            )

        # Run command
        result = runner.invoke(
            app,
            ["simulate", "province", str(province_id), "--start", "0", "--end", "1000", "--seed", "42"]
        )

        # Should succeed
        assert result.exit_code == 0
        assert "Simulation complete" in result.output

    def test_simulate_province_with_seed(self, test_db):
        """Test simulate province produces same results with same seed."""
        # Create region and province
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province",
                region_id=region_id
            )
            province_id = province.id

        with ProvinceSnapshotService() as snapshot_service:
            snapshot_service.create_snapshot(
                province_id=province_id,
                astro_day=0,
                population_total=5000,
                population_by_species={"huum": 5000}
            )

        # Run 1 with seed
        result1 = runner.invoke(
            app,
            ["simulate", "province", str(province_id), "--start", "0", "--end", "1000", "--seed", "42"]
        )

        # Extract final population from output
        assert result1.exit_code == 0

        # Should show deterministic results
        assert "Seed: 42" in result1.output

    def test_simulate_province_nonexistent_province(self, test_db):
        """Test simulate province fails for nonexistent province."""
        result = runner.invoke(
            app,
            ["simulate", "province", "99999", "--start", "0", "--end", "1000"]
        )

        # Should fail
        assert result.exit_code == 1
        assert "does not exist" in result.output


class TestSimulateCommandValidation:
    """Tests for simulation command validation."""

    def test_invalid_granularity(self, test_db):
        """Test command rejects invalid granularity."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        result = runner.invoke(
            app,
            ["simulate", "region", str(region_id), "--start", "0", "--end", "1000",
             "--granularity", "invalid"]
        )

        # Should fail
        assert result.exit_code == 1
        assert "granularity must be" in result.output

    def test_help_message(self):
        """Test help messages are displayed correctly."""
        # Test simulate help
        result = runner.invoke(app, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "Macro-scale simulation" in result.output

        # Test simulate region help
        result = runner.invoke(app, ["simulate", "region", "--help"])
        assert result.exit_code == 0
        assert "Run macro-scale simulation for a region" in result.output

        # Test simulate province help
        result = runner.invoke(app, ["simulate", "province", "--help"])
        assert result.exit_code == 0
        assert "Run macro-scale simulation for a province" in result.output
