# app_maps Salvage List

**Reconnaissance Date**: 2025-12-27
**Purpose**: Identify useful patterns, abstractions, and code from app_maps experimental code for potential integration into app_timeline.

---

## Executive Summary

The app_maps experimental code contains a working step-based simulation engine for settlement formation, population dynamics, route building, and geographic expansion. While the code is specific to settlement simulation, it demonstrates several patterns and architectural decisions that could inform app_timeline development.

**Recommendation**: Salvage patterns and concepts incrementally as needed during timeline ADR implementation. Most code is too specific to settlement simulation to copy directly, but the overall architecture provides useful reference material.

---

## Priority 1: Must-Have Patterns

### 1. Step-Based Simulation Architecture (engine.py)

**Location**: `app_maps/saskan/engine.py:17-466`

**What It Is**:
- Clean separation between simulation engine (`SaskanEngine`) and simulation state (`SimulationState`)
- Single `step()` method that advances simulation and returns events
- State is fully serializable (uses dataclasses)
- Engine maintains internal state separate from simulation state

**Why Valuable**:
- Timeline will need similar step-based progression through time
- Event-based architecture aligns with timeline ADR requirements
- Clear separation of concerns between state and logic

**Key Pattern**:
```python
class Engine:
    def __init__(self, config):
        self.config = config
        self.state = State(...)

    def step(self) -> List[Event]:
        self.state.step += 1
        events = []
        events.extend(self._update_subsystem_a())
        events.extend(self._update_subsystem_b())
        return events
```

**Integration Notes**:
- Timeline engine could follow similar pattern
- Each step represents progression through time
- Events capture state changes and narrative moments
- State should be fully serializable for persistence

---

### 2. Configuration System (settings.py)

**Location**: `app_maps/saskan/settings.py:9-214`

**What It Is**:
- Comprehensive dataclass-based configuration (`SimulationConfig`)
- Scenario presets with named variants
- `apply_scenario()` function that modifies config based on scenario name
- Helper functions that derive complex values from config

**Why Valuable**:
- Timeline will need flexible configuration for different eras, scenarios
- Dataclasses provide type safety and documentation
- Scenario system allows testing different historical trajectories

**Key Pattern**:
```python
@dataclass
class SimulationConfig:
    steps: int = 10
    seed: Optional[int] = None
    scenario: Optional[str] = None
    # ... many domain-specific parameters

    def __post_init__(self):
        # Compute derived values
        pass

SCENARIO_PRESETS = {
    "baseline": {"seed": 42, "description": "..."},
    "special-case": {"seed": 99, "description": "..."},
}

def apply_scenario(config: SimulationConfig) -> SimulationConfig:
    if config.scenario in SCENARIO_PRESETS:
        # Modify config based on preset
        pass
    return config
```

**Integration Notes**:
- Timeline config could include era-specific parameters
- Scenario presets useful for testing different historical periods
- Keep configuration separate from core logic

---

### 3. Event Model (models.py)

**Location**: `app_maps/saskan/models.py:40-43`

**What It Is**:
```python
@dataclass
class Event:
    step: int
    message: str
```

**Why Valuable**:
- Dead simple event representation
- Step/time association built in
- Message provides human-readable description

**Integration Notes**:
- Timeline events will be more complex (date, location, entities, tags)
- But the basic pattern of "timestamped narrative snippet" is sound
- Consider adding: event_type, location, entities, metadata fields

---

### 4. State Persistence (persistence.py)

**Location**: `app_maps/saskan/persistence.py:12-36`

**What It Is**:
- `snapshot_state()` function that serializes state to JSON
- Captures: metadata, config, state, events
- Timestamped filenames (step_0001.json, step_0002.json)

**Why Valuable**:
- Timeline will need to persist state for export/resume
- JSON serialization works well with dataclasses (via asdict)
- Snapshot pattern allows time-travel debugging

**Key Pattern**:
```python
def snapshot_state(state, events, config, snapshot_dir, scenario):
    payload = {
        "meta": {"step": state.step, ...},
        "config": asdict(config),
        "state": asdict(state),
        "events": [asdict(e) for e in events]
    }
    path = snapshot_dir / f"step_{state.step:04d}.json"
    path.write_text(json.dumps(payload, indent=2))
    return path
```

**Integration Notes**:
- Timeline snapshots should include timeline state at specific dates
- Consider compression for large timelines
- Metadata should track creation time, software version

---

## Priority 2: Nice-to-Have Patterns

### 5. Coordinate System and Distance Calculations (engine.py, map_utils.py)

**Location**:
- `app_maps/saskan/engine.py:186-187` (distance calculation)
- `app_maps/saskan/map_utils.py:74-78` (coordinate to block conversion)

**What It Is**:
- Simple 2D coordinate system: `Tuple[int, int]` representing (x, y) in km
- Distance calculation via Euclidean distance
- Block/grid system for coarse-grained location (50km blocks)

**Why Valuable**:
- Timeline needs geographic location representation
- Coordinate system could be reused for placing events spatially
- Block system useful for regional aggregation

**Integration Notes**:
- Timeline likely needs richer location model (region, settlement, coordinates)
- Distance calculations useful for proximity queries
- Consider geographic projection issues if using real-world coordinates

---

### 6. Stochastic Event System (engine.py)

**Location**: `app_maps/saskan/engine.py:206-263` (hazards and shocks)

**What It Is**:
- Random events triggered by probability thresholds
- Events have meaningful impacts on state
- Recovery mechanics balance negative shocks

**Pattern**:
```python
def _apply_hazards(self) -> List[Event]:
    events = []
    if self.random.random() > self.config.hazard_chance:
        return events
    # Apply hazard logic
    events.append(Event(step=..., message=...))
    return events
```

**Why Valuable**:
- Timeline might include random/probabilistic events
- Shows clean pattern for conditional event generation
- Demonstrates how to make stochastic systems reproducible (seeded random)

**Integration Notes**:
- Timeline events are likely historical facts, not random
- But procedural content generation might use similar patterns
- Seeded randomness useful for reproducible testing

---

### 7. Text Rendering (renderers/text.py)

**Location**: `app_maps/saskan/renderers/text.py:8-71`

**What It Is**:
- Convert simulation state to human-readable text
- Summary statistics, sorted lists, rollups
- Nested indentation for hierarchical data

**Why Valuable**:
- Timeline will need text export for reports
- Shows good patterns for formatting complex data
- Demonstrates summary vs detail views

**Integration Notes**:
- Timeline text output likely more narrative-focused
- Consider markdown rendering for richer formatting
- Template system might be more flexible than hardcoded rendering

---

### 8. Visualization with Matplotlib (plotting.py)

**Location**: `app_maps/saskan/plotting.py:10-113`

**What It Is**:
- Matplotlib-based 2D scatter plot of settlements
- Routes drawn as lines
- Color-coding by settlement type
- Windowing to show specific geographic region

**Why Valuable**:
- Timeline might benefit from visualization (timeline diagrams, maps)
- Shows pattern for optional visualization dependencies
- Demonstrates windowing/viewport for large datasets

**Integration Notes**:
- Timeline likely needs different visualization (timeline, not map)
- Consider more modern viz libraries (plotly, altair) for interactivity
- Pattern for graceful degradation when matplotlib not installed is good

---

## Priority 3: Reference Only (Don't Copy)

### 9. Settlement Growth Mechanics (engine.py:51-76)

**What It Is**: Population growth with carrying capacity, jitter, modifiers

**Why Reference Only**: Too specific to population simulation. Timeline entities don't "grow" this way.

---

### 10. Route Building Logic (engine.py:120-163)

**What It Is**: Procedural route generation between settlements

**Why Reference Only**: Timeline relationships aren't generated procedurally in the same way.

---

### 11. Name Generation (engine.py:189-204)

**What It Is**: Simple syllable-based name generator

**Why Reference Only**: Timeline entities will have historical names, not generated ones. If procedural generation needed, use more sophisticated system.

---

### 12. Market Town Promotion (engine.py:430-465)

**What It Is**: Settlement type transitions based on thresholds

**Why Reference Only**: Very domain-specific to settlement simulation.

---

## Anti-Patterns to Avoid

### 1. Proliferation of Magic Numbers

**Issue**: Configuration has 40+ parameters, many interdependent
**Example**: `pollination_penalty: float = -0.01` is very specific to bee pollination worldbuilding detail
**Lesson**: Keep core config focused. Move domain-specific details to extensions.

---

### 2. Monolithic Engine Class

**Issue**: SaskanEngine has 18 private methods, mixing concerns
**Lesson**: Timeline engine should delegate to subsystems (calendar, entity management, event generation) rather than implementing everything inline.

---

### 3. Hard-Coded Scenario Logic

**Issue**: `apply_scenario()` has if/elif chain for scenario tweaks
**Example**: Line 203-213 special-cases "great-migration" scenario
**Lesson**: Use data-driven scenario definitions where possible, avoid embedding scenario logic in code.

---

### 4. Weak Type Hints for Coordinates

**Issue**: Coordinates are `Tuple[int, int]` with no semantic meaning
**Lesson**: Timeline should use typed location classes (Region, Settlement, Coordinates) rather than raw tuples.

---

## Recommended Integration Strategy

### Phase 1: Initial Timeline Setup (ADR 1-2)
- Adopt step-based engine architecture pattern
- Implement configuration system using dataclasses
- Create simple Event model

### Phase 2: Entity and Relationship Management (ADR 3-4)
- Study settlement/route relationship pattern, but don't copy directly
- Design richer entity model than app_maps Settlement class
- Consider coordinate system for location representation

### Phase 3: Persistence and Export (ADR 5-6)
- Adopt snapshot persistence pattern
- Implement JSON export similar to app_maps
- Consider visualization needs (different from map plotting)

### Phase 4: Polish and Extension (ADR 7+)
- Add text rendering for reports
- Implement scenario system for testing historical variations
- Consider stochastic events if needed for procedural content

---

## Files Worth Deeper Study

1. **engine.py** - Study structure, ignore domain-specific logic
2. **settings.py** - Copy configuration patterns
3. **models.py** - Useful starting point for data models
4. **persistence.py** - Adopt snapshot pattern directly
5. **sim.py** - Shows clean runner/orchestration layer

---

## Files to Skip

1. **plotting.py** - Timeline visualization needs are different
2. **map_utils.py** - Too map-specific
3. **renderers/text.py** - Reference only, don't copy

---

## Conclusion

The app_maps codebase demonstrates a working simulation architecture that shares conceptual overlap with timeline requirements. The most valuable salvage is architectural patterns (step-based engine, configuration system, event model, persistence) rather than specific implementations.

Recommend incremental integration during ADR implementation, treating app_maps as reference material rather than copy-paste source.

The code quality is good: clear dataclass-based models, type hints throughout, functional decomposition. But it's optimized for settlement simulation, not timeline management. Timeline will need richer entity models, different visualization, and historical accuracy constraints that app_maps doesn't have.

**Bottom Line**: Mine it for patterns, not code. The architecture is the treasure, not the implementation details.
