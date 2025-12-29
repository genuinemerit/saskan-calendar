"""
Tests for SQLAlchemy models and relationships.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app_timeline.models import (
    Entity,
    Event,
    Province,
    Region,
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
        province = Province(
            name="Test Province", founded_astro_day=0, region=region
        )

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
        event1 = Event(
            astro_day=100,
            event_type="battle",
            title="Original Event",
            description="Original description",
        )

        db_session.add(event1)
        db_session.flush()

        event2 = Event(
            astro_day=100,
            event_type="battle",
            title="Corrected Event",
            description="Corrected description",
        )

        db_session.add(event2)
        db_session.flush()

        # Mark first event as deprecated
        event1.is_deprecated = True
        event1.superseded_by_id = event2.id

        db_session.commit()

        assert event1.is_deprecated is True
        assert event1.superseded_by_id == event2.id
