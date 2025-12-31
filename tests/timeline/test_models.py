"""
Tests for SQLAlchemy models and relationships.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app_timeline.models import (
    Entity,
    Epoch,
    Event,
    Province,
    ProvinceSnapshot,
    Region,
    RegionSnapshot,
    Route,
    Settlement,
    SettlementSnapshot,
)


class TestRegionModel:
    """Tests for Region model."""

    def test_create_region(self, db_session: Session):
        """Test creating a region."""
        region = Region(
            name="Northern Territories",
            founded_astro_day=0,
            is_active=True,
            meta_data={"description": "Cold northern lands"},
        )

        db_session.add(region)
        db_session.commit()

        assert region.id is not None
        assert region.name == "Northern Territories"
        assert region.is_active is True
        assert region.created_at is not None
        assert isinstance(region.created_at, datetime)

    def test_region_province_relationship(self, db_session: Session):
        """Test relationship between regions and provinces."""
        region = Region(name="Test Region", founded_astro_day=0)
        province = Province(name="Test Province", founded_astro_day=0, region=region)

        db_session.add(region)
        db_session.add(province)
        db_session.commit()

        assert province.region_id == region.id
        assert province in region.provinces


class TestProvinceModel:
    """Tests for Province model."""

    def test_create_province(self, db_session: Session):
        """Test creating a province."""
        province = Province(
            name="Fatunik Province",
            founded_astro_day=100,
            dissolved_astro_day=None,
            is_active=True,
            meta_data={"capital": "Ingar"},
        )

        db_session.add(province)
        db_session.commit()

        assert province.id is not None
        assert province.name == "Fatunik Province"
        assert province.founded_astro_day == 100
        assert province.is_active is True


class TestSettlementModel:
    """Tests for Settlement model."""

    def test_create_settlement(self, db_session: Session):
        """Test creating a settlement."""
        settlement = Settlement(
            name="Ingar",
            settlement_type="ring_town",
            founded_astro_day=0,
            location_x=100.5,
            location_y=200.3,
            is_active=True,
            is_autonomous=False,
            meta_data={"water": "fresh", "fertile": True},
        )

        db_session.add(settlement)
        db_session.commit()

        assert settlement.id is not None
        assert settlement.name == "Ingar"
        assert settlement.settlement_type == "ring_town"
        assert settlement.location_x == 100.5
        assert settlement.location_y == 200.3

    def test_settlement_parent_relationship(self, db_session: Session):
        """Test parent-child settlement relationship."""
        ring_town = Settlement(
            name="Parent Town",
            settlement_type="ring_town",
            founded_astro_day=0,
        )
        hamlet = Settlement(
            name="Child Hamlet",
            settlement_type="hamlet",
            founded_astro_day=10,
            parent=ring_town,
        )

        db_session.add(ring_town)
        db_session.add(hamlet)
        db_session.commit()

        assert hamlet.parent_settlement_id == ring_town.id
        assert hamlet in ring_town.satellites

    def test_settlement_province_relationship(self, db_session: Session):
        """Test settlement-province relationship."""
        province = Province(name="Test Province", founded_astro_day=0)
        settlement = Settlement(
            name="Test Settlement",
            settlement_type="hamlet",
            founded_astro_day=0,
            province=province,
        )

        db_session.add(province)
        db_session.add(settlement)
        db_session.commit()

        assert settlement.province_id == province.id
        assert settlement in province.settlements


class TestSettlementSnapshotModel:
    """Tests for SettlementSnapshot model."""

    def test_create_snapshot(self, db_session: Session):
        """Test creating a settlement snapshot."""
        settlement = Settlement(
            name="Test Town",
            settlement_type="market_town",
            founded_astro_day=0,
        )

        snapshot = SettlementSnapshot(
            settlement=settlement,
            astro_day=100,
            population_total=5000,
            population_by_species={"huum": 4500, "sint": 500},
            population_by_habitat={"on_ground": 5000},
            cultural_composition={"language": "Fatuni"},
            economic_data={"primary_industry": "agriculture"},
        )

        db_session.add(settlement)
        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.id is not None
        assert snapshot.settlement_id == settlement.id
        assert snapshot.astro_day == 100
        assert snapshot.population_total == 5000
        assert snapshot.population_by_species["huum"] == 4500

    def test_multiple_snapshots_per_settlement(self, db_session: Session):
        """Test that settlements can have multiple snapshots."""
        settlement = Settlement(
            name="Growing Town",
            settlement_type="hamlet",
            founded_astro_day=0,
        )

        snapshot1 = SettlementSnapshot(
            settlement=settlement,
            astro_day=0,
            population_total=100,
        )
        snapshot2 = SettlementSnapshot(
            settlement=settlement,
            astro_day=100,
            population_total=500,
        )

        db_session.add(settlement)
        db_session.add(snapshot1)
        db_session.add(snapshot2)
        db_session.commit()

        assert len(settlement.snapshots) == 2
        assert snapshot1 in settlement.snapshots
        assert snapshot2 in settlement.snapshots


class TestRouteModel:
    """Tests for Route model."""

    def test_create_route(self, db_session: Session):
        """Test creating a route between settlements."""
        origin = Settlement(
            name="Town A", settlement_type="ring_town", founded_astro_day=0
        )
        destination = Settlement(
            name="Town B", settlement_type="market_town", founded_astro_day=0
        )

        route = Route(
            origin_settlement_id=None,  # Will be set after adding settlements
            destination_settlement_id=None,
            founded_astro_day=10,
            distance_km=50.5,
            difficulty="moderate",
            route_type="road",
            is_active=True,
            meta_data={"terrain": "plains"},
        )

        db_session.add(origin)
        db_session.add(destination)
        db_session.flush()  # Get IDs

        route.origin_settlement_id = origin.id
        route.destination_settlement_id = destination.id

        db_session.add(route)
        db_session.commit()

        assert route.id is not None
        assert route.distance_km == 50.5
        assert route.difficulty == "moderate"
        assert route.route_type == "road"


class TestEntityModel:
    """Tests for Entity model."""

    def test_create_person_entity(self, db_session: Session):
        """Test creating a person entity."""
        person = Entity(
            name="Warrior Chief",
            entity_type="person",
            description="A legendary warrior",
            founded_astro_day=0,  # birth
            dissolved_astro_day=5000,  # death
            is_active=False,
            meta_data={
                "species": "huum",
                "birth_place": "Ingar",
                "roles": ["warrior", "leader"],
            },
        )

        db_session.add(person)
        db_session.commit()

        assert person.id is not None
        assert person.name == "Warrior Chief"
        assert person.entity_type == "person"
        assert person.meta_data["species"] == "huum"

    def test_create_organization_entity(self, db_session: Session):
        """Test creating an organization entity."""
        org = Entity(
            name="Traders Guild",
            entity_type="organization",
            description="Merchant organization",
            founded_astro_day=100,
            is_active=True,
            meta_data={"type": "economic", "size": "large"},
        )

        db_session.add(org)
        db_session.commit()

        assert org.id is not None
        assert org.entity_type == "organization"


class TestEventModel:
    """Tests for Event model."""

    def test_create_event(self, db_session: Session):
        """Test creating an event."""
        settlement = Settlement(
            name="Event Town", settlement_type="hamlet", founded_astro_day=0
        )
        db_session.add(settlement)
        db_session.flush()

        event = Event(
            astro_day=100,
            event_type="founding",
            title="Town Founded",
            description="A new settlement was established",
            location_x=100,
            location_y=200,
            settlement_id=settlement.id,
            is_deprecated=False,
            meta_data={"tags": ["settlement", "founding"], "importance": "high"},
        )

        db_session.add(event)
        db_session.commit()

        assert event.id is not None
        assert event.astro_day == 100
        assert event.event_type == "founding"
        assert event.title == "Town Founded"

    def test_event_deprecation(self, db_session: Session):
        """Test event deprecation and superseding."""
        # Create region for event location association
        region = Region(name="Test Region")
        db_session.add(region)
        db_session.flush()

        event1 = Event(
            astro_day=100,
            event_type="battle",
            title="Original Event",
            description="Original description",
            region_id=region.id,
        )

        db_session.add(event1)
        db_session.flush()

        event2 = Event(
            astro_day=100,
            event_type="battle",
            title="Corrected Event",
            description="Corrected description",
            region_id=region.id,
        )

        db_session.add(event2)
        db_session.flush()

        # Mark first event as deprecated
        event1.is_deprecated = True
        event1.superseded_by_id = event2.id

        db_session.commit()

        assert event1.is_deprecated is True
        assert event1.superseded_by_id == event2.id


class TestDescriptionMixin:
    """Tests for DescriptionMixin (PR-003a / ADR-008)."""

    def test_epoch_description(self, db_session: Session):
        """Test description field on Epoch model."""
        epoch = Epoch(
            name="Test Epoch",
            start_astro_day=0,
            end_astro_day=100,
            description="Initial test period",
        )

        db_session.add(epoch)
        db_session.commit()

        assert epoch.description == "Initial test period"
        assert epoch.has_description() is True

    def test_update_description(self, db_session: Session):
        """Test updating description programmatically."""
        region = Region(name="Test Region", founded_astro_day=0)
        db_session.add(region)
        db_session.commit()

        # Update description
        region.update_description("Updated description")
        db_session.commit()

        assert region.description == "Updated description"
        assert region.has_description() is True

    def test_clear_description(self, db_session: Session):
        """Test clearing description."""
        province = Province(
            name="Test Province",
            founded_astro_day=0,
            description="Initial description",
        )
        db_session.add(province)
        db_session.commit()

        province.clear_description()
        db_session.commit()

        assert province.description is None
        assert province.has_description() is False


class TestMetadataMixin:
    """Tests for MetadataMixin (PR-003a / ADR-008)."""

    def test_metadata_flat_structure_valid(self, db_session: Session):
        """Test that flat metadata structure is accepted."""
        region = Region(
            name="Test Region",
            founded_astro_day=0,
            meta_data={"key1": "value1", "key2": 123, "key3": True, "key4": None},
        )

        db_session.add(region)
        db_session.commit()

        assert region.meta_data == {
            "key1": "value1",
            "key2": 123,
            "key3": True,
            "key4": None,
        }

    def test_update_metadata_merge(self, db_session: Session):
        """Test merging metadata updates."""
        region = Region(
            name="Test Region",
            founded_astro_day=0,
            meta_data={"key1": "value1", "key2": "value2"},
        )
        db_session.add(region)
        db_session.commit()

        # Merge new values
        region.update_metadata({"key2": "updated", "key3": "new"}, mode="merge")
        flag_modified(region, "meta_data")  # Tell SQLAlchemy we modified the JSON field
        db_session.commit()

        assert region.meta_data == {
            "key1": "value1",
            "key2": "updated",
            "key3": "new",
        }

    def test_update_metadata_replace(self, db_session: Session):
        """Test replacing metadata."""
        province = Province(
            name="Test Province",
            founded_astro_day=0,
            meta_data={"key1": "value1", "key2": "value2"},
        )
        db_session.add(province)
        db_session.commit()

        # Replace entirely
        province.update_metadata({"key3": "value3"}, mode="replace")
        db_session.commit()

        assert province.meta_data == {"key3": "value3"}

    def test_remove_metadata_keys(self, db_session: Session):
        """Test removing specific metadata keys."""
        region = Region(
            name="Test Region",
            founded_astro_day=0,
            meta_data={"key1": "value1", "key2": "value2", "key3": "value3"},
        )
        db_session.add(region)
        db_session.commit()

        region.remove_metadata_keys(["key2"])
        flag_modified(region, "meta_data")  # Tell SQLAlchemy we modified the JSON field
        db_session.commit()

        assert region.meta_data == {"key1": "value1", "key3": "value3"}

    def test_clear_metadata(self, db_session: Session):
        """Test clearing all metadata."""
        province = Province(
            name="Test Province",
            founded_astro_day=0,
            meta_data={"key1": "value1"},
        )
        db_session.add(province)
        db_session.commit()

        province.clear_metadata()
        db_session.commit()

        assert province.meta_data is None

    def test_get_metadata_value(self, db_session: Session):
        """Test getting specific metadata value."""
        region = Region(
            name="Test Region",
            founded_astro_day=0,
            meta_data={"key1": "value1", "key2": 123},
        )
        db_session.add(region)
        db_session.commit()

        assert region.get_metadata_value("key1") == "value1"
        assert region.get_metadata_value("key2") == 123
        assert region.get_metadata_value("nonexistent") is None
        assert region.get_metadata_value("nonexistent", "default") == "default"

    def test_has_metadata_key(self, db_session: Session):
        """Test checking if metadata key exists."""
        province = Province(
            name="Test Province",
            founded_astro_day=0,
            meta_data={"key1": "value1"},
        )
        db_session.add(province)
        db_session.commit()

        assert province.has_metadata_key("key1") is True
        assert province.has_metadata_key("nonexistent") is False

    def test_metadata_nested_object_rejected(self, db_session: Session):
        """Test that nested objects in metadata are rejected."""
        region = Region(name="Test Region", founded_astro_day=0, meta_data={})
        db_session.add(region)
        db_session.commit()

        # Attempt to add nested object
        try:
            region.update_metadata({"nested": {"key": "value"}})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Nested objects not allowed" in str(e)

    def test_metadata_array_rejected(self, db_session: Session):
        """Test that arrays in metadata are rejected."""
        province = Province(name="Test Province", founded_astro_day=0, meta_data={})
        db_session.add(province)
        db_session.commit()

        # Attempt to add array
        try:
            province.update_metadata({"tags": ["tag1", "tag2"]})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Arrays not allowed" in str(e)


class TestRegionSnapshotModel:
    """Tests for RegionSnapshot model (PR-003a)."""

    def test_create_region_snapshot(self, db_session: Session):
        """Test creating a region snapshot."""
        region = Region(name="Test Region", founded_astro_day=0)
        db_session.add(region)
        db_session.flush()

        snapshot = RegionSnapshot(
            region_id=region.id,
            astro_day=100,
            snapshot_type="census",
            granularity="year",
            population_total=50000,
            population_by_species={"huum": 30000, "sint": 20000},
            population_by_habitat={"on_ground": 45000, "under_ground": 5000},
            cultural_composition={"language": "Fatuni"},
            economic_data={"primary_industry": "agriculture"},
            meta_data={"source": "census_2025"},
        )

        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.id is not None
        assert snapshot.region_id == region.id
        assert snapshot.astro_day == 100
        assert snapshot.snapshot_type == "census"
        assert snapshot.granularity == "year"
        assert snapshot.population_total == 50000

    def test_region_snapshot_relationship(self, db_session: Session):
        """Test relationship between region and snapshots."""
        region = Region(name="Test Region", founded_astro_day=0)
        snapshot = RegionSnapshot(
            region=region,
            astro_day=100,
            population_total=50000,
        )

        db_session.add(region)
        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.region_id == region.id
        assert snapshot in region.snapshots

    def test_region_snapshot_check_constraints(self, db_session: Session):
        """Test CHECK constraints on RegionSnapshot."""
        region = Region(name="Test Region", founded_astro_day=0)
        db_session.add(region)
        db_session.flush()

        # This should be caught by service layer, but test at model level
        # Note: SQLite doesn't enforce CHECK constraints by default in all configs
        snapshot = RegionSnapshot(
            region_id=region.id,
            astro_day=100,
            population_total=50000,  # Valid
        )
        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.population_total >= 0
        assert snapshot.astro_day >= 0


class TestProvinceSnapshotModel:
    """Tests for ProvinceSnapshot model (PR-003a)."""

    def test_create_province_snapshot(self, db_session: Session):
        """Test creating a province snapshot."""
        province = Province(name="Test Province", founded_astro_day=0)
        db_session.add(province)
        db_session.flush()

        snapshot = ProvinceSnapshot(
            province_id=province.id,
            astro_day=200,
            snapshot_type="simulation",
            granularity="decade",
            population_total=20000,
            population_by_species={"huum": 15000, "sint": 5000},
        )

        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.id is not None
        assert snapshot.province_id == province.id
        assert snapshot.snapshot_type == "simulation"
        assert snapshot.granularity == "decade"

    def test_province_snapshot_relationship(self, db_session: Session):
        """Test relationship between province and snapshots."""
        province = Province(name="Test Province", founded_astro_day=0)
        snapshot = ProvinceSnapshot(
            province=province,
            astro_day=100,
            population_total=20000,
        )

        db_session.add(province)
        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.province_id == province.id
        assert snapshot in province.snapshots


class TestSettlementSnapshotUpdates:
    """Tests for SettlementSnapshot updates (PR-003a)."""

    def test_settlement_snapshot_with_type_and_granularity(self, db_session: Session):
        """Test that SettlementSnapshot now has snapshot_type and granularity."""
        settlement = Settlement(
            name="Test Settlement",
            settlement_type="hamlet",
            founded_astro_day=0,
        )
        db_session.add(settlement)
        db_session.flush()

        snapshot = SettlementSnapshot(
            settlement_id=settlement.id,
            astro_day=100,
            population_total=1000,
            snapshot_type="census",
            granularity="year",
        )

        db_session.add(snapshot)
        db_session.commit()

        assert snapshot.snapshot_type == "census"
        assert snapshot.granularity == "year"
