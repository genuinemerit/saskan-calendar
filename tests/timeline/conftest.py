"""
Pytest configuration and shared fixtures for timeline tests.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app_timeline.config import TimelineConfig, reset_config
from app_timeline.db import get_engine, get_session, reset_engine
from app_timeline.models import Base


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_config_yaml(temp_db_path: Path) -> Generator[Path, None, None]:
    """Create a temporary test configuration YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_content = f"""
database:
  path: "{temp_db_path}"
  dialect: "sqlite"
  echo: false

settlement_types:
  - ring_town
  - market_town
  - hamlet

species:
  - huum
  - sint

habitats:
  - on_ground
  - in_sea

entity_types:
  - person
  - organization

event_types:
  - founding
  - battle

route_difficulties:
  - easy
  - moderate
  - difficult

route_types:
  - trail
  - road

app:
  version: "0.1.0-test"
  default_astro_day: 0
"""
        f.write(config_content)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    if config_path.exists():
        config_path.unlink()


@pytest.fixture
def test_config(test_config_yaml: Path) -> Generator[TimelineConfig, None, None]:
    """Load test configuration."""
    reset_config()
    config = TimelineConfig.from_yaml(test_config_yaml)

    yield config

    reset_config()


@pytest.fixture
def test_db(test_config: TimelineConfig) -> Generator[None, None, None]:
    """Create a test database with all tables."""
    reset_engine()
    engine = get_engine()
    Base.metadata.create_all(engine)

    yield

    Base.metadata.drop_all(engine)
    reset_engine()


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    session = get_session()

    yield session

    session.rollback()
    session.close()
