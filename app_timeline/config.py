"""
app_timeline.config

Configuration management for the timeline application.
Loads settings from YAML and provides type-safe runtime configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    path: str
    dialect: str = "sqlite"
    echo: bool = False

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        if self.dialect == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.dialect == "postgresql":
            return self.path  # Assume full postgres:// URL is provided
        else:
            raise ValueError(f"Unsupported database dialect: {self.dialect}")


@dataclass
class AppConfig:
    """Application-level configuration."""

    version: str = "0.1.0"
    default_astro_day: int = 0


@dataclass
class TimelineConfig:
    """Complete timeline application configuration."""

    database: DatabaseConfig
    settlement_types: List[str] = field(default_factory=list)
    species: List[str] = field(default_factory=list)
    habitats: List[str] = field(default_factory=list)
    entity_types: List[str] = field(default_factory=list)
    event_types: List[str] = field(default_factory=list)
    route_difficulties: List[str] = field(default_factory=list)
    route_types: List[str] = field(default_factory=list)
    app: AppConfig = field(default_factory=AppConfig)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> TimelineConfig:
        """Load configuration from YAML file."""
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Parse database config
        db_config = DatabaseConfig(**data.get("database", {}))

        # Parse app config
        app_data = data.get("app", {})
        app_config = AppConfig(**app_data)

        # Create timeline config
        return cls(
            database=db_config,
            settlement_types=data.get("settlement_types", []),
            species=data.get("species", []),
            habitats=data.get("habitats", []),
            entity_types=data.get("entity_types", []),
            event_types=data.get("event_types", []),
            route_difficulties=data.get("route_difficulties", []),
            route_types=data.get("route_types", []),
            app=app_config,
        )


# Global configuration instance
_config: Optional[TimelineConfig] = None


def get_config(config_path: Optional[Path] = None) -> TimelineConfig:
    """
    Get the global configuration instance.

    :param config_path: Optional path to configuration YAML file.
                       If not provided, uses default location.
    :return: TimelineConfig instance
    """
    global _config

    if _config is None:
        if config_path is None:
            # Default configuration location
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "timeline" / "settings.yaml"

        _config = TimelineConfig.from_yaml(config_path)

    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
