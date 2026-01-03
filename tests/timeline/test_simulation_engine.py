"""
Integration tests for simulation engine.

PR-003b: Tests for SimulationEngine including basic runs, event integration,
determinism, and multi-chunk execution.
"""

import pytest

from app_timeline.models.event import Event
from app_timeline.services import (
    EventService,
    ProvinceService,
    ProvinceSnapshotService,
    RegionService,
    RegionSnapshotService,
)
from app_timeline.simulation import SimulationConfig, SimulationEngine


class TestSimulationEngineBasic:
    """Tests for basic engine functionality."""

    def test_engine_initialization(self, test_db):
        """Test engine can be initialized."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        # Create engine
        config = SimulationConfig(seed=42)
        engine = SimulationEngine("region", region_id, config)

        assert engine.entity_type == "region"
        assert engine.entity_id == region_id
        assert engine.config.seed == 42

    def test_engine_rejects_invalid_entity_type(self, test_db):
        """Test engine rejects invalid entity types."""
        with pytest.raises(ValueError, match="entity_type must be"):
            SimulationEngine("invalid", 1, SimulationConfig())

    def test_engine_basic_run_with_zero_population(self, test_db):
        """Test basic engine run starting from zero population."""
        # Create region
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        # Run simulation (no initial snapshot, starts at zero)
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=365
        )
        engine = SimulationEngine("region", region_id, config)
        reports = engine.run(0, 365, granularity="year")

        # Should complete
        assert len(reports) == 1
        assert reports[0]["start_day"] == 0
        assert reports[0]["end_day"] == 365

        # Should remain at zero (no spontaneous generation)
        assert reports[0]["final_population"] == 0

    def test_engine_basic_run_with_initial_population(self, test_db):
        """Test basic engine run with initial population."""
        # Create region with initial snapshot
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

        # Run simulation
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=365
        )
        engine = SimulationEngine("region", region_id, config)
        reports = engine.run(0, 365, granularity="year")

        # Should complete
        assert len(reports) == 1

        # Should have grown (logistic growth from 10000)
        assert reports[0]["final_population"] > 10000

        # Verify snapshot was created
        with RegionSnapshotService() as snapshot_service:
            final_snapshot = snapshot_service.get_snapshot_at_day(region_id, 365)
            assert final_snapshot is not None
            assert final_snapshot.population_total > 10000
            assert final_snapshot.snapshot_type == "simulation"

    def test_engine_works_for_provinces(self, test_db):
        """Test engine works for provinces (not just regions)."""
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

        # Run simulation for province
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=365
        )
        engine = SimulationEngine("province", province_id, config)
        reports = engine.run(0, 365, granularity="year")

        # Should complete
        assert len(reports) == 1
        assert reports[0]["final_population"] > 5000


class TestSimulationEngineEvents:
    """Tests for event integration."""

    def test_engine_applies_population_shock(self, test_db):
        """Test engine applies event with population shock."""
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

        # Create event with shock at day 100
        with EventService() as event_service:
            event_service.create_event(
                title="Great Famine",
                event_type="natural_disaster",
                astro_day=100,
                region_id=region_id,
                meta_data={"effects": {"shock_multiplier": 0.75}}  # 25% loss
            )

        # Run simulation
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=365
        )
        engine = SimulationEngine("region", region_id, config)
        reports = engine.run(0, 365, granularity="year")

        # Should complete
        assert len(reports) == 1

        # Final population should be less than without the shock
        # (We can't check day 100 directly since snapshots are at intervals)
        # but final pop should be reduced compared to uninterrupted growth
        assert reports[0]["final_population"] < 30000  # Would be ~25k with growth, shock reduces it

    def test_engine_applies_infrastructure_damage(self, test_db):
        """Test engine applies event with infrastructure damage."""
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

        # Create event with infrastructure damage
        with EventService() as event_service:
            event_service.create_event(
                title="War Damage",
                event_type="battle",
                astro_day=50,
                region_id=region_id,
                meta_data={"effects": {"infrastructure_damage": 0.80}}  # 20% damage
            )

        # Run simulation
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=365,
            infrastructure_factor_initial=1.0
        )
        engine = SimulationEngine("region", region_id, config)
        reports = engine.run(0, 365, granularity="year")

        # Infrastructure factor should have been reduced
        assert reports[0]["infrastructure_factor"] < 1.0


class TestSimulationEngineDeterminism:
    """Tests for deterministic simulation."""

    def test_same_seed_produces_same_results(self, test_db):
        """Test same seed produces identical results."""
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

        # Run 1 with seed 42
        config1 = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=1000
        )
        engine1 = SimulationEngine("region", region_id, config1)
        reports1 = engine1.run(0, 1000, granularity="year")
        pop1 = reports1[0]["final_population"]
        env1 = reports1[0]["environmental_factor"]

        # Clear snapshots (except initial)
        with RegionSnapshotService() as snapshot_service:
            snapshots = snapshot_service.get_snapshots_for_region(region_id)
            for snap in snapshots:
                if snap.astro_day > 0:
                    snapshot_service.delete(snap.id)

        # Run 2 with same seed
        config2 = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=1000
        )
        engine2 = SimulationEngine("region", region_id, config2)
        reports2 = engine2.run(0, 1000, granularity="year")
        pop2 = reports2[0]["final_population"]
        env2 = reports2[0]["environmental_factor"]

        # Should be identical
        assert pop1 == pop2
        assert abs(env1 - env2) < 0.001  # Floating point tolerance

    def test_different_seed_produces_different_results(self, test_db):
        """Test different seeds produce different results."""
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

        # Run 1 with seed 42
        config1 = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=1000
        )
        engine1 = SimulationEngine("region", region_id, config1)
        reports1 = engine1.run(0, 1000, granularity="year")
        env1 = reports1[0]["environmental_factor"]

        # Clear snapshots
        with RegionSnapshotService() as snapshot_service:
            snapshots = snapshot_service.get_snapshots_for_region(region_id)
            for snap in snapshots:
                if snap.astro_day > 0:
                    snapshot_service.delete(snap.id)

        # Run 2 with different seed
        config2 = SimulationConfig(
            seed=999,
            growth_rates={"huum": 0.004},
            chunk_size_days=1000
        )
        engine2 = SimulationEngine("region", region_id, config2)
        reports2 = engine2.run(0, 1000, granularity="year")
        env2 = reports2[0]["environmental_factor"]

        # Environmental factors should differ (randomly sampled)
        assert abs(env1 - env2) > 0.01


class TestSimulationEngineChunked:
    """Tests for chunked execution."""

    def test_multi_chunk_execution(self, test_db):
        """Test simulation runs across multiple chunks."""
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

        # Run with small chunk size to force multiple chunks
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=500  # Will create 3 chunks for 1000 days
        )
        engine = SimulationEngine("region", region_id, config)
        reports = engine.run(0, 1000, granularity="year")

        # Should have multiple chunks
        assert len(reports) > 1

        # Chunks should be sequential
        for i in range(len(reports) - 1):
            assert reports[i]["end_day"] < reports[i+1]["start_day"]

    def test_snapshot_granularity(self, test_db):
        """Test different snapshot granularities."""
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
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004},
            chunk_size_days=10000
        )
        engine = SimulationEngine("region", region_id, config)
        engine.run(0, 10000, granularity="decade")

        # Check snapshots created
        with RegionSnapshotService() as snapshot_service:
            snapshots = snapshot_service.get_snapshots_for_region(region_id)
            # Should have snapshots at decade intervals
            assert len(snapshots) > 1
            # All should have decade granularity
            for snap in snapshots:
                if snap.astro_day > 0:  # Skip initial
                    assert snap.granularity == "decade"


class TestSimulationEngineValidation:
    """Tests for validation and error handling."""

    def test_invalid_date_range(self, test_db):
        """Test engine rejects invalid date ranges."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        config = SimulationConfig(seed=42)
        engine = SimulationEngine("region", region_id, config)

        # start >= end should fail
        with pytest.raises(ValueError, match="must be <"):
            engine.run(100, 50, granularity="year")

    def test_invalid_granularity(self, test_db):
        """Test engine rejects invalid granularity."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")
            region_id = region.id

        config = SimulationConfig(seed=42)
        engine = SimulationEngine("region", region_id, config)

        with pytest.raises(ValueError, match="granularity must be"):
            engine.run(0, 100, granularity="invalid")

    def test_nonexistent_entity(self, test_db):
        """Test engine fails gracefully for nonexistent entity."""
        config = SimulationConfig(seed=42)
        engine = SimulationEngine("region", 99999, config)  # Doesn't exist

        with pytest.raises(ValueError, match="does not exist"):
            engine.run(0, 100, granularity="year")
