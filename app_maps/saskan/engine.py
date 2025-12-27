from __future__ import annotations

import math
import random
from itertools import combinations
from typing import List, Optional, Tuple

from .models import Event, Route, Settlement, SimulationState
from .settings import SimulationConfig, apply_scenario, default_settlements, region_from_config


class SaskanEngine:
    """Step-based simulator for the Saskan Lands."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = apply_scenario(config or SimulationConfig())
        self.random = random.Random(self.config.seed)
        self.flow_modifier = self.config.pollination_penalty
        self.recovery_steps_remaining = 0
        self.recovery_boost = 0.0
        self.irrigation_progress = 0.0
        self.downriver_sent = False
        self.state = SimulationState(
            step=0,
            tick_unit=self.config.tick_unit,
            tick_length=self.config.tick_length,
            region=region_from_config(self.config),
            settlements=default_settlements(self.config, self.random),
            routes=[],
        )

    def step(self) -> List[Event]:
        self.state.step += 1
        events: List[Event] = []
        events.extend(self._update_flow())
        events.extend(self._apply_growth())
        events.extend(self._apply_hazards())
        events.extend(self._apply_shocks())
        events.extend(self._update_market_status())
        events.extend(self._maybe_found_settlement())
        events.extend(self._maybe_force_downriver())
        events.extend(self._maybe_out_migrate())
        events.extend(self._maybe_build_route())
        return events

    def _apply_growth(self) -> List[Event]:
        events: List[Event] = []
        for settlement in self.state.settlements:
            jitter = self.random.uniform(-0.01, 0.01)
            growth = max(
                0.0,
                settlement.growth_rate
                + jitter
                + self.flow_modifier
                + self.irrigation_progress
                + self.recovery_boost,
            )
            effective_capacity = self._effective_carrying_capacity(settlement)
            new_population = int(settlement.population * (1 + growth))
            new_population = min(new_population, effective_capacity)
            delta = new_population - settlement.population
            settlement.population = new_population
            if delta > 0:
                events.append(
                    Event(
                        step=self.state.step,
                        message=f"{settlement.name} grew by {delta} to {settlement.population}.",
                    )
                )
        return events

    def _maybe_found_settlement(self) -> List[Event]:
        events: List[Event] = []
        if len(self.state.settlements) >= self.config.max_settlements:
            return events
        if self.random.random() > self.config.new_settlement_chance:
            return events

        parent = self.random.choice(self.state.settlements)
        location = self._jitter_location(parent.location, radius=10)
        pop_low, pop_high = self.config.new_settlement_population
        growth_low, growth_high = self.config.growth_rate_range
        new_name = self._generate_name(len(self.state.settlements))
        affinity = self._compute_affinity(parent.location, location)
        new_settlement = Settlement(
            name=new_name,
            population=self.random.randint(pop_low, pop_high),
            location=location,
            growth_rate=self.random.uniform(growth_low, growth_high),
            carrying_capacity=self.config.carrying_capacity,
            metadata={"parent": parent.name, "type": "hamlet", "affinity": affinity},
        )
        self.state.settlements.append(new_settlement)
        events.append(
            Event(
                step=self.state.step,
                message=f"Founded {new_settlement.name} near {parent.name} at {new_settlement.location}.",
            )
        )
        # Connect to parent automatically to keep the graph cohesive.
        new_route = self._build_route(parent, new_settlement)
        if new_route:
            self.state.routes.append(new_route)
            events.append(
                Event(
                    step=self.state.step,
                    message=(
                        f"Trail opened between {new_route.origin} and {new_route.destination} "
                        f"({new_route.distance:.1f} units)."
                    ),
                )
            )
        return events

    def _maybe_build_route(self) -> List[Event]:
        events: List[Event] = []
        if len(self.state.routes) >= self.config.max_routes:
            return events
        if len(self.state.settlements) < 2:
            return events
        if self.random.random() > self.config.new_route_chance:
            return events

        existing_keys = {route.key() for route in self.state.routes}
        candidates: List[Tuple[Settlement, Settlement]] = []
        for a, b in combinations(self.state.settlements, 2):
            if (a.name, b.name) in existing_keys or (b.name, a.name) in existing_keys:
                continue
            candidates.append((a, b))
        if not candidates:
            return events

        origin, destination = self.random.choice(candidates)
        new_route = self._build_route(origin, destination)
        if new_route:
            self.state.routes.append(new_route)
            events.append(
                Event(
                    step=self.state.step,
                    message=(
                        f"Surveyed route {origin.name} -> {destination.name} "
                        f"({new_route.distance:.1f} units)."
                    ),
                )
            )
        return events

    def _build_route(self, origin: Settlement, destination: Settlement) -> Optional[Route]:
        distance = self._distance(origin.location, destination.location)
        difficulty = 1 + self.random.uniform(0, 0.4)
        return Route(
            origin=origin.name,
            destination=destination.name,
            distance=distance,
            difficulty=difficulty,
        )

    def _jitter_location(self, location: Tuple[int, int], radius: int = 8) -> Tuple[int, int]:
        x, y = location
        dx = self.random.randint(-radius, radius)
        dy = self.random.randint(-radius, radius)
        new_x = max(0, min(self.state.region.width, x + dx))
        new_y = max(0, min(self.state.region.height, y + dy))
        return (new_x, new_y)

    def _biased_location(self, origin: Tuple[int, int], bias: Tuple[int, int], radius: int = 8) -> Tuple[int, int]:
        x, y = origin
        dx_bias, dy_bias = bias
        dx = self.random.randint(-radius, radius) + dx_bias
        dy = self.random.randint(-radius, radius) + dy_bias
        new_x = max(0, min(self.state.region.width, x + dx))
        new_y = max(0, min(self.state.region.height, y + dy))
        return (new_x, new_y)

    def _distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.hypot(b[0] - a[0], b[1] - a[1])

    def _generate_name(self, index: int) -> str:
        syllables = [
            "Ska",
            "Kan",
            "Tor",
            "Vel",
            "Mer",
            "Lan",
            "Ost",
            "Rim",
            "Tal",
            "Fen",
        ]
        prefix = self.random.choice(syllables)
        suffix = self.random.choice(syllables)
        return f"{prefix}{suffix}-{index}"

    def _apply_hazards(self) -> List[Event]:
        """Hook for hazards/conflicts; currently a light stochastic population loss."""
        events: List[Event] = []
        if not self.state.settlements:
            return events
        if self.random.random() > self.config.hazard_chance:
            return events

        target = self.random.choice(self.state.settlements)
        loss_low, loss_high = self.config.hazard_population_loss
        loss = self.random.randint(loss_low, loss_high)
        target.population = max(0, target.population - loss)
        hazard_types = ["wolves", "bandits", "plague", "harsh winter"]
        hazard = self.random.choice(hazard_types)
        events.append(
            Event(
                step=self.state.step,
                message=f"Hazard ({hazard}) hit {target.name}, population -{loss} to {target.population}.",
            )
        )
        return events

    def _apply_shocks(self) -> List[Event]:
        """Major shocks (famine/flood/fire/conflict) and recoveries affecting productivity."""
        events: List[Event] = []
        if not self.state.settlements:
            return events

        triggered_shock = False
        if self.random.random() < self.config.shock_chance:
            target = self.random.choice(self.state.settlements)
            frac_low, frac_high = self.config.shock_loss_fraction
            loss_fraction = self.random.uniform(frac_low, frac_high)
            loss = int(target.population * loss_fraction)
            target.population = max(0, target.population - loss)
            self.flow_modifier -= loss_fraction / 2  # dampen productivity
            events.append(
                Event(
                    step=self.state.step,
                    message=(
                        f"Shock hit {target.name}: -{loss} ({loss_fraction:.0%}) from famine/conflict/flood."
                    ),
                )
            )
            triggered_shock = True

        if not triggered_shock and self.random.random() < self.config.recovery_chance:
            boost_low, boost_high = self.config.recovery_boost
            self.recovery_boost = self.random.uniform(boost_low, boost_high)
            self.recovery_steps_remaining = self.config.recovery_duration
            events.append(
                Event(
                    step=self.state.step,
                    message=f"Favorable conditions: temporary productivity boost {self.recovery_boost:.2%} "
                    f"for {self.recovery_steps_remaining} {self.state.tick_unit}s.",
                )
            )
        return events

    def _update_flow(self) -> List[Event]:
        """Adjust long-term flow: pollination penalty baseline, recoveries decay, irrigation gains."""
        events: List[Event] = []
        # Gradual improvement when no shocks: modest uptick, capped.
        self.flow_modifier = min(self.flow_modifier + 0.004, 0.05)
        # Recovery decay
        if self.recovery_steps_remaining > 0:
            self.recovery_steps_remaining -= 1
            if self.recovery_steps_remaining == 0:
                self.recovery_boost = 0.0
        # Irrigation progress accumulates
        self.irrigation_progress = min(
            self.irrigation_progress + self.config.irrigation_growth_bonus, self.config.irrigation_bonus_cap
        )
        return events

    def _maybe_out_migrate(self) -> List[Event]:
        events: List[Event] = []
        if len(self.state.settlements) >= self.config.max_settlements:
            return events
        if self.random.random() > self.config.out_migration_chance:
            return events
        viable = [s for s in self.state.settlements if s.population > 300]
        if not viable:
            return events
        parent = self.random.choice(viable)
        frac_low, frac_high = self.config.out_migration_fraction
        frac = self.random.uniform(frac_low, frac_high)
        migrants = max(20, int(parent.population * frac))
        parent.population = max(0, parent.population - migrants)
        location = self._biased_location(parent.location, self.config.out_migration_bias, radius=20)
        growth_low, growth_high = self.config.growth_rate_range
        affinity = self._compute_affinity(parent.location, location)
        new_settlement = Settlement(
            name=self._generate_name(len(self.state.settlements)),
            population=migrants,
            location=location,
            growth_rate=self.random.uniform(growth_low, growth_high),
            carrying_capacity=parent.carrying_capacity,
            metadata={"parent": parent.name, "type": "hamlet", "affinity": affinity},
        )
        self.state.settlements.append(new_settlement)
        events.append(
            Event(
                step=self.state.step,
                message=(
                    f"Out-migration: {migrants} left {parent.name} to found {new_settlement.name} at "
                    f"{new_settlement.location}."
                ),
            )
        )
        new_route = self._build_route(parent, new_settlement)
        if new_route:
            self.state.routes.append(new_route)
            events.append(
                Event(
                    step=self.state.step,
                    message=(
                        f"Trade path opened between {new_route.origin} and {new_route.destination} "
                        f"({new_route.distance:.1f} units)."
                    ),
            )
        )
        return events

    def _maybe_force_downriver(self) -> List[Event]:
        """Single forced out-migration downriver (toward the bay)."""
        events: List[Event] = []
        if self.downriver_sent:
            return events
        if self.config.downriver_migration_step and self.state.step == self.config.downriver_migration_step:
            parent = next((s for s in self.state.settlements if s.name == "Ingar"), None)
            if not parent:
                parent = self.state.settlements[0] if self.state.settlements else None
            if not parent:
                return events
            frac = self.config.downriver_migration_fraction
            migrants = max(200, int(parent.population * frac))
            parent.population = max(0, parent.population - migrants)
            bias = (self.config.out_migration_bias[0] * 2, self.config.out_migration_bias[1] * 2)
            location = self._biased_location(parent.location, bias, radius=40)
            affinity = self._compute_affinity(parent.location, location)
            growth_low, growth_high = self.config.growth_rate_range
            new_settlement = Settlement(
                name=self._generate_name(len(self.state.settlements)),
                population=migrants,
                location=location,
                growth_rate=self.random.uniform(growth_low, growth_high),
                carrying_capacity=parent.carrying_capacity,
                metadata={"parent": parent.name, "type": "hamlet", "affinity": affinity, "water": "fresh"},
            )
            self.state.settlements.append(new_settlement)
            events.append(
                Event(
                    step=self.state.step,
                    message=(
                        f"Downriver migration: {migrants} left {parent.name} to found {new_settlement.name} "
                        f"at {new_settlement.location}."
                    ),
                )
            )
            new_route = self._build_route(parent, new_settlement)
            if new_route:
                self.state.routes.append(new_route)
                events.append(
                    Event(
                        step=self.state.step,
                        message=(
                            f"River path opened between {new_route.origin} and {new_route.destination} "
                            f"({new_route.distance:.1f} units)."
                        ),
                    )
                )
            self.downriver_sent = True
        return events

    def _compute_affinity(self, parent_loc: Tuple[int, int], child_loc: Tuple[int, int]) -> float:
        dist = self._distance(parent_loc, child_loc)
        scale = self.config.affinity_distance_scale
        affinity = max(self.config.affinity_floor, 1 - dist / scale)
        return round(affinity, 3)

    def _effective_carrying_capacity(self, settlement: Settlement) -> int:
        base = settlement.carrying_capacity
        meta = settlement.metadata or {}
        water = meta.get("water")
        if water == "fresh":
            base = int(base * (1 + self.config.fresh_water_capacity_bonus))
        elif water == "sea":
            base = int(base * (1 + self.config.sea_water_capacity_bonus))
        if meta.get("fertile"):
            base = int(base * (1 + self.config.fertile_bonus))

        if meta.get("type") in {"hamlet", "market-town"}:
            return min(base, self.config.hamlet_max_population)

        support = 0
        for h in self.state.settlements:
            if (h.metadata or {}).get("parent") == settlement.name and (h.metadata or {}).get("type") in {
                "hamlet",
                "market-town",
            }:
                support += int(h.population * self.config.hamlet_support_ratio)
        return base + support

    def _update_market_status(self) -> List[Event]:
        """Promote hamlets to market towns when they hit thresholds."""
        events: List[Event] = []
        for s in self.state.settlements:
            meta = s.metadata or {}
            if meta.get("type") == "hamlet":
                value_score = meta.get("value_score", 0)
                if s.population >= self.config.market_town_population_threshold or value_score >= self.config.market_value_threshold:
                    if not self._market_capacity_available(s):
                        continue
                    meta["type"] = "market-town"
                    meta["status"] = "candidate"
                    s.metadata = meta
                    events.append(
                        Event(
                            step=self.state.step,
                            message=f"{s.name} flagged as market-town candidate (pop {s.population}).",
                        )
                    )
        return events

    def _market_capacity_available(self, candidate: Settlement) -> bool:
        """Limit market towns per radius to avoid clustering."""
        radius = self.config.market_radius_km
        limit = self.config.max_market_towns_within_radius
        count = 0
        for s in self.state.settlements:
            if s is candidate:
                continue
            if (s.metadata or {}).get("type") == "market-town":
                if self._distance(s.location, candidate.location) <= radius:
                    count += 1
        return count < limit
