"""
Tests for RegionSnapshotService and ProvinceSnapshotService.

PR-003a: Tests for macro-scale demographic snapshot services including
interpolation, validation, and temporal queries.
"""

import pytest

from app_timeline.models import Province, Region
from app_timeline.services import (
    ProvinceService,
    ProvinceSnapshotService,
    RegionService,
    RegionSnapshotService,
)


class TestRegionSnapshotService:
    """Tests for RegionSnapshotService."""

    def test_create_snapshot(self, db_session):
        """Test creating a valid region snapshot."""
        # Create region first
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        # Create snapshot
        with RegionSnapshotService() as service:
            snapshot = service.create_snapshot(
                region_id=region.id,
                astro_day=100,
                population_total=50000,
                snapshot_type="census",
                granularity="year",
                population_by_species={"huum": 30000, "sint": 20000},
                population_by_habitat={"on_ground": 45000, "under_ground": 5000},
                meta_data={"source": "census_2025"},
            )

            assert snapshot.id is not None
            assert snapshot.region_id == region.id
            assert snapshot.astro_day == 100
            assert snapshot.population_total == 50000
            assert snapshot.snapshot_type == "census"
            assert snapshot.granularity == "year"
            assert snapshot.population_by_species == {"huum": 30000, "sint": 20000}
            assert snapshot.meta_data == {"source": "census_2025"}

    def test_create_snapshot_invalid_region(self, db_session):
        """Test that creating snapshot with invalid region ID fails."""
        with RegionSnapshotService() as service:
            with pytest.raises(ValueError, match="does not exist"):
                service.create_snapshot(
                    region_id=9999,
                    astro_day=100,
                    population_total=50000,
                )

    def test_create_snapshot_negative_day(self, db_session):
        """Test that negative astro_day is rejected."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            with pytest.raises(ValueError, match="astro_day must be >= 0"):
                service.create_snapshot(
                    region_id=region.id,
                    astro_day=-1,
                    population_total=50000,
                )

    def test_create_snapshot_negative_population(self, db_session):
        """Test that negative population is rejected."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            with pytest.raises(ValueError, match="population_total must be >= 0"):
                service.create_snapshot(
                    region_id=region.id,
                    astro_day=100,
                    population_total=-1000,
                )

    def test_create_snapshot_duplicate(self, db_session):
        """Test that duplicate snapshots (same region + day) are rejected."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            # Create first snapshot
            service.create_snapshot(
                region_id=region.id,
                astro_day=100,
                population_total=50000,
            )

            # Attempt to create duplicate
            with pytest.raises(ValueError, match="already exists"):
                service.create_snapshot(
                    region_id=region.id,
                    astro_day=100,
                    population_total=60000,
                )

    def test_get_snapshots_for_region(self, db_session):
        """Test retrieving all snapshots for a region."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snap1 = service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )
            snap2 = service.create_snapshot(
                region_id=region.id, astro_day=200, population_total=60000
            )
            snap3 = service.create_snapshot(
                region_id=region.id, astro_day=300, population_total=70000
            )

            snapshots = service.get_snapshots_for_region(region.id)

            assert len(snapshots) == 3
            assert snapshots[0].astro_day == 100  # Ordered by day
            assert snapshots[1].astro_day == 200
            assert snapshots[2].astro_day == 300

    def test_get_snapshots_for_region_filtered(self, db_session):
        """Test retrieving filtered snapshots for a region."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            service.create_snapshot(
                region_id=region.id,
                astro_day=100,
                population_total=50000,
                snapshot_type="census",
                granularity="year",
            )
            service.create_snapshot(
                region_id=region.id,
                astro_day=200,
                population_total=60000,
                snapshot_type="simulation",
                granularity="decade",
            )
            service.create_snapshot(
                region_id=region.id,
                astro_day=300,
                population_total=70000,
                snapshot_type="census",
                granularity="year",
            )

            # Filter by day range
            snapshots = service.get_snapshots_for_region(
                region.id, start_day=150, end_day=250
            )
            assert len(snapshots) == 1
            assert snapshots[0].astro_day == 200

            # Filter by snapshot type
            snapshots = service.get_snapshots_for_region(
                region.id, snapshot_type="census"
            )
            assert len(snapshots) == 2

            # Filter by granularity
            snapshots = service.get_snapshots_for_region(
                region.id, granularity="decade"
            )
            assert len(snapshots) == 1

    def test_get_snapshot_at_day(self, db_session):
        """Test retrieving exact snapshot at specific day."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )
            service.create_snapshot(
                region_id=region.id, astro_day=200, population_total=60000
            )

            # Exact match
            snapshot = service.get_snapshot_at_day(region.id, 100)
            assert snapshot is not None
            assert snapshot.astro_day == 100

            # No match
            snapshot = service.get_snapshot_at_day(region.id, 150)
            assert snapshot is None

    def test_get_nearest_snapshot(self, db_session):
        """Test finding nearest snapshot before/after a day."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snap1 = service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )
            snap2 = service.create_snapshot(
                region_id=region.id, astro_day=300, population_total=70000
            )

            # Nearest before
            nearest = service.get_nearest_snapshot(region.id, 200, before=True)
            assert nearest.id == snap1.id

            # Nearest after
            nearest = service.get_nearest_snapshot(region.id, 200, before=False)
            assert nearest.id == snap2.id

            # Exact match (before)
            nearest = service.get_nearest_snapshot(region.id, 100, before=True)
            assert nearest.id == snap1.id

            # No snapshot before
            nearest = service.get_nearest_snapshot(region.id, 50, before=True)
            assert nearest is None

            # No snapshot after
            nearest = service.get_nearest_snapshot(region.id, 400, before=False)
            assert nearest is None

    def test_get_interpolated_no_data(self, db_session):
        """Test interpolation with no snapshots available."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            result = service.get_interpolated(region.id, 100)
            assert result is None

    def test_get_interpolated_exact_match(self, db_session):
        """Test interpolation returns exact snapshot when available."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snapshot = service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )

            result = service.get_interpolated(region.id, 100)

            assert result is not None
            assert result["id"] == snapshot.id
            assert result["astro_day"] == 100
            assert result["population_total"] == 50000

    def test_get_interpolated_before_first(self, db_session):
        """Test interpolation before first snapshot returns first snapshot."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snapshot = service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )

            result = service.get_interpolated(region.id, 50)

            assert result is not None
            assert result["id"] == snapshot.id
            assert result["astro_day"] == 100

    def test_get_interpolated_after_last(self, db_session):
        """Test interpolation after last snapshot returns last snapshot."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snapshot = service.create_snapshot(
                region_id=region.id, astro_day=100, population_total=50000
            )

            result = service.get_interpolated(region.id, 200)

            assert result is not None
            assert result["id"] == snapshot.id
            assert result["astro_day"] == 100

    def test_get_interpolated_linear(self, db_session):
        """Test linear interpolation between snapshots."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            snap1 = service.create_snapshot(
                region_id=region.id,
                astro_day=100,
                population_total=50000,
                population_by_species={"huum": 30000, "sint": 20000},
                population_by_habitat={"on_ground": 45000, "under_ground": 5000},
                cultural_composition={"language": "Fatuni"},
                economic_data={"primary_industry": "agriculture"},
                meta_data={"source": "census"},
            )
            snap2 = service.create_snapshot(
                region_id=region.id,
                astro_day=200,
                population_total=70000,
                population_by_species={"huum": 40000, "sint": 30000},
                population_by_habitat={"on_ground": 60000, "under_ground": 10000},
                cultural_composition={"language": "Mixed"},
                economic_data={"primary_industry": "trade"},
                meta_data={"source": "estimate"},
            )

            # Interpolate at midpoint (day 150)
            result = service.get_interpolated(region.id, 150)

            assert result is not None
            assert result["astro_day"] == 150
            assert result["snapshot_type"] == "interpolated"
            assert result["population_total"] == 60000  # Midpoint

            # Check interpolated species breakdown
            assert result["population_by_species"]["huum"] == 35000
            assert result["population_by_species"]["sint"] == 25000

            # Check interpolated habitat breakdown
            assert result["population_by_habitat"]["on_ground"] == 52500
            assert result["population_by_habitat"]["under_ground"] == 7500

            # Check that JSON fields use nearest (before)
            assert result["cultural_composition"] == {"language": "Fatuni"}
            assert result["economic_data"] == {"primary_industry": "agriculture"}
            assert result["meta_data"] == {"source": "census"}

            # Check interpolation metadata
            assert result["interpolation_info"]["before_day"] == 100
            assert result["interpolation_info"]["after_day"] == 200
            assert result["interpolation_info"]["before_id"] == snap1.id
            assert result["interpolation_info"]["after_id"] == snap2.id
            assert result["interpolation_info"]["interpolation_factor"] == 0.5

    def test_interpolate_dict_with_new_keys(self, db_session):
        """Test dict interpolation handles keys appearing/disappearing."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with RegionSnapshotService() as service:
            # First snapshot has only huum
            service.create_snapshot(
                region_id=region.id,
                astro_day=100,
                population_total=50000,
                population_by_species={"huum": 50000},
            )

            # Second snapshot has both huum and sint
            service.create_snapshot(
                region_id=region.id,
                astro_day=200,
                population_total=70000,
                population_by_species={"huum": 40000, "sint": 30000},
            )

            # Interpolate at midpoint
            result = service.get_interpolated(region.id, 150)

            # huum should interpolate from 50000 to 40000
            assert result["population_by_species"]["huum"] == 45000

            # sint should interpolate from 0 to 30000
            assert result["population_by_species"]["sint"] == 15000


class TestProvinceSnapshotService:
    """Tests for ProvinceSnapshotService."""

    def test_create_snapshot(self, db_session):
        """Test creating a valid province snapshot."""
        # Create province first
        with ProvinceService() as province_service:
            province = province_service.create_province(name="Test Province")

        # Create snapshot
        with ProvinceSnapshotService() as service:
            snapshot = service.create_snapshot(
                province_id=province.id,
                astro_day=100,
                population_total=20000,
                snapshot_type="simulation",
                granularity="decade",
            )

            assert snapshot.id is not None
            assert snapshot.province_id == province.id
            assert snapshot.astro_day == 100
            assert snapshot.population_total == 20000
            assert snapshot.snapshot_type == "simulation"
            assert snapshot.granularity == "decade"

    def test_create_snapshot_invalid_province(self, db_session):
        """Test that creating snapshot with invalid province ID fails."""
        with ProvinceSnapshotService() as service:
            with pytest.raises(ValueError, match="does not exist"):
                service.create_snapshot(
                    province_id=9999,
                    astro_day=100,
                    population_total=20000,
                )

    def test_create_snapshot_duplicate(self, db_session):
        """Test that duplicate snapshots are rejected."""
        with ProvinceService() as province_service:
            province = province_service.create_province(name="Test Province")

        with ProvinceSnapshotService() as service:
            service.create_snapshot(
                province_id=province.id,
                astro_day=100,
                population_total=20000,
            )

            with pytest.raises(ValueError, match="already exists"):
                service.create_snapshot(
                    province_id=province.id,
                    astro_day=100,
                    population_total=25000,
                )

    def test_get_snapshots_for_province(self, db_session):
        """Test retrieving all snapshots for a province."""
        with ProvinceService() as province_service:
            province = province_service.create_province(name="Test Province")

        with ProvinceSnapshotService() as service:
            service.create_snapshot(
                province_id=province.id, astro_day=100, population_total=20000
            )
            service.create_snapshot(
                province_id=province.id, astro_day=200, population_total=25000
            )

            snapshots = service.get_snapshots_for_province(province.id)

            assert len(snapshots) == 2
            assert snapshots[0].astro_day == 100
            assert snapshots[1].astro_day == 200

    def test_interpolation_matches_region_pattern(self, db_session):
        """Test that province interpolation follows same pattern as region."""
        with ProvinceService() as province_service:
            province = province_service.create_province(name="Test Province")

        with ProvinceSnapshotService() as service:
            service.create_snapshot(
                province_id=province.id,
                astro_day=100,
                population_total=20000,
                population_by_species={"huum": 15000, "sint": 5000},
            )
            service.create_snapshot(
                province_id=province.id,
                astro_day=300,
                population_total=40000,
                population_by_species={"huum": 25000, "sint": 15000},
            )

            # Interpolate at midpoint
            result = service.get_interpolated(province.id, 200)

            assert result is not None
            assert result["population_total"] == 30000
            assert result["population_by_species"]["huum"] == 20000
            assert result["population_by_species"]["sint"] == 10000
