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

**Current Status:** The MVP provides database schema and management commands. Data import/export and CRUD operations will be added in future iterations.

**Planned Features:**

- CLI commands for adding/editing settlements, events, entities
- CSV/JSON import for bulk data loading
- Query commands for searching and filtering
- Export to various formats (JSON, CSV, markdown)

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

2. **Data Entry** (future)

   ```bash
   # Add data via CLI or Python API
   ```

3. **Query and Export** (future)

   ```bash
   # Query data, generate reports
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

## Next Steps

With the database foundation in place, upcoming work includes:

1. **Data Entry CLI** - Commands to add/edit settlements, events, entities
2. **Query System** - Search and filter capabilities
3. **Import/Export** - CSV/JSON data loading and export
4. **Reporting** - Generate timeline reports and visualizations
5. **Integration** - Connect with app_calendar for date conversion

---

## Support

- GitHub Issues: <https://github.com/genuinemerit/saskan-calendar/issues>
- Technical Documentation: See TECHNICAL.md in this directory
- ADRs: See /docs/design/ for architecture decision records

---

## Version History

**v0.1.0** (2025-12-29)

- Initial MVP release
- Database schema with 7 core tables
- CLI for database management
- Configuration system
- Comprehensive test suite (27 tests)
