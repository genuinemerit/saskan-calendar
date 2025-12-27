from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .models import Region, Settlement


@dataclass
class SimulationConfig:
    steps: int = 10
    seed: Optional[int] = None
    scenario: Optional[str] = None
    tick_unit: str = "year"
    tick_length: float = 1.0
    # Spatial grid
    block_size_km: int = 50
    region_cols: int = 40
    region_rows: int = 30
    # Population & growth
    initial_population: int = 5000
    roles_distribution: Dict[str, float] = None  # set in __post_init__
    growth_rate_range: Tuple[float, float] = (0.03, 0.07)
    carrying_capacity: int = 850
    arable_fraction: float = 0.4
    arable_support_range: Tuple[int, int] = (60, 200)  # people per km^2
    pollination_penalty: float = -0.01  # manual pollination drag on growth
    irrigation_growth_bonus: float = 0.002  # incremental bonus per year as canals improve
    irrigation_bonus_cap: float = 0.02
    fresh_water_capacity_bonus: float = 0.2
    sea_water_capacity_bonus: float = 0.12
    fertile_bonus: float = 0.25
    hamlet_support_ratio: float = 0.4  # fraction of hamlet pop that can support its parent
    hamlet_max_population: int = 5000
    market_town_population_threshold: int = 1000
    market_value_threshold: int = 10  # placeholder economic score
    max_market_towns_within_radius: int = 2
    market_radius_km: float = 30.0
    # Migration / travel to first settlement
    travel_years: int = 10
    travel_loss_rate_range: Tuple[float, float] = (0.02, 0.04)
    # Settlement formation
    new_settlement_chance: float = 0.25
    new_route_chance: float = 0.35
    new_settlement_population: Tuple[int, int] = (40, 90)
    max_settlements: int = 15
    max_routes: int = 30
    # Hazards
    hazard_chance: float = 0.1
    hazard_population_loss: Tuple[int, int] = (5, 25)
    # Shocks & recovery
    shock_chance: float = 0.18
    shock_loss_fraction: Tuple[float, float] = (0.05, 0.25)
    recovery_chance: float = 0.14
    recovery_boost: Tuple[float, float] = (0.0075, 0.01)  # 0.75% to 1% growth boost
    recovery_duration: int = 2
    # Out-migration
    out_migration_chance: float = 0.08
    out_migration_fraction: Tuple[float, float] = (0.03, 0.08)
    out_migration_bias: Tuple[int, int] = (0, 0)  # directional bias (km) for new sites
    affinity_distance_scale: float = 300.0  # km over which ties decay
    affinity_floor: float = 0.2
    downriver_migration_step: int = 0  # if >0, force a large out-migration at this step
    downriver_migration_fraction: float = 0.12

    def __post_init__(self) -> None:
        if self.roles_distribution is None:
            self.roles_distribution = {"walkers": 0.9, "riders": 0.08, "guides": 0.02}


def region_from_config(config: SimulationConfig) -> Region:
    width = config.block_size_km * config.region_cols
    height = config.block_size_km * config.region_rows
    return Region(
        name="Saskan Lands",
        width=width,
        height=height,
        description="Grid 40x30 blocks (~50km each), coastal plains east, highlands west.",
    )


def block_center(config: SimulationConfig, col: int, row: int) -> Tuple[int, int]:
    """Convert 1-based block indices (C?, R?) to km coordinates (x east, y south)."""
    x = int((col - 0.5) * config.block_size_km)
    y = int((row - 0.5) * config.block_size_km)
    return (x, y)


def compute_carrying_capacity(config: SimulationConfig, blocks: int = 1) -> int:
    """Estimate carrying capacity for a given number of blocks."""
    block_area = config.block_size_km * config.block_size_km
    arable_area = block_area * config.arable_fraction * blocks
    density_low, density_high = config.arable_support_range
    density = (density_low + density_high) / 2
    return int(arable_area * density)


def compute_migration_survivors(config: SimulationConfig, rng) -> Dict[str, int]:
    """Simulate travel attrition for the great migration."""
    population = config.initial_population
    total_losses = 0
    for _ in range(config.travel_years):
        loss_rate = rng.uniform(*config.travel_loss_rate_range)
        loss = int(population * loss_rate)
        population -= loss
        total_losses += loss
    roles = {}
    for role, pct in config.roles_distribution.items():
        roles[role] = int(population * pct)
    # Adjust rounding
    roles["walkers"] += population - sum(roles.values())
    return {"survivors": population, "losses": total_losses, "roles": roles}


def default_settlements(config: SimulationConfig, rng) -> List[Settlement]:
    """Seed the world with a few starting settlements."""
    if config.scenario == "great-migration":
        return _great_migration_settlements(config, rng)

    low, high = config.growth_rate_range
    carrying_capacity = config.carrying_capacity
    harbor_loc = block_center(config, col=8, row=12)
    stoneford_loc = block_center(config, col=16, row=18)
    northwatch_loc = block_center(config, col=24, row=8)
    return [
        Settlement(
            name="Harborfall",
            population=180,
            location=harbor_loc,
            growth_rate=low,
            carrying_capacity=carrying_capacity,
        ),
        Settlement(
            name="Stoneford",
            population=120,
            location=stoneford_loc,
            growth_rate=(low + high) / 2,
            carrying_capacity=carrying_capacity,
        ),
        Settlement(
            name="Northwatch",
            population=90,
            location=northwatch_loc,
            growth_rate=high,
            carrying_capacity=carrying_capacity,
        ),
    ]


def _great_migration_settlements(config: SimulationConfig, rng) -> List[Settlement]:
    survivors = compute_migration_survivors(config, rng)
    ingar_location = block_center(config, col=33, row=14)
    capacity = compute_carrying_capacity(config, blocks=1)
    growth_low, growth_high = config.growth_rate_range
    growth = rng.uniform(growth_low, growth_high)
    metadata = {
        "travel_years": config.travel_years,
        "travel_losses": survivors["losses"],
        "roles": survivors["roles"],
        "notes": "Founded at Pavan River bend after bypassing mountain at R12/C34.",
        "grid_ref": {"col": 33, "row": 14},
        "water": "fresh",
        "fertile": True,
    }
    ingar = Settlement(
        name="Ingar",
        population=survivors["survivors"],
        location=ingar_location,
        growth_rate=growth,
        carrying_capacity=capacity,
        metadata=metadata,
    )
    return [ingar]


SCENARIO_PRESETS: Dict[str, Dict] = {
    "baseline": {"seed": 42, "description": "Default growth and terrain assumptions."},
    "northern-expansion": {"seed": 7, "description": "Bias toward northern expansions."},
    "coastal-boom": {"seed": 99, "description": "More eastern/coastal growth variants."},
    "great-migration": {"seed": 1234, "description": "Arrival of the huum at Ingar after river descent."},
}


def apply_scenario(config: SimulationConfig) -> SimulationConfig:
    """Derive seed/config tweaks from a named scenario if provided."""
    if config.scenario:
        preset = SCENARIO_PRESETS.get(config.scenario)
        if preset and config.seed is None:
            config.seed = preset.get("seed")
        if config.scenario == "great-migration":
            # Higher max settlements/routes for the 2k-year horizon.
            config.max_settlements = max(config.max_settlements, 60)
            config.max_routes = max(config.max_routes, 120)
            # Increase carrying capacity to reflect fertile floodplain.
            config.carrying_capacity = compute_carrying_capacity(config, blocks=1)
            # Bias out-migration downriver toward the bay.
            config.out_migration_bias = (80, -40)
            config.downriver_migration_step = 6
            config.downriver_migration_fraction = 0.15
    return config
