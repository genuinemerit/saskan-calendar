# Saskan Timeline - Technical Documentation

**Version:** 0.1.0  
**Python:** 3.12  
**Framework:** SQLAlchemy 2.0

---

## Architecture Overview

The timeline system follows a layered architecture with clear separation of concerns.

### Layers

1. **CLI Layer** - Typer + Rich for user interaction
2. **Business Logic** - Future application logic
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
  config.py             # Configuration management
  models/               # SQLAlchemy models
    __init__.py
    base.py            # Base classes and mixins
    entity.py          # Entity model
    event.py           # Event model
    province.py        # Province and Region models
    route.py           # Route model
    settlement.py      # Settlement and SettlementSnapshot models
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
  test_models.py       # Model tests
```

---

## Database Schema

### Table Relationships

- Region (1) ---< (M) Province
- Province (1) ---< (M) Settlement
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
- founded_astro_day (INTEGER, NOT NULL)
- dissolved_astro_day (INTEGER, nullable)
- is_active (BOOLEAN, NOT NULL, default=True)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

#### provinces

Stores administrative divisions within regions.

**Columns:**

- id (INTEGER, PK)
- name (VARCHAR, UNIQUE, NOT NULL)
- region_id (INTEGER, FK -> regions.id)
- founded_astro_day (INTEGER, NOT NULL)
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
- population_total (INTEGER, NOT NULL)
- population_by_species (JSON, nullable)
- population_by_habitat (JSON, nullable)
- cultural_composition (JSON, nullable)
- economic_data (JSON, nullable)
- meta_data (JSON, nullable)
- created_at (DATETIME, NOT NULL)

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

1. Add command function in `app_timeline/cli.py`
2. Use Typer decorators for arguments/options
3. Use Rich library for formatted output
4. Test manually
5. Update documentation

### Schema Changes (MVP Phase)

1. Modify model class in appropriate file
2. Drop database: `saskan-timeline db drop --yes`
3. Recreate database: `saskan-timeline db init`
4. Update tests if needed
5. Update documentation
6. Commit changes with descriptive message

**Note:** Once schema stabilizes, add Alembic for proper migrations.

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

**v0.1.0** (2025-12-29)

- Initial MVP release
- Database schema with 7 core tables
- SQLAlchemy ORM models with relationships
- YAML-based configuration system
- CLI for database management (init, drop, info, validate)
- Comprehensive test suite (27 tests, 100% pass rate)
- Complete user and technical documentation
