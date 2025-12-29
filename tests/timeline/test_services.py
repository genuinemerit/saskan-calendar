"""
Tests for the timeline service layer.

Tests CRUD operations and business logic for all service classes.
"""

import pytest

from app_timeline.models import (
    Entity,
    Epoch,
    Event,
    Province,
    Region,
    Route,
    Settlement,
    SettlementSnapshot,
)
from app_timeline.services import (
    EntityService,
    EpochService,
    EventService,
    ProvinceService,
    RegionService,
    RouteService,
    SettlementService,
    SnapshotService,
)


class TestEpochService:
    """Tests for EpochService."""

    def test_create_epoch(self, db_session):
        """Test creating a valid epoch."""
        with EpochService() as service:
            epoch = service.create_epoch(
                name="Early Recovery Era",
                start_astro_day=0,
                end_astro_day=500,
                description="Initial settlement period",
            )

            assert epoch.id is not None
            assert epoch.name == "Early Recovery Era"
            assert epoch.start_astro_day == 0
            assert epoch.end_astro_day == 500
            assert epoch.duration == 500

    def test_create_epoch_invalid_range(self, db_session):
        """Test that creating epoch with end < start fails."""
        with EpochService() as service:
            with pytest.raises(ValueError, match="must be >="):
                service.create_epoch(
                    name="Invalid Epoch", start_astro_day=500, end_astro_day=100
                )

    def test_create_epoch_duplicate_name(self, db_session):
        """Test that duplicate epoch names are rejected."""
        with EpochService() as service:
            service.create_epoch(
                name="Test Epoch", start_astro_day=0, end_astro_day=100
            )

            with pytest.raises(ValueError, match="already exists"):
                service.create_epoch(
                    name="Test Epoch", start_astro_day=200, end_astro_day=300
                )

    def test_get_epochs_containing_day(self, db_session):
        """Test finding epochs containing a specific day."""
        with EpochService() as service:
            epoch1 = service.create_epoch(
                name="Epoch 1", start_astro_day=0, end_astro_day=100
            )
            epoch2 = service.create_epoch(
                name="Epoch 2", start_astro_day=50, end_astro_day=150
            )
            epoch3 = service.create_epoch(
                name="Epoch 3", start_astro_day=200, end_astro_day=300
            )

            # Day 75 should be in epochs 1 and 2
            epochs = service.get_epochs_containing_day(75)
            assert len(epochs) == 2
            assert epoch1 in epochs
            assert epoch2 in epochs
            assert epoch3 not in epochs

    def test_get_overlapping_epochs(self, db_session):
        """Test finding overlapping epochs."""
        with EpochService() as service:
            epoch1 = service.create_epoch(
                name="Epoch 1", start_astro_day=0, end_astro_day=100
            )
            epoch2 = service.create_epoch(
                name="Epoch 2", start_astro_day=50, end_astro_day=150
            )
            epoch3 = service.create_epoch(
                name="Epoch 3", start_astro_day=200, end_astro_day=300
            )

            # Epoch 1 should overlap with epoch 2 only
            overlapping = service.get_overlapping_epochs(epoch1.id)
            assert len(overlapping) == 1
            assert epoch2 in overlapping

    def test_get_epochs_in_range(self, db_session):
        """Test finding epochs in a time range."""
        with EpochService() as service:
            epoch1 = service.create_epoch(
                name="Epoch 1", start_astro_day=0, end_astro_day=100
            )
            epoch2 = service.create_epoch(
                name="Epoch 2", start_astro_day=50, end_astro_day=150
            )
            epoch3 = service.create_epoch(
                name="Epoch 3", start_astro_day=200, end_astro_day=300
            )

            # Query range 25-125 should overlap with epochs 1 and 2
            epochs = service.get_epochs_in_range(25, 125, fully_contained=False)
            assert len(epochs) == 2
            assert epoch1 in epochs
            assert epoch2 in epochs


class TestRegionService:
    """Tests for RegionService."""

    def test_create_region(self, db_session):
        """Test creating a valid region."""
        with RegionService() as service:
            region = service.create_region(name="Northern Territories")

            assert region.id is not None
            assert region.name == "Northern Territories"
            assert region.is_active is True

    def test_create_region_duplicate_name(self, db_session):
        """Test that duplicate region names are rejected."""
        with RegionService() as service:
            service.create_region(name="Test Region")

            with pytest.raises(ValueError, match="already exists"):
                service.create_region(name="Test Region")

    def test_get_active_regions(self, db_session):
        """Test retrieving active regions."""
        with RegionService() as service:
            region1 = service.create_region(name="Region A")
            region2 = service.create_region(name="Region B")

            regions = service.get_active_regions()
            assert len(regions) == 2
            assert region1 in regions
            assert region2 in regions


class TestProvinceService:
    """Tests for ProvinceService."""

    def test_create_province(self, db_session):
        """Test creating a valid province."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as service:
            province = service.create_province(
                name="Test Province", region_id=region.id
            )

            assert province.id is not None
            assert province.name == "Test Province"
            assert province.region_id == region.id

    def test_create_province_invalid_region(self, db_session):
        """Test that creating province with invalid region fails."""
        with ProvinceService() as service:
            with pytest.raises(ValueError, match="does not exist"):
                service.create_province(name="Test Province", region_id=999)

    def test_get_provinces_by_region(self, db_session):
        """Test retrieving provinces by region."""
        with RegionService() as region_service:
            region1 = region_service.create_region(name="Region 1")
            region2 = region_service.create_region(name="Region 2")

        with ProvinceService() as service:
            prov1 = service.create_province(name="Province A", region_id=region1.id)
            prov2 = service.create_province(name="Province B", region_id=region1.id)
            prov3 = service.create_province(name="Province C", region_id=region2.id)

            region1_provinces = service.get_provinces_by_region(region1.id)
            assert len(region1_provinces) == 2
            assert prov1 in region1_provinces
            assert prov2 in region1_provinces


class TestSettlementService:
    """Tests for SettlementService."""

    def test_create_settlement(self, db_session):
        """Test creating a valid settlement."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as service:
            settlement = service.create_settlement(
                name="Test City",
                province_id=province.id,
                settlement_type="city",
                grid_x=20,
                grid_y=15,
                area_sq_km=100.5,
            )

            assert settlement.id is not None
            assert settlement.name == "Test City"
            assert settlement.grid_x == 20
            assert settlement.grid_y == 15
            assert settlement.area_sq_km == 100.5

    def test_create_settlement_invalid_grid(self, db_session):
        """Test that invalid grid coordinates are rejected."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as service:
            # grid_x out of range
            with pytest.raises(ValueError, match="grid_x must be between 1 and 40"):
                service.create_settlement(
                    name="Invalid City",
                    province_id=province.id,
                    settlement_type="city",
                    grid_x=50,
                )

            # grid_y out of range
            with pytest.raises(ValueError, match="grid_y must be between 1 and 30"):
                service.create_settlement(
                    name="Invalid City",
                    province_id=province.id,
                    settlement_type="city",
                    grid_y=35,
                )

    def test_get_settlements_in_grid_area(self, db_session):
        """Test finding settlements in a grid area."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as service:
            s1 = service.create_settlement(
                name="City A",
                province_id=province.id,
                settlement_type="city",
                grid_x=10,
                grid_y=10,
            )
            s2 = service.create_settlement(
                name="City B",
                province_id=province.id,
                settlement_type="city",
                grid_x=20,
                grid_y=20,
            )
            s3 = service.create_settlement(
                name="City C",
                province_id=province.id,
                settlement_type="city",
                grid_x=30,
                grid_y=30,
            )

            # Query area (15, 25, 15, 25) should only contain s2
            settlements = service.get_settlements_in_grid_area(15, 25, 15, 25)
            assert len(settlements) == 1
            assert s2 in settlements


class TestSnapshotService:
    """Tests for SnapshotService."""

    def test_create_snapshot(self, db_session):
        """Test creating a valid settlement snapshot."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            settlement = settlement_service.create_settlement(
                name="Test City", province_id=province.id, settlement_type="city"
            )

        with SnapshotService() as service:
            snapshot = service.create_snapshot(
                settlement_id=settlement.id,
                astro_day=100,
                population=5000,
                labor_force=2000,
            )

            assert snapshot.id is not None
            assert snapshot.settlement_id == settlement.id
            assert snapshot.astro_day == 100
            assert snapshot.population == 5000

    def test_create_snapshot_duplicate(self, db_session):
        """Test that duplicate snapshots (same settlement + day) are rejected."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            settlement = settlement_service.create_settlement(
                name="Test City", province_id=province.id, settlement_type="city"
            )

        with SnapshotService() as service:
            service.create_snapshot(
                settlement_id=settlement.id, astro_day=100, population=5000
            )

            with pytest.raises(ValueError, match="already exists"):
                service.create_snapshot(
                    settlement_id=settlement.id, astro_day=100, population=6000
                )

    def test_get_snapshots_in_range(self, db_session):
        """Test finding snapshots in a time range."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            settlement = settlement_service.create_settlement(
                name="Test City", province_id=province.id, settlement_type="city"
            )

        with SnapshotService() as service:
            snap1 = service.create_snapshot(settlement_id=settlement.id, astro_day=50)
            snap2 = service.create_snapshot(settlement_id=settlement.id, astro_day=100)
            snap3 = service.create_snapshot(settlement_id=settlement.id, astro_day=150)

            # Query range 75-125 should contain snap2 only
            snapshots = service.get_snapshots_in_range(settlement.id, 75, 125)
            assert len(snapshots) == 1
            assert snap2 in snapshots


class TestRouteService:
    """Tests for RouteService."""

    def test_create_route(self, db_session):
        """Test creating a valid route."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            s1 = settlement_service.create_settlement(
                name="City A", province_id=province.id, settlement_type="city"
            )
            s2 = settlement_service.create_settlement(
                name="City B", province_id=province.id, settlement_type="city"
            )

        with RouteService() as service:
            route = service.create_route(
                name="Main Road",
                settlement_a_id=s1.id,
                settlement_b_id=s2.id,
                distance_km=50.0,
                travel_days=2.5,
                route_type="road",
            )

            assert route.id is not None
            assert route.name == "Main Road"
            assert route.distance_km == 50.0

    def test_create_route_same_settlement(self, db_session):
        """Test that routes must connect different settlements."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            settlement = settlement_service.create_settlement(
                name="City A", province_id=province.id, settlement_type="city"
            )

        with RouteService() as service:
            with pytest.raises(ValueError, match="two different settlements"):
                service.create_route(
                    name="Invalid Route",
                    settlement_a_id=settlement.id,
                    settlement_b_id=settlement.id,
                    distance_km=10.0,
                )

    def test_get_route_between_settlements(self, db_session):
        """Test finding route between two settlements."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            s1 = settlement_service.create_settlement(
                name="City A", province_id=province.id, settlement_type="city"
            )
            s2 = settlement_service.create_settlement(
                name="City B", province_id=province.id, settlement_type="city"
            )

        with RouteService() as service:
            route = service.create_route(
                name="Main Road",
                settlement_a_id=s1.id,
                settlement_b_id=s2.id,
                distance_km=50.0,
            )

            # Should find route regardless of order
            found1 = service.get_route_between_settlements(s1.id, s2.id)
            found2 = service.get_route_between_settlements(s2.id, s1.id)

            assert found1 == route
            assert found2 == route


class TestEntityService:
    """Tests for EntityService."""

    def test_create_entity(self, db_session):
        """Test creating a valid entity."""
        with EntityService() as service:
            entity = service.create_entity(
                name="King Aldric",
                entity_type="person",
                founded_astro_day=0,
                dissolved_astro_day=15000,
                description="First king",
            )

            assert entity.id is not None
            assert entity.name == "King Aldric"
            assert entity.entity_type == "person"

    def test_create_entity_invalid_temporal_bounds(self, db_session):
        """Test that end < start is rejected."""
        with EntityService() as service:
            with pytest.raises(
                ValueError, match="dissolved_astro_day.*must be.*founded_astro_day"
            ):
                service.create_entity(
                    name="Invalid Entity",
                    entity_type="person",
                    founded_astro_day=1000,
                    dissolved_astro_day=500,
                )

    def test_get_entities_alive_at_day(self, db_session):
        """Test finding entities alive at a specific day."""
        with EntityService() as service:
            e1 = service.create_entity(
                name="Entity 1",
                entity_type="person",
                founded_astro_day=0,
                dissolved_astro_day=100,
            )
            e2 = service.create_entity(
                name="Entity 2",
                entity_type="person",
                founded_astro_day=50,
                dissolved_astro_day=150,
            )
            e3 = service.create_entity(
                name="Entity 3",
                entity_type="person",
                founded_astro_day=200,
                dissolved_astro_day=300,
            )

            # Day 75 should have e1 and e2
            entities = service.get_entities_alive_at_day(75)
            assert len(entities) == 2
            assert e1 in entities
            assert e2 in entities


class TestEventService:
    """Tests for EventService."""

    def test_create_event(self, db_session):
        """Test creating a valid event."""
        with EventService() as service:
            event = service.create_event(
                title="Battle of the Plains",
                event_type="battle",
                astro_day=500,
                description="Major conflict",
            )

            assert event.id is not None
            assert event.title == "Battle of the Plains"
            assert event.astro_day == 500

    def test_create_event_with_relations(self, db_session):
        """Test creating event with settlement and entity references."""
        with RegionService() as region_service:
            region = region_service.create_region(name="Test Region")

        with ProvinceService() as province_service:
            province = province_service.create_province(
                name="Test Province", region_id=region.id
            )

        with SettlementService() as settlement_service:
            settlement = settlement_service.create_settlement(
                name="Test City", province_id=province.id, settlement_type="city"
            )

        with EntityService() as entity_service:
            entity = entity_service.create_entity(
                name="King Aldric", entity_type="person"
            )

        with EventService() as service:
            event = service.create_event(
                title="City Founding",
                event_type="founding",
                astro_day=100,
                settlement_id=settlement.id,
                entity_id=entity.id,
            )

            assert event.settlement_id == settlement.id
            assert event.entity_id == entity.id

    def test_get_events_in_range(self, db_session):
        """Test finding events in a time range."""
        with EventService() as service:
            e1 = service.create_event(
                title="Event 1", event_type="battle", astro_day=50
            )
            e2 = service.create_event(
                title="Event 2", event_type="treaty", astro_day=100
            )
            e3 = service.create_event(
                title="Event 3", event_type="founding", astro_day=150
            )

            # Range 75-125 should contain e2 only
            events = service.get_events_in_range(75, 125)
            assert len(events) == 1
            assert e2 in events

    def test_get_events_in_epoch(self, db_session):
        """Test finding events during an epoch."""
        with EpochService() as epoch_service:
            epoch = epoch_service.create_epoch(
                name="Test Epoch", start_astro_day=0, end_astro_day=100
            )

        with EventService() as service:
            e1 = service.create_event(
                title="Event 1", event_type="battle", astro_day=50
            )
            e2 = service.create_event(
                title="Event 2", event_type="treaty", astro_day=150
            )

            events = service.get_events_in_epoch(epoch.id)
            assert len(events) == 1
            assert e1 in events
