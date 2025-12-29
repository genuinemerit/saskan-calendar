# Saskan Timeline - User Guide

**Version:** 0.1.0
**Status:** MVP - Database Foundation

---

## Overview

The Saskan Timeline system is a database-backed application for managing historical timelines in the Saskan Lands universe. It tracks settlements, provinces, regions, entities (people and organizations), events, routes, and their evolution over time.

**Key Features:**

- Geographic hierarchy (Regions -> Provinces -> Settlements)
- Time-series demographic snapshots
- Event tracking with temporal references
- Relationship management (routes, hierarchies)
- Flexible metadata storage (JSON fields)
- SQLite database (with PostgreSQL migration path)

---

## Installation

```bash
# Navigate to project directory
cd /path/to/saskan-calendar

# Install dependencies
poetry install

# Verify installation
poetry run saskan-timeline --help
```

---

## Quick Start

### 1. Initialize the Database

```bash
poetry run saskan-timeline db init
```

This creates the database file at `data/timeline/saskan_timeline.db` with all required tables.

### 2. Verify Database

```bash
# Show database information
poetry run saskan-timeline db info

# Validate schema
poetry run saskan-timeline db validate
```

### 3. Drop Database (Caution!)

```bash
# Interactive confirmation
poetry run saskan-timeline db drop

# Skip confirmation
poetry run saskan-timeline db drop --yes
```

---

## Database Schema

### Core Tables

**Regions** - Top-level geographic groupings

- Multiple provinces per region
- Temporal bounds (founded/dissolved dates)

**Provinces** - Administrative divisions

- Usually one Ring Town per province (with exceptions)
- Can have 0, 1, or 2+ Ring Towns
- Part of a region (optional)

**Settlements** - Cities, towns, villages, camps

- Types: ring_town, market_town, military_camp_large, military_camp_small, hamlet, village, camp, den
- Parent-child relationships (e.g., hamlets satellite to ring towns)
- Geographic coordinates (location_x, location_y)
- Autonomous flag for independent settlements

**Settlement Snapshots** - Time-series demographic data

- Population totals and breakdowns (by species, habitat)
- Cultural composition (language, religion, tribes)
- Economic data (industries, trade goods)
- Multiple snapshots per settlement at different dates

**Routes** - Connections between settlements

- Types: trail, road, paved_road, ring_road, river, sea_route, mountain_pass
- Difficulty levels: trivial, easy, moderate, difficult, very_difficult, extreme
- Distance, terrain notes, hazards

**Entities** - People, organizations, groups

- Types: person, organization, group, collective
- Birth/death or formation/dissolution dates
- Species, roles, affiliations (in metadata)

**Events** - Historical timeline events

- Types: founding, dissolution, battle, treaty, migration, natural_disaster, cultural, political, economic
- Location references
- Deprecation support (superseding events)

---

## Time System

The timeline uses **astro_day** as the fundamental unit of time:

- Integer representing days since the astro epoch
- Day 0 is the reference point
- All dates are stored as astro_day values
- Calendar conversion (Fatunik, Lunar, etc.) handled by app_calendar

**Example:**

- `founded_astro_day: 0` - Entity founded at Day 0
- `dissolved_astro_day: 5000` - Entity dissolved at Day 5,000
- `astro_day: 100` - Snapshot taken on Day 100

---

## Configuration

Configuration is stored in `config/timeline/settings.yaml`:

```yaml
database:
  path: "data/timeline/saskan_timeline.db"
  dialect: "sqlite"
  echo: false

settlement_types:
  - ring_town
  - market_town
  # ... more types

species:
  - huum  # Human
  - sint  # Sentients
  # ... more species

route_types:
  - trail
  - road
  - paved_road
  # ... more types
```

These values serve as **guidance** - no database constraints are enforced. You can use non-standard values, though warnings may be added in future versions.

---

## CLI Reference

### Database Management

```bash
# Initialize database
saskan-timeline db init

# Show database info (path, tables, row counts)
saskan-timeline db info

# Validate schema
saskan-timeline db validate

# Drop all tables (with confirmation)
saskan-timeline db drop

# Drop tables without confirmation
saskan-timeline db drop --yes
```

### Application Info

```bash
# Show version
saskan-timeline version
```

---

## Data Management

The timeline system provides comprehensive CLI commands for creating, querying, updating, and deleting timeline data.

### Creating Data

Use the `data` command group to add new records:

```bash
# Add a new epoch
saskan-timeline data add-epoch --name "Early Era" --start 0 --end 1000

# Add a new region
saskan-timeline data add-region --name "Northlands"

# Add a new province
saskan-timeline data add-province --name "North Province" --region 1

# Add a new settlement
saskan-timeline data add-settlement --name "Ingar" --type city --province 1 --grid-x 20 --grid-y 15

# Add a new entity
saskan-timeline data add-entity --name "King Aldric" --type person --founded 100

# Add a new event
saskan-timeline data add-event --title "Founding of Ingar" --type founding --day 50 --settlement 1

# Add a new route
saskan-timeline data add-route --origin 1 --destination 2 --distance 50 --type road

# Add a demographic snapshot
saskan-timeline data add-snapshot --settlement 1 --day 100 --population 5000
```

### Querying Data

Use the `list` command group to query records:

```bash
# List all epochs
saskan-timeline list epochs

# List all regions
saskan-timeline list regions

# List all provinces (or filter by region)
saskan-timeline list provinces
saskan-timeline list provinces --region 1

# List all settlements (or filter by type/province)
saskan-timeline list settlements
saskan-timeline list settlements --type city
saskan-timeline list settlements --province 1

# List all entities (or filter by type/day)
saskan-timeline list entities
saskan-timeline list entities --type person
saskan-timeline list entities --day 500

# List all events (or filter by type/day/settlement/entity/range)
saskan-timeline list events
saskan-timeline list events --type founding
saskan-timeline list events --settlement 1
saskan-timeline list events --start-day 0 --end-day 1000

# List all routes (or filter by settlement/type)
saskan-timeline list routes
saskan-timeline list routes --settlement 1
saskan-timeline list routes --type road

# List all snapshots (or filter by settlement/range)
saskan-timeline list snapshots
saskan-timeline list snapshots --settlement 1
saskan-timeline list snapshots --start-day 0 --end-day 1000

# Include inactive records
saskan-timeline list regions --all
```

### Updating Data

Use the `update` command group to modify records:

```bash
# Update an epoch
saskan-timeline update epoch 1 --name "New Name" --start 5 --end 2000

# Update a region
saskan-timeline update region 1 --name "Updated Region"

# Update a province
saskan-timeline update province 1 --name "Updated Province" --region 2

# Update a settlement
saskan-timeline update settlement 1 --name "New Name" --type town --grid-x 25

# Update an entity
saskan-timeline update entity 1 --name "Updated Name" --dissolved 500

# Update an event
saskan-timeline update event 1 --title "Updated Event" --day 75

# Update a route
saskan-timeline update route 1 --distance 75 --type trail

# Update a snapshot
saskan-timeline update snapshot 1 --population 6000
```

### Deleting Data

Use the `delete-*` commands within the `update` group:

```bash
# Delete records (soft delete for entities with is_active field)
saskan-timeline update delete-region 1
saskan-timeline update delete-province 1
saskan-timeline update delete-settlement 1
saskan-timeline update delete-entity 1
saskan-timeline update delete-event 1
saskan-timeline update delete-route 1

# Hard delete (permanent removal)
saskan-timeline update delete-region 1 --hard

# Skip confirmation prompt
saskan-timeline update delete-region 1 --yes

# Note: Epochs and snapshots always use hard delete (no soft delete)
saskan-timeline update delete-epoch 1
saskan-timeline update delete-snapshot 1
```

### Import/Export

Use the `io` command group for bulk operations:

```bash
# Export all data to JSON
saskan-timeline io export output.json

# Export specific entity type
saskan-timeline io export epochs.json --type epochs

# Include inactive records in export
saskan-timeline io export all_data.json --include-inactive

# Import data from JSON
saskan-timeline io import data.json

# Preview import without making changes
saskan-timeline io import data.json --dry-run

# Skip existing records (match by name)
saskan-timeline io import data.json --skip-existing
```

---

## Development Workflow

### Typical Development Cycle

1. **Design Iteration**

   ```bash
   # Make schema changes in app_timeline/models/
   saskan-timeline db drop --yes
   saskan-timeline db init
   saskan-timeline db validate
   ```

2. **Data Entry**

   ```bash
   # Add data via CLI
   saskan-timeline data add-epoch --name "Early Era" --start 0 --end 1000
   saskan-timeline data add-region --name "Northlands"
   saskan-timeline data add-province --name "North Province" --region 1

   # Or import from JSON file
   saskan-timeline io import initial_data.json
   ```

3. **Query and Export**

   ```bash
   # Query data
   saskan-timeline list epochs
   saskan-timeline list settlements --type city

   # Export for backup or sharing
   saskan-timeline io export backup.json
   ```

### Testing

```bash
# Run all timeline tests
poetry run pytest tests/timeline/ -v

# Run specific test file
poetry run pytest tests/timeline/test_models.py -v

# Run with coverage
poetry run pytest tests/timeline/ --cov=app_timeline
```

---

## Database Tools

The timeline database is a standard SQLite file. You can use external tools for inspection:

### Recommended: DBeaver

1. Open DBeaver
2. Create new SQLite connection
3. Point to `data/timeline/saskan_timeline.db`
4. Browse tables, run queries, inspect schema

**Command Line:**

```bash
# Open database in sqlite3
sqlite3 data/timeline/saskan_timeline.db

# Example queries
.tables
.schema settlements
SELECT * FROM settlements;
```

---

## Migration Path

The system is designed for easy migration from SQLite to PostgreSQL:

1. **Current (MVP):** SQLite for development and prototyping
2. **Future (Production):** PostgreSQL for scalability and features
   - Change `dialect` in settings.yaml
   - Update connection string
   - Add database constraints (CHECK, ENUM) at migration time

---

## Troubleshooting

### Database locked error

- Close any open connections (DBeaver, sqlite3 sessions)
- Ensure only one process accesses the database at a time

### Missing tables

```bash
saskan-timeline db validate
saskan-timeline db init
```

### Schema changes not reflected

```bash
# Drop and recreate database
saskan-timeline db drop --yes
saskan-timeline db init
```

### Import errors

```bash
# Reinstall dependencies
poetry install
```

---

## Temporal Conversion Utilities

The system includes utility functions for converting between different time units in the Saskan calendar:

**Time Units:**
- pulse: 1 second (86,400 pulses per day)
- turn: 365.25 days (synonym for solar year)
- decade: 10 turns (3,652.5 days)
- century: 100 turns (36,525 days)
- shell: 132 turns (48,213 days - average Terpin lifespan)

**Available Functions:**
- `days_to_turns()`, `turns_to_days()` - Convert between days and turns
- `days_to_decades()`, `decades_to_days()` - Convert between days and decades
- `days_to_centuries()`, `centuries_to_days()` - Convert between days and centuries
- `days_to_shells()`, `shells_to_days()` - Convert between days and shells
- `format_duration()` - Format duration in human-readable form
- `format_lifespan()` - Format entity lifespan with duration

**Example:**
```python
from app_timeline.utils import days_to_turns, format_duration

# Convert 1000 days to turns
turns = days_to_turns(1000)  # ~2.74 turns

# Format a duration
duration = format_duration(1000)  # "2.74 turns"
```

---

## Next Steps

With the CLI implementation complete, upcoming work includes:

1. **Validation Integration** - Apply validation utilities across all data entry points
2. **Reporting** - Generate timeline reports and visualizations
3. **Integration** - Connect with app_calendar for date conversion
4. **Parquet Export** - Add Parquet format export for OLAP/DuckDB analysis
5. **Advanced Queries** - Additional filtering and search capabilities

---

## Support

- GitHub Issues: <https://github.com/genuinemerit/saskan-calendar/issues>
- Technical Documentation: See TECHNICAL.md in this directory
- ADRs: See /docs/design/ for architecture decision records

---

## Version History

**v0.2.0** (2025-12-29) - PR-002: CLI Implementation

- Complete CLI command implementation (data, list, update, io groups)
- Create, query, update, and delete operations for all entity types
- JSON import/export functionality with dry-run and skip-existing modes
- Temporal conversion utilities (turns, decades, centuries, shells)
- Validation utility functions for all data types
- Soft delete support (is_active field) with hard delete option
- Rich-formatted table output for list commands
- Comprehensive test suite (150 tests total for CLI features)

**v0.1.0** (2025-12-29)

- Initial MVP release
- Database schema with 7 core tables
- CLI for database management
- Configuration system
- Comprehensive test suite (27 tests)
