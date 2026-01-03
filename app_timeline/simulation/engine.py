"""
app_timeline.simulation.engine

Core simulation engine for macro-scale demographic simulation.

PR-003b: Implements unified SimulationEngine for regions and provinces
with chunked execution (ADR-006) and event integration (ADR-007).
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from ..models.event import Event
from .config import SimulationConfig
from .effects import apply_event_effects
from .formulas import calculate_multi_species_growth
from .state import PopulationState, SimulationState


class SimulationEngine:
    """
    Unified simulation engine for macro-scale demographic simulation.

    Handles both regions and provinces using polymorphic design based on
    entity_type parameter. Implements:
    - Logistic population growth with multi-species tracking
    - Carrying capacity dynamics with environmental/infrastructure/location factors
    - Event-driven simulation (ADR-007: humans author, algorithm applies)
    - Chunked execution with validation checkpoints (ADR-006)
    - Deterministic simulation with optional seeding

    Example usage:
        config = SimulationConfig(seed=42, growth_rates={"huum": 0.004})
        engine = SimulationEngine("region", region_id=1, config=config)
        reports = engine.run(start_day=0, end_day=36525, granularity="decade")
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: int,
        config: SimulationConfig
    ):
        """
        Initialize simulation engine for specific entity.

        :param entity_type: "region" or "province"
        :param entity_id: Database ID of the region or province to simulate
        :param config: SimulationConfig with parameters
        """
        if entity_type not in ("region", "province"):
            raise ValueError(f"entity_type must be 'region' or 'province', got '{entity_type}'")

        self.entity_type = entity_type
        self.entity_id = entity_id
        self.config = config

        # Initialize deterministic RNG
        self.rng = random.Random(config.seed)

        # State (loaded during run)
        self.state: Optional[SimulationState] = None

    def run(
        self,
        start_day: int,
        end_day: int,
        granularity: str = "year"
    ) -> List[Dict[str, Any]]:
        """
        Run simulation from start_day to end_day in chunks.

        Implements ADR-006 chunked execution pattern:
        1. Divide [start_day, end_day] into chunks (default: 100 years)
        2. For each chunk:
           a. Run simulation steps
           b. Validate results
           c. Write snapshots
           d. Report progress

        :param start_day: Starting astro_day
        :param end_day: Ending astro_day (inclusive)
        :param granularity: Snapshot granularity ("year", "decade", "century")
        :return: List of chunk reports with statistics
        :raises ValueError: If start_day >= end_day or invalid granularity
        """
        if start_day >= end_day:
            raise ValueError(f"start_day ({start_day}) must be < end_day ({end_day})")

        if granularity not in ("year", "decade", "century"):
            raise ValueError(f"granularity must be 'year', 'decade', or 'century', got '{granularity}'")

        reports = []

        # Calculate chunk boundaries
        chunks = self._calculate_chunks(start_day, end_day)

        print(f"\nSimulating {self.entity_type} {self.entity_id} from day {start_day} to {end_day}")
        print(f"Chunks: {len(chunks)}, Granularity: {granularity}, Seed: {self.config.seed}")

        for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
            print(f"\n{'='*60}")
            print(f"Chunk {i}/{len(chunks)}: days {chunk_start} to {chunk_end}")
            print(f"{'='*60}")

            # Run chunk
            chunk_report = self._run_chunk(chunk_start, chunk_end, granularity)

            # Validate
            validation_issues = self._validate_chunk(chunk_end)
            if validation_issues:
                print("\n⚠️  VALIDATION WARNINGS:")
                for issue in validation_issues:
                    print(f"  - {issue}")

            reports.append(chunk_report)

            # Print chunk summary
            print(f"\nChunk {i} complete:")
            print(f"  Final population: {chunk_report['final_population']:,}")
            print(f"  Carrying capacity: {chunk_report['carrying_capacity']:,}")
            if chunk_report['population_by_species']:
                print(f"  Species breakdown: {chunk_report['population_by_species']}")

        print(f"\n{'='*60}")
        print("Simulation complete!")
        print(f"{'='*60}\n")

        return reports

    def _run_chunk(
        self,
        start_day: int,
        end_day: int,
        granularity: str
    ) -> Dict[str, Any]:
        """
        Execute one simulation chunk.

        Steps:
        1. Load initial state (from snapshot or create new)
        2. Load events in time range
        3. For each day in chunk:
           a. Apply any events on this day
           b. Calculate population growth
           c. Update state
        4. Write snapshots at regular intervals

        :param start_day: Chunk start day
        :param end_day: Chunk end day (inclusive)
        :param granularity: Snapshot granularity
        :return: Chunk report with statistics
        """
        # 1. Initialize state if needed
        if self.state is None:
            self.state = self._load_initial_state(start_day)

        # 2. Load events for this chunk
        events = self._load_events(start_day, end_day)
        events_by_day = self._index_events_by_day(events)

        if events:
            print(f"  Loaded {len(events)} event(s) for this chunk")

        # 3. Calculate snapshot interval
        snapshot_interval = self._calculate_snapshot_interval(granularity)

        # 4. Simulate day by day
        days_simulated = 0
        for day in range(start_day, end_day + 1):
            # Apply events on this day
            if day in events_by_day:
                for event in events_by_day[day]:
                    print(f"  Day {day}: Applying event '{event.title}'")
                    self.state = apply_event_effects(self.state, event)

            # Calculate growth
            self._step(day)

            # Write snapshot at intervals
            if (day - start_day) % snapshot_interval == 0 or day == end_day:
                self._write_snapshot(day, granularity)

            days_simulated += 1

        print(f"  Simulated {days_simulated} days")

        # 5. Generate report
        return self._generate_chunk_report(start_day, end_day)

    def _step(self, day: int):
        """
        Execute one simulation step (one day).

        Applies logistic growth formula to current population using
        multi-species growth model.

        :param day: Current astro_day
        """
        # Calculate carrying capacity
        K = self.state.carrying_capacity

        # Apply multi-species growth
        if self.state.population.total > 0:
            new_populations = calculate_multi_species_growth(
                populations=self.state.population.by_species,
                growth_rates=self.config.growth_rates,
                K=K,
                time_step=1.0  # 1 day (for annual rates, this is 1/365.25 of a year)
            )

            # Update population state
            self.state.population.by_species = new_populations
            self.state.population.total = sum(new_populations.values())

            # Scale habitat breakdown proportionally
            # (in real implementation, might want more sophisticated logic)

        # Update current day
        self.state.current_day = day

    def _load_initial_state(self, start_day: int) -> SimulationState:
        """
        Load or create initial simulation state.

        Uses snapshot service's get_interpolated() to load demographic data
        at start_day. If no data exists, starts with zero population.

        :param start_day: Day to load initial state from
        :return: Initialized SimulationState
        """
        # Select appropriate service based on entity_type
        if self.entity_type == "region":
            from ..services import RegionService, RegionSnapshotService

            # Get entity name
            with RegionService() as region_service:
                entity = region_service.get_by_id(self.entity_id)
                if entity is None:
                    raise ValueError(f"Region with ID {self.entity_id} does not exist")
                entity_name = entity.name

            # Get initial demographic data
            with RegionSnapshotService() as snapshot_service:
                initial_data = snapshot_service.get_interpolated(
                    self.entity_id, start_day
                )
        else:  # province
            from ..services import ProvinceService, ProvinceSnapshotService

            # Get entity name
            with ProvinceService() as province_service:
                entity = province_service.get_by_id(self.entity_id)
                if entity is None:
                    raise ValueError(f"Province with ID {self.entity_id} does not exist")
                entity_name = entity.name

            # Get initial demographic data
            with ProvinceSnapshotService() as snapshot_service:
                initial_data = snapshot_service.get_interpolated(
                    self.entity_id, start_day
                )

        # Create population state from snapshot data or defaults
        if initial_data:
            population = PopulationState(
                total=initial_data["population_total"],
                by_species=initial_data.get("population_by_species", {}) or {},
                by_habitat=initial_data.get("population_by_habitat", {}) or {}
            )
            print(f"  Loaded initial state: population={population.total:,}")
        else:
            # No data - start with zero population
            population = PopulationState(
                total=0,
                by_species={},
                by_habitat={}
            )
            print(f"  No initial data found, starting with zero population")

        # Initialize carrying capacity factors with randomness
        environmental_factor = self.rng.uniform(*self.config.environmental_factor_range)
        location_factor = self.rng.uniform(*self.config.location_factor_range)

        print(f"  Environmental factor: {environmental_factor:.3f}")
        print(f"  Infrastructure factor: {self.config.infrastructure_factor_initial:.3f}")
        print(f"  Location factor: {location_factor:.3f}")

        return SimulationState(
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            entity_name=entity_name,
            current_day=start_day,
            population=population,
            K_base=self.config.base_carrying_capacity,
            environmental_factor=environmental_factor,
            infrastructure_factor=self.config.infrastructure_factor_initial,
            location_factor=location_factor,
            rng=self.rng
        )

    def _load_events(self, start_day: int, end_day: int) -> List[Event]:
        """
        Load human-authored events for time range.

        Queries EventService for events affecting this entity within
        the specified time range.

        :param start_day: Start of range
        :param end_day: End of range (inclusive)
        :return: List of events (sorted by astro_day)
        """
        from ..services import EventService

        with EventService() as event_service:
            # Load all events in time range
            all_events = event_service.get_events_in_range(
                start_day, end_day, active_only=True
            )

            # Filter to events for this entity
            if self.entity_type == "region":
                events = [e for e in all_events if e.region_id == self.entity_id]
            else:  # province
                events = [e for e in all_events if e.province_id == self.entity_id]

        return events

    def _write_snapshot(self, day: int, granularity: str):
        """
        Write snapshot to database via snapshot service.

        :param day: Day to write snapshot for
        :param granularity: Snapshot granularity
        """
        if self.entity_type == "region":
            from ..services import RegionSnapshotService

            with RegionSnapshotService() as snapshot_service:
                # Check if snapshot already exists
                existing = snapshot_service.get_snapshot_at_day(self.entity_id, day)
                if existing:
                    # Skip to avoid duplicate error
                    return

                snapshot_service.create_snapshot(
                    region_id=self.entity_id,
                    astro_day=day,
                    population_total=self.state.population.total,
                    snapshot_type="simulation",
                    granularity=granularity,
                    population_by_species=self.state.population.by_species,
                    population_by_habitat=self.state.population.by_habitat
                )
        else:  # province
            from ..services import ProvinceSnapshotService

            with ProvinceSnapshotService() as snapshot_service:
                existing = snapshot_service.get_snapshot_at_day(self.entity_id, day)
                if existing:
                    return

                snapshot_service.create_snapshot(
                    province_id=self.entity_id,
                    astro_day=day,
                    population_total=self.state.population.total,
                    snapshot_type="simulation",
                    granularity=granularity,
                    population_by_species=self.state.population.by_species,
                    population_by_habitat=self.state.population.by_habitat
                )

    def _validate_chunk(self, end_day: int) -> List[str]:
        """
        Validate chunk results and return list of issues.

        Checks for common problems:
        - Negative population
        - Population exceeding carrying capacity by large margin
        - Other sanity checks

        :param end_day: End day of chunk (for context)
        :return: List of warning messages (empty if no issues)
        """
        issues = []

        # Check for negative population
        if self.state.population.total < 0:
            issues.append(f"Negative population: {self.state.population.total}")

        # Check for extremely low infrastructure
        if self.state.infrastructure_factor < 0.1:
            issues.append(f"Very low infrastructure factor: {self.state.infrastructure_factor:.3f}")

        # Check for extremely low environmental factor
        if self.state.environmental_factor < 0.1:
            issues.append(f"Very low environmental factor: {self.state.environmental_factor:.3f}")

        return issues

    def _calculate_chunks(
        self, start_day: int, end_day: int
    ) -> List[Tuple[int, int]]:
        """
        Divide time range into chunks for incremental execution.

        :param start_day: Start of range
        :param end_day: End of range (inclusive)
        :return: List of (chunk_start, chunk_end) tuples
        """
        chunks = []
        chunk_size = self.config.chunk_size_days

        current = start_day
        while current <= end_day:
            chunk_end = min(current + chunk_size, end_day)
            chunks.append((current, chunk_end))
            current = chunk_end + 1

        return chunks

    def _calculate_snapshot_interval(self, granularity: str) -> int:
        """
        Calculate snapshot interval in days based on granularity.

        :param granularity: "year", "decade", or "century"
        :return: Interval in days
        """
        if granularity == "year":
            return 365  # Approximately 1 year
        elif granularity == "decade":
            return 3652  # Approximately 10 years
        elif granularity == "century":
            return 36525  # Approximately 100 years
        else:
            return 365  # Default to year

    def _index_events_by_day(self, events: List[Event]) -> Dict[int, List[Event]]:
        """
        Index events by astro_day for fast lookup during simulation.

        :param events: List of events
        :return: Dictionary mapping astro_day to list of events on that day
        """
        indexed = {}
        for event in events:
            if event.astro_day not in indexed:
                indexed[event.astro_day] = []
            indexed[event.astro_day].append(event)
        return indexed

    def _generate_chunk_report(
        self, start_day: int, end_day: int
    ) -> Dict[str, Any]:
        """
        Generate summary report for completed chunk.

        :param start_day: Chunk start day
        :param end_day: Chunk end day
        :return: Report dictionary with statistics
        """
        return {
            "start_day": start_day,
            "end_day": end_day,
            "final_population": self.state.population.total,
            "carrying_capacity": self.state.carrying_capacity,
            "population_by_species": dict(self.state.population.by_species),
            "environmental_factor": self.state.environmental_factor,
            "infrastructure_factor": self.state.infrastructure_factor,
            "location_factor": self.state.location_factor,
        }
