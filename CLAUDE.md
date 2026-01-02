# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saskan Calendar is a multi-app monorepo for worldbuilding the **Saskan Lands**, a solarpunk post-catastrophe fictional world. It contains three independent applications plus shared utilities:

- **app_timeline**: Historical timeline database with SQLAlchemy/Typer CLI
- **app_calendar**: Astronomical calendar calculation library (pure Python)
- **app_maps**: Geographic simulation engine with discrete-step demographic modeling
- **shared/**: Common utilities

## Development Commands

### Environment Setup

```bash
# Install dependencies
poetry install

# Activate virtual environment (optional)
source poetry_activate
```

### Testing

```bash
# Run all tests
poetry run pytest tests/ -v

# Run tests for a specific app
poetry run pytest tests/timeline/ -v
poetry run pytest tests/calendar/ -v

# Run specific test file
poetry run pytest tests/timeline/test_models.py -v

# Run with coverage
poetry run pytest tests/timeline/ --cov=app_timeline --cov-report=html

# Run single test
poetry run pytest tests/timeline/test_models.py::TestSettlementModel::test_create_settlement -v
```

### Timeline CLI Commands

The primary CLI entry point is `saskan-timeline`:

```bash
# Database management
poetry run saskan-timeline db init          # Create all tables
poetry run saskan-timeline db drop --yes    # Drop all tables
poetry run saskan-timeline db info          # Show database info
poetry run saskan-timeline db validate      # Validate schema

# Create data (examples)
poetry run saskan-timeline data add-epoch --name "Early Era" --start 0 --end 1000
poetry run saskan-timeline data add-region --name "Northlands"
poetry run saskan-timeline data add-settlement --name "Ingar" --type ring_town --province 1

# Query data (examples)
poetry run saskan-timeline list epochs
poetry run saskan-timeline list settlements --type ring_town
poetry run saskan-timeline list events --start-day 0 --end-day 1000

# Update/delete data (examples)
poetry run saskan-timeline update settlement 1 --name "New Name"
poetry run saskan-timeline update delete-settlement 1 --yes
poetry run saskan-timeline update delete-settlement 1 --hard --yes  # Permanent deletion

# Import/export
poetry run saskan-timeline io export backup.json
poetry run saskan-timeline io import data.json --dry-run
poetry run saskan-timeline io import data.json --skip-existing
```

### Code Quality

```bash
# Format code
poetry run black app_timeline/ app_calendar/ app_maps/ shared/

# Sort imports
poetry run isort app_timeline/ app_calendar/ app_maps/ shared/
```

## Architecture

### app_timeline: Layered Database Application

**Layers (bottom to top):**

1. **Storage**: SQLite database at `data/timeline/saskan_timeline.db`
2. **Database Layer** (`db/`): SQLAlchemy engine and session management
3. **Models** (`models/`): SQLAlchemy ORM models with mixins
4. **Service Layer** (`services/`): Business logic and CRUD operations
5. **CLI Layer** (`cli*.py`): Typer-based command-line interface

**Key Models:**
- `Region` → `Province` → `Settlement` (geographic hierarchy)
- `RegionSnapshot`, `ProvinceSnapshot`, `SettlementSnapshot` (time-series demographic data)
- `Entity` (people, organizations)
- `Event` (historical timeline events)
- `Route` (connections between settlements)
- `Epoch` (time periods)

**Model Mixins:**
- `PrimaryKeyMixin`: Auto-incrementing ID
- `TimestampMixin`: Created/updated timestamps
- `TemporalBoundsMixin`: `founded_astro_day`, `dissolved_astro_day`
- `DescriptionMixin`: Programmatic description management
- `MetadataMixin`: Flat key-value JSON validation (no nested objects/arrays)

**Service Pattern:**
```python
from app_timeline.services import SettlementService

# Context manager ensures proper session cleanup
with SettlementService() as service:
    settlement = service.create_settlement(
        name="Ingar",
        settlement_type="ring_town",
        province_id=1,
        founded_astro_day=100
    )
    settlement_id = settlement.id  # Extract ID before exiting context

# settlement object is detached after context exit
# Use settlement_id for subsequent operations
```

**Critical Pattern - Extract IDs Before Context Exit:**
```python
# WRONG - DetachedInstanceError
with RegionService() as region_service:
    region = region_service.create_region(name="Test Region")

with ProvinceService() as province_service:
    province = province_service.create_province(name="Test", region_id=region.id)  # Error!

# CORRECT - Extract ID first
with RegionService() as region_service:
    region = region_service.create_region(name="Test Region")
    region_id = region.id  # Extract before exit

with ProvinceService() as province_service:
    province = province_service.create_province(name="Test", region_id=region_id)  # Works!
```

### app_calendar: Pure Computational Library

Stateless astronomical calculation library with no CLI or database. Provides calendar conversion functions:

```python
from app_calendar import universal_date_translator

# Convert between calendar systems
result = universal_date_translator(source_calendar, target_calendar, date_value)
```

Calendar classes: `AstroCalendar`, `FatunikCalendar`, `StrictLunarCalendar`, `LunarSolarCalendar`

### app_maps: Simulation Engine

Discrete-step simulation for settlement growth and migration:

```python
from app_maps.saskan.engine import SaskanEngine

# Deterministic simulation with reproducibility
engine = SaskanEngine(seed=42)
state = engine.run_simulation(steps=100)
```

## Configuration

**Main config:** `config/timeline/settings.yaml`

```yaml
database:
  path: "data/timeline/saskan_timeline.db"
  dialect: "sqlite"  # or "postgresql" for production
  echo: false        # Set true for SQL logging

settlement_types:
  - ring_town
  - market_town
  # ... more types

species:
  - huum  # Human
  - sint  # Sentients
  # ... more species
```

Configuration values are **guidance only** - no database constraints enforced (soft validation).

## Time System

All dates stored as `astro_day` (integer days since epoch):

```python
from app_timeline.utils import days_to_turns, format_duration

# Convert 1000 days to turns
turns = days_to_turns(1000)  # ~2.74 turns

# Format human-readable duration
duration = format_duration(1000)  # "2.74 turns"
```

**Time units:**
- `pulse`: 1 second (86,400 per day)
- `turn`: 365.25 days (1 solar year)
- `decade`: 10 turns
- `century`: 100 turns
- `shell`: 132 turns (Terpin lifespan)

## Database Schema

**Core tables:**
- `epochs` - Time periods
- `regions` - Top geographic groupings
- `provinces` - Administrative divisions
- `settlements` - Cities, towns, villages
- `entities` - People, organizations
- `events` - Historical events
- `routes` - Connections between settlements

**Snapshot tables (time-series demographic data):**
- `region_snapshots` - Regional demographic data
- `province_snapshots` - Provincial demographic data
- `settlement_snapshots` - Settlement demographic data

All snapshots have: `population_total`, `population_by_species`, `population_by_habitat`, `cultural_composition`, `economic_data`, `snapshot_type` (census/simulation/estimate), `granularity` (year/decade/century).

## Common Workflows

### Schema Change Workflow (Development)

```bash
# 1. Modify models in app_timeline/models/
# 2. Drop and recreate database
poetry run saskan-timeline db drop --yes
poetry run saskan-timeline db init

# 3. Re-import data if backed up
poetry run saskan-timeline io import backup.json
```

### Adding New Model

1. Create model file in `app_timeline/models/`
2. Use appropriate mixins (`PrimaryKeyMixin`, `TimestampMixin`, etc.)
3. Add exports to `app_timeline/models/__init__.py`
4. Update `validate_schema()` in `db/schema.py`
5. Create corresponding service in `app_timeline/services/`
6. Write tests in `tests/timeline/test_models.py`

### Adding CLI Command

1. Choose command group: `cli_data.py` (create), `cli_list.py` (query), `cli_update.py` (update/delete), `cli_import_export.py` (bulk ops)
2. Add Typer command function with appropriate decorators
3. Use service layer for business logic
4. Use Rich library for formatted output
5. Write tests in `tests/timeline/test_cli_*.py`

## Important Patterns

### Metadata Management (ADR-008)

**MetadataMixin - Flat structure validation:**
```python
# Valid - flat key-value pairs
region.update_metadata({"climate": "cold", "terrain": "mountains"}, mode="merge")

# Invalid - nested objects/arrays rejected
region.update_metadata({"nested": {"key": "value"}})  # ValueError
region.update_metadata({"array": [1, 2, 3]})  # ValueError
```

**SQLAlchemy JSON mutation tracking:**
```python
from sqlalchemy.orm.attributes import flag_modified

# WRONG - Change not detected
region.meta_data["new_key"] = "value"
session.commit()  # Not persisted!

# CORRECT - Use mixin methods (auto-flags)
region.update_metadata({"new_key": "value"}, mode="merge")
session.commit()  # Persisted

# Or manually flag
region.meta_data["new_key"] = "value"
flag_modified(region, "meta_data")
session.commit()  # Persisted
```

### Soft vs Hard Delete

**Soft delete** (default for most models):
- Sets `is_active=False` (or `is_deprecated=True` for events)
- Record preserved, excluded from default queries
- Applies to: Region, Province, Settlement, Entity, Route, Event

**Hard delete** (permanent):
- Always used for: Epoch, Snapshots
- Optional `--hard` flag for entities with soft delete

### Snapshot Interpolation

```python
from app_timeline.services import RegionSnapshotService

with RegionSnapshotService() as service:
    # Create snapshots at day 100 and 200
    service.create_snapshot(region_id=1, astro_day=100, population_total=50000)
    service.create_snapshot(region_id=1, astro_day=200, population_total=70000)

    # Interpolate at day 150 (midpoint)
    interpolated = service.get_interpolated(region_id=1, astro_day=150)
    # Returns: population_total=60000 (linear interpolation)
```

## Critical Design Principles

### AI Usage Philosophy (ADR-005)

**AI is ONLY for narrative generation, NOT for simulation logic or decision-making.**

**Permitted AI uses:**
- Generate prose descriptions from simulation data
- Expand bullet-point notes into paragraphs
- Suggest character names, cultural details (subject to curation)

**Prohibited AI uses:**
- Write simulation formulas (logistic growth, migration flows)
- Make story decisions (which city should rebel? when does famine strike?)
- Generate historical events without data grounding

**Workflow pattern:**
```
1. Simulation generates data → 2. Human writes contextualized prompt
3. AI generates draft prose → 4. Human reviews/edits/curates
5. Approved text stored in database
```

**Key principle:** AI as **assistant**, not **authority**. AI as **amplifier**, not **replacement**.

### Hybrid Manual-Algorithmic Workflow (ADR-007)

Clear separation between algorithmic and creative elements:

**Algorithms handle:**
- Population growth/decline (logistic formulas)
- Migration flows (network calculations)
- Resource constraints (carrying capacity)
- City hierarchies (rank-size distributions)

**Humans handle:**
- Major historical events (wars, reforms, discoveries)
- Cultural details (religions, languages, practices)
- Character creation (legendary figures, protagonists)
- Thematic arcs (planetary awakening, species cooperation)
- Narrative descriptions (converting data to prose)

**Workflow:** Human defines eras/events → Algorithm simulates demographic impacts → Human inspects results → Human adjusts parameters if implausible → Algorithm re-simulates → Human writes narrative based on final data.

**Feedback loop:** Simulation reveals inconsistencies → Human adjusts timeline or adds infrastructure → Simulation validates adjustments.

### Incremental Simulation (ADR-006)

Simulations run in configurable chunks (default: 100-year segments) with checkpoints:

**Benefits:**
- Fail-fast inspection (catch implausible results at year 100, not year 2000)
- Parameter tuning without full re-simulation
- Branching timelines for "what-if" scenarios
- Built-in validation between chunks

**Pattern:**
```python
sim.run(start_year=0, end_year=500)  # Runs in 100-year chunks
# Inspect results, fix bugs if needed
sim.resume(from_year=500, to_year=1000)  # Continue from checkpoint
```

## Architecture Decision Records (ADRs)

Key decisions documented in `docs/design/timeline/adr/`:

- **ADR-001**: SQLite as source of truth (portable, ACID guarantees)
- **ADR-002**: Time-series snapshots (one row per entity per period)
- **ADR-003**: Python simulation engine (no Rust unless needed)
- **ADR-004**: JSON for configuration only (not data)
- **ADR-005**: AI for narrative generation only (not simulation logic)
- **ADR-006**: Incremental, resumable simulation
- **ADR-007**: Hybrid manual-algorithmic workflow
- **ADR-008**: Metadata with flat structure validation

## Migration Path

**Current:** SQLite for development
**Future:** PostgreSQL for production

```yaml
# Update config/timeline/settings.yaml
database:
  path: "postgresql://user:password@localhost:5432/saskan_timeline"
  dialect: "postgresql"
```

Then run: `poetry run saskan-timeline db init`

## Key Files

**Entry points:**
- `app_timeline/cli.py` - Primary CLI application
- `app_timeline/models/__init__.py` - All ORM models
- `app_timeline/services/base.py` - Base service pattern

**Configuration:**
- `config/timeline/settings.yaml` - Runtime configuration
- `pyproject.toml` - Project metadata, dependencies, scripts

**Documentation:**
- `docs/timeline/README.md` - User guide
- `docs/timeline/TECHNICAL.md` - Technical documentation
- `docs/design/timeline/adr/` - Architecture decision records

## Tech Stack

- **Python**: 3.12 (type hints required)
- **Package Manager**: Poetry
- **Database**: SQLite (dev), PostgreSQL (production path)
- **ORM**: SQLAlchemy 2.0
- **CLI**: Typer + Rich
- **Testing**: pytest + pytest-mock
- **Data**: pandas, numpy
- **Graphs**: networkx
- **Visualization**: matplotlib

## Development Roadmap

### Current Version: 0.3.0 (PR-003a Complete)

**PR-003a: Schema Refactoring for Macro-Scale Simulation** ✅ COMPLETE
- Added RegionSnapshot and ProvinceSnapshot models
- Implemented snapshot interpolation services
- Added snapshot_type and granularity fields to all snapshots
- Implemented ADR-008 (Metadata and Description Field Management)
- CLI commands for region/province snapshot management
- Extended import/export support

### Next: PR-003b - Macro-Scale Simulation Engine

**Status:** Next major development effort (NOT YET STARTED)

**Scope:**

1. **Population Dynamics Formulas**
   - Implement logistic growth calculations
   - Carrying capacity formulas (K_t = K_base × C_t × I_t × L_t)
   - Multi-species population modeling

2. **Region/Province Simulation Engine**
   - Discrete-step simulation at regional and provincial levels
   - Generate demographic snapshots from simulation runs
   - Pre-settlement era simulation capability (before cities existed)
   - Follows ADR-006: Chunked execution with checkpoints (default 100-year segments)

3. **Event System Basics**
   - Migration events
   - Climate events (droughts, favorable periods)
   - Event effects on population dynamics
   - Human-authored events applied during simulation (ADR-007)

4. **CLI Commands**
   - `saskan-timeline simulate region <region_id> --start <day> --end <day>`
   - `saskan-timeline simulate province <province_id> --start <day> --end <day>`
   - Integration with existing snapshot infrastructure
   - Validation and reporting between simulation chunks

5. **Integration Points**
   - Leverages PR-003a schema (RegionSnapshot, ProvinceSnapshot tables)
   - Uses interpolation services from PR-003a
   - Generates snapshots with `snapshot_type='simulation'`
   - Respects ADR-007: Humans define events/parameters, algorithm simulates demographics

**Key Dependencies:**
- ✅ PR-003a (snapshot schema and services)
- ✅ ADR-003 (Python simulation engine)
- ✅ ADR-006 (Incremental, resumable simulation)
- ✅ ADR-007 (Hybrid manual-algorithmic workflow)

**Design Notes:**
- Simulation engine will read events from database (human-authored)
- Simulation writes demographic snapshots (algorithm-calculated)
- Chunked execution allows inspection and parameter adjustment
- Deterministic with optional random seed for reproducibility

### Future Work (After PR-003b)

1. **Validation Integration** - Apply validation utilities across all data entry
2. **Reporting** - Generate timeline reports and visualizations
3. **Integration** - Connect with app_calendar for date conversion
4. **Parquet Export** - Add Parquet format for OLAP/DuckDB analysis
5. **Advanced Queries** - Additional filtering and search capabilities
6. **Event System Expansion** - Wars, technology changes, cultural shifts
7. **Settlement-Level Simulation** - Extend simulation down to settlement granularity
