"""
app_timeline.simulation.config

Configuration dataclass for simulation parameters.

PR-003b: Defines SimulationConfig for controlling simulation behavior,
adapted from app_maps SimulationConfig pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class SimulationConfig:
    """
    Configuration for macro-scale demographic simulation runs.

    Provides parameters for:
    - Execution control (seed, chunk size)
    - Population dynamics (growth rates per species)
    - Carrying capacity factors
    - Migration parameters (for future use)
    - Validation thresholds

    Example usage:
        config = SimulationConfig(
            seed=42,
            growth_rates={"huum": 0.004, "sint": 0.006},
            base_carrying_capacity=50000
        )
    """

    # === Execution Parameters ===

    seed: Optional[int] = None
    """Random seed for deterministic simulation (None = non-deterministic)"""

    chunk_size_days: int = 36525
    """Chunk size for incremental simulation (default: 100 years ≈ 36525 days)"""

    # === Growth Rate Parameters ===

    growth_rates: Dict[str, float] = field(default_factory=dict)
    """
    Intrinsic growth rates per species (annual rate).

    Example: {"huum": 0.004, "sint": 0.006, "mixed": 0.005}
    A rate of 0.004 means 0.4% annual growth.
    """

    # === Carrying Capacity Parameters ===

    base_carrying_capacity: int = 50000
    """Base carrying capacity K_base (default for regions)"""

    environmental_factor_range: Tuple[float, float] = (0.8, 1.2)
    """
    Range for random environmental factor (climate, terrain quality).
    Sampled uniformly at simulation start.
    """

    infrastructure_factor_initial: float = 1.0
    """
    Initial infrastructure factor (irrigation, technology).
    Can be modified by events during simulation.
    """

    location_factor_range: Tuple[float, float] = (0.9, 1.1)
    """
    Range for random location factor (trade routes, resource access).
    Sampled uniformly at simulation start.
    """

    # === Migration Parameters (Future Use) ===

    migration_enabled: bool = False
    """Enable inter-regional migration (not implemented in PR-003b)"""

    migration_rate_range: Tuple[float, float] = (0.01, 0.05)
    """Range for migration rates (for future implementation)"""

    # === Validation Parameters ===

    max_growth_rate_per_step: float = 0.10
    """
    Maximum allowed growth rate per simulation step (default: 10% per year).
    Used for validation warnings.
    """

    negative_population_tolerance: int = 0
    """
    Tolerance for negative populations (default: 0, no negatives allowed).
    Triggers validation warnings if exceeded.
    """


def load_simulation_config_from_settings(
    entity_type: str,
    seed: Optional[int] = None,
    chunk_size_days: Optional[int] = None,
    overrides: Optional[Dict] = None
) -> SimulationConfig:
    """
    Load simulation configuration from settings.yaml with optional overrides.

    This function reads default simulation parameters from the settings.yaml
    configuration file and allows selective overrides for specific runs.

    :param entity_type: Entity type ("region" or "province") for base K selection
    :param seed: Optional random seed override
    :param chunk_size_days: Optional chunk size override
    :param overrides: Optional dictionary of additional overrides
    :return: Configured SimulationConfig instance
    """
    from pathlib import Path
    import yaml

    # Read settings.yaml directly
    config_path = Path(__file__).parent.parent.parent / "config" / "timeline" / "settings.yaml"

    if not config_path.exists():
        # Fallback to defaults if config not found
        sim_settings = {}
    else:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            sim_settings = data.get("simulation", {})

    # Extract growth rates
    growth_rates = sim_settings.get("growth_rates", {})

    # Extract base carrying capacity for entity type
    base_K_settings = sim_settings.get("base_carrying_capacity", {})
    base_K = base_K_settings.get(entity_type, 50000)  # Default fallback

    # Extract factor ranges
    env_range = sim_settings.get("environmental_factor_range", [0.8, 1.2])
    loc_range = sim_settings.get("location_factor_range", [0.9, 1.1])
    infra_initial = sim_settings.get("infrastructure_factor_initial", 1.0)

    # Extract chunk size (with override)
    default_chunk_size = sim_settings.get("chunk_size_days", 36525)
    chunk_size = chunk_size_days if chunk_size_days is not None else default_chunk_size

    # Build config
    sim_config = SimulationConfig(
        seed=seed,
        chunk_size_days=chunk_size,
        growth_rates=growth_rates,
        base_carrying_capacity=base_K,
        environmental_factor_range=tuple(env_range),
        infrastructure_factor_initial=infra_initial,
        location_factor_range=tuple(loc_range),
    )

    # Apply overrides if provided
    if overrides:
        for key, value in overrides.items():
            if hasattr(sim_config, key):
                setattr(sim_config, key, value)

    return sim_config
