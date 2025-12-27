# ADR 001: SQLite as Source of Truth for Worldbuilding Data

**Status:** Proposed

**Date:** 2024-12-27

## Context

The Saskantinon worldbuilding project requires tracking entities (cities, populations, events, infrastructure) across 2000+ years of simulated history. Previous attempts have explored:
- JSON as primary database (complex queries difficult, relationship management awkward)
- OpenAI Codex + prompts (insufficient consistency, state management issues)
- Bespoke SQL with custom code (correct instinct, needs refinement)

The system must support:
- Complex temporal queries ("What did Beshquahoek look like in 1200 AA?")
- Relationship modeling (cities connected by roads, events affecting regions)
- Efficient year-by-year simulation runs
- Version control and branching (alternative timelines)
- Integration with Python simulation engine

## Decision

**We will use SQLite as the canonical source of truth** for all worldbuilding data, with the following characteristics:

1. **Relational schema** designed around temporal snapshots and entity relationships
2. **Single-file database** (portable, version-controllable via Git LFS if needed)
3. **Accessed via Python** using `sqlite3` or `sqlalchemy` as needed
4. **No external dependencies** (PostgreSQL, MySQL, etc.) to maintain simplicity

JSON will be used **only for configuration** (simulation parameters, regional settings), not as a data store.

## Consequences

### Positive

- **Query power:** Complex temporal and relational queries are straightforward
  - "Show all cities in Fatunik Dominion in year 1500"
  - "Trace migration flows from Ingar to Juuj, 2000-2100 AA"
  - "Find all events affecting Kahila region with shock < 0.8"

- **ACID guarantees:** Transactions ensure data consistency during simulation runs

- **Standard SQL:** Decades of experience directly applicable; no new query language

- **Tooling:** Can use DB Browser for SQLite, DBeaver, or VS Code extensions for inspection

- **Versioning:** Can commit entire database state, branch for "what-if" scenarios

- **Performance:** SQLite handles millions of rows efficiently (2000 years × 100 cities × snapshots = manageable)

### Negative

- **Binary format:** Diffs in Git are opaque (mitigated by exporting key tables to CSV for version control)

- **Schema migrations:** Requires discipline when evolving structure (use Alembic or manual versioning)

- **Concurrency:** Single-writer limitation (not an issue for single-user worldbuilding workflow)

- **Must learn/remember:** Schema design choices affect simulation code structure

### Neutral

- **Not NoSQL:** If graph-heavy queries dominate later, could add Neo4j alongside, but SQLite + networkx should suffice

## Implementation Notes

- Start with minimal schema (cities, snapshots, events)
- Use foreign keys with `PRAGMA foreign_keys = ON`
- Create indexes on `(entity_id, year)` for temporal queries
- Consider partitioning snapshots by era for very large datasets (premature optimization for now)
- Use views for common queries ("current_state" = max(year) for each entity)

## Alternatives Considered

**PostgreSQL:**
- Pro: More powerful, better concurrency, JSON support
- Con: Overkill for single-user, local-first workflow; requires server process
- **Rejected:** Complexity exceeds needs

**DuckDB:**
- Pro: Analytical queries, Parquet support, modern SQL
- Con: Less mature ecosystem, fewer tools
- **Deferred:** Consider if analytical queries become bottleneck

**JSON + Document DB (MongoDB, etc.):**
- Pro: Flexible schema, easy to version control
- Con: Complex temporal queries painful, relationship modeling awkward
- **Rejected:** Already explored, found wanting

## References

- SQLite Documentation: https://www.sqlite.org/docs.html
- Time-series data modeling: https://www.timescale.com/blog/time-series-data-postgresql-10-vs-timescaledb-816ee808bac5/ (concepts apply to SQLite)
