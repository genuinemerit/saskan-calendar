# Saskan Timeline - Technical Documentation

**Version:** 0.3.0
**Python:** 3.12
**Framework:** SQLAlchemy 2.0

---

## Architecture Overview

The timeline system follows a layered architecture with clear separation of concerns.

### Layers

1. **CLI Layer** - Typer + Rich for user interaction
2. **Service Layer** - Business logic and data operations
3. **Database Layer** - SQLAlchemy ORM
4. **Storage** - SQLite (development) / PostgreSQL (production)

### Key Design Principles

1. **Declarative Models** - SQLAlchemy ORM with type hints
2. **Configuration as Code** - YAML + Python dataclasses
3. **No Hard Constraints** - Flexible schema, soft validation
4. **Time-Series Support** - Snapshot pattern for demographic data
5. **Migration Ready** - SQLite to PostgreSQL path designed in

---

## Project Structure

```text
app_timeline/
  __init__.py           # Package exports
  cli.py                # Typer CLI application
  cli_data.py           # CLI commands for creating data
  cli_list.py           # CLI commands for querying data
  cli_update.py         # CLI commands for updating/deleting data
  cli_import_export.py  # CLI commands for import/export
  config.py             # Configuration management
  models/               # SQLAlchemy models
    __init__.py
    base.py            # Base classes and mixins (PR-003a: added DescriptionMixin, MetadataMixin)
    entity.py          # Entity model
    epoch.py           # Epoch model (PR-003a: added description field)
    event.py           # Event model
    province.py        # Province and Region models (PR-003a: added description fields)
    province_snapshot.py # ProvinceSnapshot model (PR-003a: new)
    region_snapshot.py # RegionSnapshot model (PR-003a: new)
    route.py           # Route model
    settlement.py      # Settlement and SettlementSnapshot models (PR-003a: added snapshot_type/granularity)
  services/             # Business logic layer
    __init__.py
    base.py            # Base service class
    entity_service.py  # Entity operations
    epoch_service.py   # Epoch operations
    event_service.py   # Event operations
    province_service.py # Province operations
    province_snapshot_service.py # Province snapshot operations (PR-003a: new)
    region_service.py  # Region operations
    region_snapshot_service.py # Region snapshot operations (PR-003a: new)
    route_service.py   # Route operations
    settlement_service.py # Settlement operations
    snapshot_service.py # Settlement snapshot operations
  utils/                # Utility functions
    __init__.py
    temporal.py        # Temporal conversion utilities
    validation.py      # Validation utilities
  db/                   # Database utilities
    __init__.py
    connection.py      # Engine and session management
    schema.py          # Schema operations

config/timeline/
  settings.yaml        # Application configuration

tests/timeline/
  conftest.py          # Pytest fixtures
  test_config.py       # Configuration tests
  test_db.py           # Database tests
  test_models.py       # Model tests (includes ADR-008 mixin tests - PR-003a)
  test_services.py     # Service layer tests
  test_snapshot_services.py # Region/province snapshot service tests (PR-003a)
  test_cli_data.py     # CLI create command tests
  test_cli_list.py     # CLI query command tests
  test_cli_update.py   # CLI update/delete command tests
  test_cli_import_export.py # CLI import/export tests
  test_validation.py   # Validation utility tests
  test_temporal.py     # Temporal utility tests
```

---

## Database Schema

### Table Relationships

- Region (1) ---< (M) Province
- Region (1) ---< (M) RegionSnapshot (PR-003a)
- Province (1) ---< (M) Settlement
- Province (1) ---< (M) ProvinceSnapshot (PR-003a)
- Settlement (1) ---< (M) SettlementSnapshot
- Settlement (parent) (1) ---< (M) Settlement (child)
- Settlement (origin) (1) ---< (M) Route >--- (1) Settlement (destination)
- Entity (1) ---< (M) Event
- Event >--- (M:1) Settlement
- Event >--- (M:1) Province

### Core Tables

#### regions

Stores top-level geographic groupings.

**Columns:**

- id (INTEGER, PK)
- name (VARCHAR, UNIQUE, NOT NULL)
- description (TEXT, nullable) - PR-003a: Added via DescriptionMixin
- founded_astro_day (INTEGER, nullable)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- meta_data (JSON, nullable) - PR-003a: Validated via MetadataMixin (flat structure)
- created_at (DATETIME, NOT NULL)
- updated_at (DATETIME, NOT NULL)

#### provinces

Stores administrative divisions within regions.

**Columns:**

- id (INTEGER, PK)
- name (VARCHAR, UNIQUE, NOT NULL)
- description (TEXT, nullable) - PR-003a: Added via DescriptionMixin
- region_id (INTEGER, FK -> regions.id, nullable)
- founded_astro_day (INTEGER, nullable)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

#### settlements

Stores cities, towns, villages, camps, and other populated places.

**Columns:**

- id (INTEGER, PK)
- name (VARCHAR, UNIQUE, NOT NULL)
- settlement_type (VARCHAR, NOT NULL)
- location_x (FLOAT, nullable)
- location_y (FLOAT, nullable)
- parent_settlement_id (INTEGER, FK -> settlements.id)
- province_id (INTEGER, FK -> provinces.id)
- founded_astro_day (INTEGER, NOT NULL)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- is_autonomous (BOOLEAN, NOT NULL, default=False)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

#### settlement_snapshots

Stores time-series demographic data for settlements.

**Columns:**

- id (INTEGER, PK)
- settlement_id (INTEGER, FK -> settlements.id, NOT NULL)
- astro_day (INTEGER, NOT NULL)
- snapshot_type (VARCHAR, NOT NULL, default='simulation') - PR-003a: Added (census/simulation/estimate/etc.)
- granularity (VARCHAR, NOT NULL, default='year') - PR-003a: Added (year/decade/century/etc.)
- population_total (INTEGER, NOT NULL)
- population_by_species (JSON, nullable)
- population_by_habitat (JSON, nullable)
- cultural_composition (JSON, nullable)
- economic_data (JSON, nullable)
- meta_data (JSON, nullable) - PR-003a: Validated via MetadataMixin (flat structure)
- created_at (DATETIME, NOT NULL)
- updated_at (DATETIME, NOT NULL)

#### region_snapshots (PR-003a)

Stores time-series demographic data for regions.

**Columns:**

- id (INTEGER, PK)
- region_id (INTEGER, FK -> regions.id, NOT NULL)
- astro_day (INTEGER, NOT NULL)
- snapshot_type (VARCHAR, NOT NULL, default='simulation')
- granularity (VARCHAR, NOT NULL, default='year')
- population_total (INTEGER, NOT NULL)
- population_by_species (JSON, nullable)
- population_by_habitat (JSON, nullable)
- cultural_composition (JSON, nullable)
- economic_data (JSON, nullable)
- meta_data (JSON, nullable) - Validated via MetadataMixin (flat structure)
- created_at (DATETIME, NOT NULL)
- updated_at (DATETIME, NOT NULL)

**Constraints:**
- CHECK (population_total >= 0)
- CHECK (astro_day >= 0)

#### province_snapshots (PR-003a)

Stores time-series demographic data for provinces.

**Columns:**

- id (INTEGER, PK)
- province_id (INTEGER, FK -> provinces.id, NOT NULL)
- astro_day (INTEGER, NOT NULL)
- snapshot_type (VARCHAR, NOT NULL, default='simulation')
- granularity (VARCHAR, NOT NULL, default='year')
- population_total (INTEGER, NOT NULL)
- population_by_species (JSON, nullable)
- population_by_habitat (JSON, nullable)
- cultural_composition (JSON, nullable)
- economic_data (JSON, nullable)
- meta_data (JSON, nullable) - Validated via MetadataMixin (flat structure)
- created_at (DATETIME, NOT NULL)
- updated_at (DATETIME, NOT NULL)

**Constraints:**
- CHECK (population_total >= 0)
- CHECK (astro_day >= 0)

#### routes

Stores connections/routes between settlements.

**Columns:**

- id (INTEGER, PK)
- origin_settlement_id (INTEGER, FK -> settlements.id, NOT NULL)
- destination_settlement_id (INTEGER, FK -> settlements.id, NOT NULL)
- distance_km (FLOAT, nullable)
- difficulty (VARCHAR, nullable)
- route_type (VARCHAR, nullable)
- founded_astro_day (INTEGER, NOT NULL)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

#### entities

Stores people, organizations, groups, and collectives.

**Columns:**

- id (INTEGER, PK)
- name (VARCHAR, NOT NULL)
- entity_type (VARCHAR, NOT NULL)
- description (TEXT, nullable)
- founded_astro_day (INTEGER, NOT NULL)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

#### events

Stores historical timeline events.

**Columns:**

- id (INTEGER, PK)
- astro_day (INTEGER, NOT NULL)
- event_type (VARCHAR, NOT NULL)
- title (VARCHAR, NOT NULL)
- description (TEXT, nullable)
- location_x (INTEGER, nullable)
- location_y (INTEGER, nullable)
- settlement_id (INTEGER, FK -> settlements.id)
- province_id (INTEGER, FK -> provinces.id)
- entity_id (INTEGER, FK -> entities.id)
- is_deprecated (BOOLEAN, NOT NULL, default=False)
- superseded_by_id (INTEGER, FK -> events.id)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

---

## Model Implementation

### Base Mixins

All models inherit from one or more base mixins for common functionality:

**PrimaryKeyMixin** - Provides auto-incrementing integer primary key:

```python
class PrimaryKeyMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
```

**TimestampMixin** - Tracks when database record was created:

```python
class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

**TemporalBoundsMixin** - Tracks entity lifespan in lore timeline:

```python
class TemporalBoundsMixin:
    founded_astro_day = Column(Integer, nullable=False, index=True)
    dissolved_astro_day = Column(Integer, nullable=True, index=True)
```

### Metadata Pattern

All models use `meta_data` (not `metadata` - reserved by SQLAlchemy) as a JSON column for flexible extension.

**Common patterns:**

Settlement metadata:

```python
meta_data = {
    "water": "fresh",        # Water source type
    "fertile": True,         # Agricultural potential
    "notes": "..."          # Arbitrary notes
}
```

Entity (person) metadata:

```python
meta_data = {
    "species": "huum",
    "birth_place": "Ingar",
    "roles": ["warrior", "leader"]
}
```

Event metadata:

```python
meta_data = {
    "tags": ["battle", "political"],
    "source": "Chapter 12",
    "importance": "high"
}
```

---

## Configuration System

### YAML Configuration

Location: `config/timeline/settings.yaml`

Structure:

```yaml
database:
  path: "data/timeline/saskan_timeline.db"
  dialect: "sqlite"  # or "postgresql"
  echo: false        # SQL logging

settlement_types:
  - ring_town
  - market_town
  # ... more types

species:
  - huum
  - sint
  # ... more species

# ... other enum lists

app:
  version: "0.1.0"
  default_astro_day: 0
```

### Python Configuration Classes

```python
@dataclass
class DatabaseConfig:
    path: str
    dialect: str = "sqlite"
    echo: bool = False

    @property
    def connection_string(self) -> str:
        if self.dialect == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.dialect == "postgresql":
            return self.path
        else:
            raise ValueError(f"Unsupported dialect: {self.dialect}")

@dataclass
class TimelineConfig:
    database: DatabaseConfig
    settlement_types: List[str]
    species: List[str]
    # ... etc
```

### Loading Configuration

```python
from app_timeline.config import get_config

# Loads from default location
config = get_config()

# Or specify custom path
from pathlib import Path
config = get_config(Path("/custom/config.yaml"))

# Access values
print(config.database.connection_string)
print(config.settlement_types)
```

---

## Database Connection

### Singleton Pattern

Engine and session factory use singleton pattern for efficiency:

```python
from app_timeline.db import get_engine, get_session

# Get engine (created once, reused)
engine = get_engine()

# Get new session
session = get_session()
try:
    # Use session
    session.add(obj)
    session.commit()
finally:
    session.close()
```

### Testing

For tests, reset singletons between tests:

```python
from app_timeline.config import reset_config
from app_timeline.db import reset_engine

reset_config()
reset_engine()
# Now get_config() and get_engine() will create fresh instances
```

---

## CLI Commands

### Available Commands

```text
saskan-timeline
  version          # Show application version
  db               # Database management subcommand
    init           # Create all tables
    drop           # Drop all tables (with confirmation)
    info           # Show database statistics
    validate       # Validate schema
```

### Usage Examples

```bash
# Initialize database
poetry run saskan-timeline db init

# Show database info
poetry run saskan-timeline db info

# Validate schema
poetry run saskan-timeline db validate

# Drop database (interactive confirmation)
poetry run saskan-timeline db drop

# Drop database (skip confirmation)
poetry run saskan-timeline db drop --yes

# Show version
poetry run saskan-timeline version
```

### Adding New Commands

```python
from typer import Typer
from rich import print as rprint

app = typer.Typer()

@app.command("new-command")
def new_command(
    arg: str = typer.Argument(..., help="Required argument"),
    opt: bool = typer.Option(False, "--flag", "-f", help="Optional flag")
):
    """Command description appears in help."""
    rprint(f"[cyan]Processing {arg}...[/cyan]")
    # Implementation here
```

---

## Testing Design

### Test Structure

- **conftest.py** - Shared pytest fixtures
- **test_config.py** - Configuration loading and validation
- **test_db.py** - Database connection and schema management
- **test_models.py** - Model creation and relationships

### Key Fixtures

```python
@pytest.fixture
def test_db(test_config):
    """Create temporary test database with all tables."""
    reset_engine()
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    reset_engine()

@pytest.fixture
def db_session(test_db):
    """Provide clean database session for testing."""
    session = get_session()
    yield session
    session.rollback()
    session.close()
```

### Running Tests

Note: If poetry shell is enabled, then omit `poetry run` and just type `pytest ...`.

```bash
# All timeline tests
poetry run pytest tests/timeline/ -v

# With coverage report
poetry run pytest tests/timeline/ --cov=app_timeline --cov-report=html

# Specific test file
poetry run pytest tests/timeline/test_models.py -v

# Specific test
poetry run pytest tests/timeline/test_models.py::TestSettlementModel::test_create_settlement -v
```

---

## Migration to PostgreSQL

### Step 1: Update Configuration

Edit `config/timeline/settings.yaml`:

```yaml
database:
  path: "postgresql://user:password@localhost:5432/saskan_timeline"
  dialect: "postgresql"
```

### Step 2: Install PostgreSQL Dependencies

```bash
poetry add psycopg2-binary
```

### Step 3: Create PostgreSQL Database

```sql
CREATE DATABASE saskan_timeline;
CREATE USER saskan_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE saskan_timeline TO saskan_user;
```

### Step 4: Initialize Schema

```bash
poetry run saskan-timeline db init
```

### Step 5: Add Constraints (Optional)

For PostgreSQL, you can add CHECK constraints or ENUMs:

```python
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM

# CHECK constraint
settlement_type = Column(
    String,
    CheckConstraint("settlement_type IN ('ring_town', 'market_town', ...)"),
    nullable=False
)

# PostgreSQL ENUM
SettlementTypeEnum = ENUM(
    'ring_town', 'market_town', 'hamlet', 'village',
    name='settlement_type_enum'
)
settlement_type = Column(SettlementTypeEnum, nullable=False)
```

---

## Performance

### Indexes

Automatically created indexes:

- Primary keys on all tables
- Unique constraints (settlement names, etc.)
- Foreign key columns
- Temporal columns (founded_astro_day, dissolved_astro_day, astro_day)
- Status columns (is_active)

### Query Optimization

Use eager loading for relationships:

```python
from sqlalchemy.orm import joinedload

# Load settlement with related objects
settlement = session.query(Settlement)\
    .options(joinedload(Settlement.province))\
    .options(joinedload(Settlement.parent))\
    .filter(Settlement.name == "Ingar")\
    .one()

# Limit results
recent_events = session.query(Event)\
    .filter(Event.astro_day >= 1000)\
    .order_by(Event.astro_day.desc())\
    .limit(100)\
    .all()
```

---

## Common Patterns

### Creating Related Objects

```python
from app_timeline.models import Region, Province, Settlement

# Create hierarchy
region = Region(name="Northern Territories", founded_astro_day=0)
province = Province(name="Fatunik", founded_astro_day=100, region=region)
settlement = Settlement(
    name="Ingar",
    settlement_type="ring_town",
    founded_astro_day=100,
    province=province
)

session.add(region)
session.add(province)
session.add(settlement)
session.commit()
```

### Time-Series Snapshots

```python
from app_timeline.models import Settlement, SettlementSnapshot

# Create settlement
ingar = Settlement(name="Ingar", settlement_type="ring_town", founded_astro_day=0)
session.add(ingar)
session.flush()

# Create snapshots at different points in time
for day in [0, 100, 200, 300]:
    snapshot = SettlementSnapshot(
        settlement=ingar,
        astro_day=day,
        population_total=1000 + (day * 10),
        population_by_species={
            "huum": 900 + (day * 9),
            "sint": 100 + day
        }
    )
    session.add(snapshot)

session.commit()
```

### Event Deprecation

```python
from app_timeline.models import Event

# Original event (later found to be incorrect)
original = Event(
    astro_day=100,
    event_type="battle",
    title="Original Description"
)
session.add(original)
session.flush()

# Corrected event
corrected = Event(
    astro_day=100,
    event_type="battle",
    title="Corrected Description"
)
session.add(corrected)
session.flush()

# Mark original as deprecated
original.is_deprecated = True
original.superseded_by_id = corrected.id
session.commit()
```

---

## Troubleshooting

### Database Locked

**Symptom:** `sqlite3.OperationalError: database is locked`

**Causes:**

- Multiple processes writing simultaneously
- Unclosed DBeaver connections
- Hanging pytest processes

**Solutions:**

- Close all DBeaver connections
- Kill hanging processes: `ps aux | grep python`
- Reset database: `saskan-timeline db drop --yes && saskan-timeline db init`

### Relationship Loading Errors

**Symptom:** `DetachedInstanceError` when accessing relationships

**Cause:** Accessing relationships after session is closed

**Solution:**

```python
# Keep session open
session = get_session()
settlement = session.query(Settlement).get(1)
province = settlement.province  # Access while session is active
session.close()

# Or use eager loading
from sqlalchemy.orm import joinedload
settlement = session.query(Settlement)\
    .options(joinedload(Settlement.province))\
    .get(1)
session.close()
# Now province is loaded even after session closes
```

### Schema Changes Not Reflected

**Symptom:** Old table structure persists after model changes

**Cause:** SQLite doesn't support ALTER TABLE for complex changes

**Solution:**

```bash
# Drop and recreate (development only!)
saskan-timeline db drop --yes
saskan-timeline db init
```

---

## Developer Workflow

### Adding a New Model

1. Create model file in `app_timeline/models/`
2. Define model class with appropriate mixins
3. Add imports to `app_timeline/models/__init__.py`
4. Update `validate_schema()` in schema.py with expected table name
5. Write tests in `tests/timeline/test_models.py`
6. Update documentation

### Adding a CLI Command

1. Determine appropriate command group (data, list, update, io)
2. Add command function in corresponding CLI module:
   - `cli_data.py` for create operations
   - `cli_list.py` for query operations
   - `cli_update.py` for update/delete operations
   - `cli_import_export.py` for bulk operations
3. Use appropriate service layer class for business logic
4. Use Typer decorators for arguments/options
5. Use Rich library for formatted output (tables, prompts, etc.)
6. Write tests in `tests/timeline/test_cli_*.py`
7. Update documentation

### Schema Changes (MVP Phase)

1. Modify model class in appropriate file
2. Drop database: `saskan-timeline db drop --yes`
3. Recreate database: `saskan-timeline db init`
4. Update tests if needed
5. Update documentation
6. Commit changes with descriptive message

**Note:** Once schema stabilizes, add Alembic for proper migrations.

---

## Service Layer

The service layer provides business logic and data access patterns for all entities.

### Base Service Pattern

All services inherit from `BaseService` which provides:

- Context manager support (`with` statement) for automatic session management
- Common CRUD operations (`create`, `get_by_id`, `update`, `delete`)
- Soft delete support (sets `is_active=False`)
- Hard delete support (permanent removal)
- List operations with filtering

### Service Classes

Each entity type has a dedicated service class:

- `EpochService` - Epoch management
- `RegionService` - Region operations
- `ProvinceService` - Province operations with region filtering
- `SettlementService` - Settlement operations with type/province filtering
- `EntityService` - Entity operations with type/temporal filtering
- `EventService` - Event operations with multiple filter options
- `RouteService` - Route operations with settlement/type filtering
- `SnapshotService` - Snapshot operations with settlement/temporal filtering

### Usage Pattern

```python
from app_timeline.services import EpochService

# Context manager ensures proper session cleanup
with EpochService() as service:
    epoch = service.create_epoch(
        name="Early Era",
        start_astro_day=0,
        end_astro_day=1000,
        description="The beginning"
    )

    # Query operations
    all_epochs = service.list_all()
    epoch = service.get_by_id(1)
    epoch = service.get_by_name("Early Era")

    # Update operations
    updated = service.update(1, name="Updated Name")

    # Delete operations
    service.delete(1, hard=False)  # Soft delete (if supported)
    service.delete(1, hard=True)   # Hard delete
```

---

## CLI Implementation

The CLI is organized into four command groups, each in its own module.

### Command Groups

**data** - Create operations (`cli_data.py`)
- Commands: `add-epoch`, `add-region`, `add-province`, `add-settlement`, `add-entity`, `add-event`, `add-route`, `add-snapshot`
- Pattern: Collect parameters, call service layer, display success/error

**list** - Query operations (`cli_list.py`)
- Commands: `epochs`, `regions`, `provinces`, `settlements`, `entities`, `events`, `routes`, `snapshots`
- Pattern: Query via service layer, format as Rich table, display results
- Features: Filtering by type/region/province/settlement/entity/temporal range, `--all` flag for inactive records

**update** - Update/Delete operations (`cli_update.py`)
- Commands: `epoch`, `region`, `province`, `settlement`, `entity`, `event`, `route`, `snapshot` (for updates)
- Commands: `delete-epoch`, `delete-region`, etc. (for deletions)
- Pattern: Collect parameters, call service layer, display success/error
- Features: Partial updates (only specified fields), soft delete (default), `--hard` flag for permanent deletion, `--yes` flag to skip confirmation

**io** - Import/Export operations (`cli_import_export.py`)
- Commands: `export`, `import`
- Export features: `--type` filter, `--include-inactive` flag
- Import features: `--dry-run` preview, `--skip-existing` flag
- Format: JSON (structured data interchange)

### Delete Behavior

**Soft Delete** (models with `is_active` field):
- Sets `is_active=False`
- Record preserved in database
- Excluded from default queries
- Applies to: Region, Province, Settlement, Entity, Route

**Hard Delete** (always):
- Permanent removal from database
- No `is_active` field or conceptually immutable
- Applies to: Epoch (definitional), Snapshot (observational)

**Special Case** (Event):
- Uses `is_deprecated` field instead of `is_active`
- Soft delete sets `is_deprecated=True`

---

## Utility Functions

### Temporal Conversion (`utils/temporal.py`)

Provides functions for converting between Saskan temporal units:

**Constants:**
- `PULSES_PER_DAY = 86400` (1 pulse = 1 second)
- `DAYS_PER_TURN = 365.25` (1 turn = 1 solar year)
- `DAYS_PER_DECADE = 3652.5` (10 turns)
- `DAYS_PER_CENTURY = 36525` (100 turns)
- `DAYS_PER_SHELL = 48213` (132 turns, Terpin lifespan)

**Conversion Functions:**
- `days_to_turns(days)`, `turns_to_days(turns)`
- `days_to_decades(days)`, `decades_to_days(decades)`
- `days_to_centuries(days)`, `centuries_to_days(centuries)`
- `days_to_shells(days)`, `shells_to_days(shells)`

**Formatting Functions:**
- `format_duration(days, use_turns=True)` - Human-readable duration string
- `format_lifespan(founded_day, dissolved_day)` - Entity lifespan with duration

### Validation (`utils/validation.py`)

Provides reusable validation functions for data integrity:

**Constants:**
- `VALID_SETTLEMENT_TYPES` - Allowed settlement types
- `VALID_ENTITY_TYPES` - Allowed entity types
- `VALID_EVENT_TYPES` - Allowed event types
- `VALID_ROUTE_TYPES` - Allowed route types
- `VALID_ROUTE_DIFFICULTIES` - Allowed difficulty levels
- `GRID_X_MIN`, `GRID_X_MAX`, `GRID_Y_MIN`, `GRID_Y_MAX` - Grid bounds

**Validation Functions:**
- `validate_date_range(start, end, allow_equal=False)` - Temporal range validation
- `validate_grid_coordinates(x, y)` - Geographic coordinate validation
- `validate_settlement_type(type)` - Settlement type validation
- `validate_entity_type(type)` - Entity type validation
- `validate_event_type(type)` - Event type validation
- `validate_route_type(type)` - Route type validation
- `validate_route_difficulty(difficulty)` - Difficulty validation
- `validate_positive(value, field_name)` - Value > 0 validation
- `validate_non_negative(value, field_name)` - Value >= 0 validation

---

## Best Practices and Common Patterns

### ADR-008: Metadata and Description Management (PR-003a)

The system implements ADR-008 with two mixins for flexible data storage:

**DescriptionMixin** - Programmatic description management:
```python
# Models with description field: Epoch, Region, Province
epoch = Epoch(name="Early Era", description="The founding period")

# Programmatic methods
epoch.update_description("Updated description text")
epoch.clear_description()
```

**MetadataMixin** - Flat structure validation:
```python
# All models have meta_data field via MetadataMixin
region = Region(name="Northlands", meta_data={"climate": "cold", "population_density": "sparse"})

# Validation: Only flat key-value pairs allowed
region.update_metadata({"climate": "temperate"}, mode="merge")  # ✓ Valid
region.update_metadata({"nested": {"key": "value"}})  # ✗ Raises ValueError
region.update_metadata({"array": [1, 2, 3]})  # ✗ Raises ValueError

# Programmatic methods
region.update_metadata({"key": "value"}, mode="replace")  # Replace all
region.update_metadata({"key": "value"}, mode="merge")  # Merge with existing
region.remove_metadata_keys(["old_key"])
region.clear_metadata()
value = region.get_metadata_value("climate", default="unknown")
has_key = region.has_metadata_key("climate")
```

**IMPORTANT: SQLAlchemy JSON Mutation Tracking**

When modifying JSON fields in-place, you MUST tell SQLAlchemy about the change:

```python
from sqlalchemy.orm.attributes import flag_modified

# Wrong - SQLAlchemy won't detect the change
region.meta_data["new_key"] = "value"
session.commit()  # Change NOT persisted!

# Correct - Use programmatic methods (they handle flag_modified internally)
region.update_metadata({"new_key": "value"}, mode="merge")
session.commit()  # ✓ Change persisted

# Or manually flag the modification
region.meta_data["new_key"] = "value"
flag_modified(region, "meta_data")
session.commit()  # ✓ Change persisted
```

### Service Context Manager Pattern

Services use context managers for automatic session cleanup. **Critical**: Extract IDs before exiting context to avoid `DetachedInstanceError`:

```python
# Wrong - DetachedInstanceError when accessing region.id outside context
with RegionService() as region_service:
    region = region_service.create_region(name="Test Region")

with ProvinceService() as province_service:
    # Error! region is detached from session
    province = province_service.create_province(name="Test Province", region_id=region.id)

# Correct - Extract ID while in context
with RegionService() as region_service:
    region = region_service.create_region(name="Test Region")
    region_id = region.id  # Extract ID before exiting context

with ProvinceService() as province_service:
    # ✓ Works! Using ID, not detached object
    province = province_service.create_province(name="Test Province", region_id=region_id)
```

### Snapshot Interpolation (PR-003a)

The system supports linear interpolation for demographic data across region, province, and settlement levels:

```python
from app_timeline.services import RegionSnapshotService

with RegionSnapshotService() as service:
    # Create sparse snapshots
    service.create_snapshot(region_id=1, astro_day=100, population_total=50000,
                          population_by_species={"huum": 40000, "sint": 10000})
    service.create_snapshot(region_id=1, astro_day=200, population_total=70000,
                          population_by_species={"huum": 50000, "sint": 20000})

    # Interpolate at day 150 (midpoint)
    interpolated = service.get_interpolated(region_id=1, astro_day=150)

    # Returns dict with:
    # - population_total: 60000 (linear interpolation)
    # - population_by_species: {"huum": 45000, "sint": 15000} (per-component interpolation)
    # - snapshot_type: "interpolated"
    # - interpolation_info: metadata about source snapshots
    # - cultural_composition, economic_data: from nearest "before" snapshot (not interpolated)
```

**Interpolation Behavior:**
- **Linear interpolation** for `population_total` and breakdown fields (`population_by_species`, `population_by_habitat`)
- **Nearest snapshot (before target)** for JSON fields (`cultural_composition`, `economic_data`, `meta_data`)
- **Edge cases handled**: no data (None), before first snapshot, after last snapshot, exact match

### Testing Patterns

**Test File Organization (PR-003a update):**
- `test_snapshot_services.py` - Region and province snapshot service tests (20 tests)
- `test_models.py` - Added ADR-008 mixin tests, snapshot model tests (18 new tests)

**Negative Testing:**
Services validate inputs and raise `ValueError` for invalid data:

```python
# Test invalid inputs
with pytest.raises(ValueError, match="does not exist"):
    service.create_province(name="Test", region_id=999)  # Invalid FK

with pytest.raises(ValueError, match="must be >= 0"):
    service.create_snapshot(region_id=1, astro_day=-100, population_total=5000)  # Negative day

with pytest.raises(ValueError, match="already exists"):
    service.create_snapshot(region_id=1, astro_day=100, population_total=5000)
    service.create_snapshot(region_id=1, astro_day=100, population_total=6000)  # Duplicate
```

**Testing with Multiple Services:**

```python
def test_multi_service_pattern(db_session):
    """Pattern for tests requiring multiple related entities."""
    # Create hierarchy: Region -> Province -> Settlement
    with RegionService() as region_service:
        region = region_service.create_region(name="Test Region")
        region_id = region.id  # Extract ID before context exit

    with ProvinceService() as province_service:
        province = province_service.create_province(name="Test Province", region_id=region_id)
        province_id = province.id

    with SettlementService() as settlement_service:
        settlement = settlement_service.create_settlement(
            name="Test City", province_id=province_id, settlement_type="city"
        )
        settlement_id = settlement.id

    # Now use extracted IDs for assertions or further operations
    assert settlement_id is not None
```

### Schema Updates

**Breaking Schema Changes:**
PR-003a (v0.2.0 → v0.3.0) introduced breaking changes:
- Added `region_snapshots` and `province_snapshots` tables
- Added `snapshot_type` and `granularity` fields to all snapshot tables
- Added `description` field to `epochs`, `regions`, `provinces`
- Changed `population` to `population_total` in snapshots

**Migration path:**
```bash
# Drop old database
poetry run saskan-timeline db drop --yes

# Recreate with new schema
poetry run saskan-timeline db init

# Re-import data (if backed up to JSON)
poetry run saskan-timeline io import backup.json
```

### Performance Considerations

**Snapshot Queries:**
- Use filtering by `snapshot_type` and `granularity` for targeted queries
- Index on `(region_id, astro_day)` and `(province_id, astro_day)` optimizes temporal queries
- For large datasets, consider filtering by time range before interpolation

**Metadata Queries:**
SQLite JSON queries are limited. For production, use PostgreSQL with JSON operators:

```python
# PostgreSQL JSON queries (future)
from sqlalchemy.dialects.postgresql import JSONB

# Query by metadata value
regions = session.query(Region).filter(
    Region.meta_data['climate'].astext == 'cold'
).all()
```

---

## Future Enhancements

### Planned Features

1. **Alembic Migrations** - Proper schema versioning when stable
2. **Full-Text Search** - PostgreSQL FTS for event/description search
3. **Spatial Queries** - PostGIS extension for geographic queries
4. **Materialized Views** - Pre-computed timeline summaries
5. **Table Partitioning** - Partition by time period for performance
6. **Replication** - Read replicas for query scaling

### Extension Points

- **Custom Validators** - Soft validation with warnings
- **Event Sourcing** - Track all changes as events
- **Audit Logging** - Detailed change tracking
- **REST API** - FastAPI or Flask-RESTX API layer
- **GraphQL API** - For complex queries
- **Web Interface** - Admin interface for data management

---

## References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Version History

**v0.3.0** (2025-12-30) - PR-003a: Schema Refactoring for Macro-Scale Simulation

- Added `RegionSnapshot` and `ProvinceSnapshot` models for multi-scale demographic tracking
- Implemented snapshot interpolation services for sparse demographic data
- Added `snapshot_type` and `granularity` fields to all snapshot tables (census/simulation/estimate, year/decade/century)
- Implemented ADR-008: Metadata and Description Field Management
  - `DescriptionMixin` for programmatic description management
  - `MetadataMixin` with flat structure validation (rejects nested objects/arrays)
  - Retrofitted `Region`, `Province`, and `Epoch` models with description fields
- CLI commands for region and province snapshot management (add, delete)
- Extended import/export to support `region_snapshots` and `province_snapshots`
- New test file: `test_snapshot_services.py` (20 tests)
- Extended `test_models.py` with ADR-008 mixin and snapshot tests (18 new tests)
- Breaking schema change: v0.2.0 → v0.3.0 (requires database recreation)
- Total test count: 243 tests (all passing)

**v0.2.0** (2025-12-29) - PR-002: CLI Implementation

- Service layer with 8 service classes and base service pattern
- Four CLI command groups (data, list, update, io) across 4 modules
- Complete CRUD operations for all 8 entity types
- JSON import/export with dry-run and skip-existing modes
- Soft delete (is_active) and hard delete support
- Temporal conversion utilities (turns, decades, centuries, shells)
- Validation utility functions with constants for all data types
- Rich-formatted table output for all list commands
- Comprehensive test suite (150 tests for CLI, 100% pass rate)
- Updated documentation with full CLI reference

**v0.1.0** (2025-12-29)

- Initial MVP release
- Database schema with 7 core tables
- SQLAlchemy ORM models with relationships
- YAML-based configuration system
- CLI for database management (init, drop, info, validate)
- Comprehensive test suite (27 tests, 100% pass rate)
- Complete user and technical documentation
