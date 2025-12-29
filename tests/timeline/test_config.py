"""
Tests for configuration loading and management.
"""

from pathlib import Path

import pytest

from app_timeline.config import DatabaseConfig, TimelineConfig


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""

    def test_sqlite_connection_string(self):
        """Test SQLite connection string generation."""
        config = DatabaseConfig(path="data/test.db", dialect="sqlite")
        assert config.connection_string == "sqlite:///data/test.db"

    def test_postgresql_connection_string(self):
        """Test PostgreSQL connection string passthrough."""
        pg_url = "postgresql://user:pass@localhost/dbname"
        config = DatabaseConfig(path=pg_url, dialect="postgresql")
        assert config.connection_string == pg_url

    def test_unsupported_dialect(self):
        """Test error on unsupported database dialect."""
        config = DatabaseConfig(path="data/test.db", dialect="mysql")
        with pytest.raises(ValueError, match="Unsupported database dialect"):
            _ = config.connection_string

    def test_default_values(self):
        """Test default configuration values."""
        config = DatabaseConfig(path="test.db")
        assert config.dialect == "sqlite"
        assert config.echo is False


class TestTimelineConfig:
    """Tests for TimelineConfig class."""

    def test_load_from_yaml(self, test_config_yaml: Path):
        """Test loading configuration from YAML file."""
        config = TimelineConfig.from_yaml(test_config_yaml)

        # Check database config
        assert config.database.dialect == "sqlite"
        assert config.database.echo is False

        # Check lists
        assert "ring_town" in config.settlement_types
        assert "market_town" in config.settlement_types
        assert "huum" in config.species
        assert "sint" in config.species
        assert "on_ground" in config.habitats
        assert "person" in config.entity_types
        assert "founding" in config.event_types
        assert "moderate" in config.route_difficulties
        assert "road" in config.route_types

        # Check app config
        assert config.app.version == "0.1.0-test"
        assert config.app.default_astro_day == 0

    def test_missing_yaml_file(self):
        """Test error when YAML file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            TimelineConfig.from_yaml(Path("/nonexistent/config.yaml"))

    def test_config_defaults(self, test_config: TimelineConfig):
        """Test configuration has sensible defaults."""
        # Even with minimal config, these should be lists (possibly empty)
        assert isinstance(test_config.settlement_types, list)
        assert isinstance(test_config.species, list)
        assert isinstance(test_config.habitats, list)
        assert isinstance(test_config.entity_types, list)
        assert isinstance(test_config.event_types, list)
        assert isinstance(test_config.route_difficulties, list)
        assert isinstance(test_config.route_types, list)
