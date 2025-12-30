# ADR-008: Metadata and Description Field Management

**Status:** Proposed

**Date:** 2024-12-30

## Context

The saskan-timelines database uses a hybrid schema approach:

- **Formal columns:** Queryable, indexed, typed data (e.g.,
  `population_total`, `founded_year`)
- **Description fields:** TEXT columns for human-readable descriptions (e.g.,
  `cities.description`)
- **Metadata columns:** JSON-typed fields for flexible, user-defined key-value
  pairs (e.g., `cities.meta_data`)

### Description and metadata appear on multiple entity types

- Cities: `cities.description`, `cities.meta_data`
- Regions: `regions.description`, `regions.meta_data`
- Events: `events.description`, `events.meta_data`
- Snapshots: May have description/metadata (optional)

Both fields are optional (NOT NULL = False).

### Current state

- Description and metadata can be set at record creation
- No update capabilities exist for either field
- No standard semantics for modifying existing values
- No service layer methods for removing/clearing these fields

### Use cases for description fields

1. **Entity summaries:** Human-readable overview of city, region, event
1. **Narrative context:** "Beshquahoek grew rapidly after canal completion..."
1. **Working notes:** Temporary notes during worldbuilding process
1. **AI-generated drafts:** Store AI-generated text before curation

### Use cases for metadata

1. **User annotations:** "This city is interesting for Story Arc 3"
1. **Flexible attributes:** "climate_notes": "Unusually dry winters"
1. **Temporary flags:** "needs_review": true
1. **External references:** "worldanvil_id": "12345"
1. **Experimental data:** Testing new attributes before formalizing in schema

### Requirements

- Must support updating description text (replace entire field)
- Must support clearing/removing description
- Must support adding new key-value pairs to existing metadata
- Must support removing specific metadata keys
- Must support modifying values of existing metadata keys
- Must support wholesale replacement of metadata
- **Must enforce flat key-value structure for metadata** (no nesting, no lists)
- Should be consistent across all entity types
- Should not break existing records with NULL or empty values

## Decision

**We will implement standardized update semantics for both description and
metadata fields** with clear operations for each.

### Summary of Operations

| Field Type | Operations Supported | Structure Constraint |
|-----------|---------------------|---------------------|
| **Description** (TEXT) | Update (replace), Clear | Free-form text, Unicode support |
| **Metadata** (JSON) | Merge, Remove keys, Replace, Clear | **Flat key-value only** (no nesting/arrays) |

### Key principles

- Both fields are optional (NOT NULL = False)
- Both fields are updateable after creation
- Both fields support removal/clearing
- Metadata enforces flat structure via validation
- Consistent API across all entity types (Cities, Regions, Events, etc.)

---

## Part 1: Description Field Management

Description fields are simple TEXT columns used for human-readable summaries and
notes.

### Operations for Descriptions

#### 1. Update (replace entire description)

**Semantic:** Replace entire description text

```python
existing = "Old description"
update_to = "New description"
result = "New description"
```

#### 2. Clear (remove description)

**Semantic:** Set description to NULL

```python
existing = "Some description"
clear()
result = NULL
```

### Database Layer for Descriptions

#### Schema definition

```sql
-- All entity tables include:
description TEXT,  -- Optional human-readable text
```

#### Update queries

```sql
-- Update: Replace description
UPDATE cities
SET description = ?
WHERE id = ?;

-- Clear: Remove description
UPDATE cities
SET description = NULL
WHERE id = ?;
```

### Service Layer for Descriptions

#### Mixin for description management

```python
# src/timelines/models/base.py
class DescriptionMixin:
    """Mixin providing description management methods."""

    def update_description(self, text: Optional[str]) -> Optional[str]:
        """
        Update description text.

        Args:
            text: New description text, or None to clear

        Returns:
            Updated description
        """
        self.description = text
        return self.description

    def clear_description(self) -> None:
        """Remove description (set to NULL)."""
        self.description = None

    def has_description(self) -> bool:
        """Check if entity has a description."""
        return bool(self.description)
```

#### CLI for descriptions

```bash
# Update description
timeline city update <city_id> --description "New description text"

# Clear description
timeline city update <city_id> --clear-description

# Read from file (useful for long descriptions)
timeline city update <city_id> --description-file description.txt
```

#### CLI implementation

```python
@click.option(
    '--description',
    type=str,
    help='Set description text'
)
@click.option(
    '--description-file',
    type=click.File('r'),
    help='Read description from file'
)
@click.option(
    '--clear-description',
    is_flag=True,
    help='Clear description'
)
def update(city_id, description, description_file, clear_description):
    """Update city description."""

    # Validate: can't combine operations
    if sum([bool(description), bool(description_file), clear_description]) > 1:
        raise click.UsageError(
            "Can only use one of: --description, --description-file, --clear-description"
        )

    if clear_description:
        city.clear_description()
        db.commit()
        click.echo(f"Cleared description for city {city_id}")

    elif description_file:
        text = description_file.read()
        city.update_description(text)
        db.commit()
        click.echo(f"Updated description for city {city_id} from file")

    elif description:
        city.update_description(description)
        db.commit()
        click.echo(f"Updated description for city {city_id}")
```

---

## Part 2: Metadata Management

Metadata fields are JSON columns for flexible key-value pairs. **Critical
constraint: Only flat, simple key-value pairs are supported.** Nested objects,
arrays, and complex structures are not allowed.

### JSON Structure Constraints

#### Allowed (flat key-value pairs)

```json
{
  "worldanvil_id": "WA-12345",
  "importance": "high",
  "needs_review": "true",
  "story_arc": "The Pollinator Quest"
}
```

#### NOT allowed (nested objects)

```json
{
  "config": {
    "setting1": "value1",
    "setting2": "value2"
  }
}
```

#### NOT allowed (arrays/lists)

```json
{
  "tags": ["important", "review", "arc3"]
}
```

#### Rationale

- Simpler to reason about (one level only)
- Easier to display/edit in CLI
- Merge semantics are unambiguous
- Forces attribute names to be descriptive (e.g., `climate_rainfall` not nested
  `climate.rainfall`)

**Enforcement:** Service layer validates structure before persistence.

### Operations for Metadata

### 1. Merge (add/update keys, preserve others)

**Semantic:** Add new keys or update existing keys, leave other keys untouched

```python
existing = {"flag": "important", "note": "old value"}
merge_with = {"note": "new value", "tag": "added"}
result = {"flag": "important", "note": "new value", "tag": "added"}
```

### 2. Remove (delete specific keys)

**Semantic:** Remove one or more keys, leave others intact

```python
existing = {"flag": "important", "note": "value", "tag": "added"}
remove_keys = ["note", "tag"]
result = {"flag": "important"}
```

### 3. Replace (wholesale replacement)

**Semantic:** Replace entire metadata object

```python
existing = {"flag": "important", "note": "old"}
replace_with = {"new_key": "new_value"}
result = {"new_key": "new_value"}
```

### 4. Clear (remove all metadata)

**Semantic:** Set metadata to empty object or NULL

```python
existing = {"flag": "important", "note": "value"}
clear()
result = {} or NULL
```

**Default behavior:** When in doubt, use **merge** (least destructive, most
expected).

## Implementation Design

### Database Layer (SQLite JSON Functions)

#### Schema definition

```sql
-- All entity tables include:
meta_data TEXT,  -- JSON object or NULL
CHECK (meta_data IS NULL OR json_valid(meta_data))
```

#### Update queries using SQLite JSON functions

```sql
-- Merge: Add/update specific keys
UPDATE cities
SET meta_data = json_patch(
    COALESCE(meta_data, '{}'),
    json_object('key', 'value', 'another_key', 'another_value')
)
WHERE id = ?;

-- Remove: Delete specific keys
UPDATE cities
SET meta_data = json_remove(
    meta_data,
    '$.key_to_remove',
    '$.another_key_to_remove'
)
WHERE id = ?;

-- Replace: Wholesale replacement
UPDATE cities
SET meta_data = ?  -- New JSON object
WHERE id = ?;

-- Clear: Remove all metadata
UPDATE cities
SET meta_data = NULL  -- or '{}'
WHERE id = ?;
```

### Service Layer API

#### Base class for all entities with metadata

```python
# src/timelines/models/base.py
from typing import Dict, List, Optional, Any
import json

class MetadataMixin:
    """Mixin providing metadata management methods."""

    @staticmethod
    def _validate_flat_structure(data: Dict[str, Any]) -> None:
        """
        Validate that metadata is a flat key-value structure.

        Raises:
            ValueError: If data contains nested objects or arrays
        """
        for key, value in data.items():
            if isinstance(value, dict):
                raise ValueError(
                    f"Nested objects not allowed in metadata. Key '{key}' contains object."
                )
            if isinstance(value, (list, tuple)):
                raise ValueError(
                    f"Arrays not allowed in metadata. Key '{key}' contains array."
                )
            # Allow: str, int, float, bool, None
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise ValueError(
                    f"Invalid value type for key '{key}': {type(value).__name__}. "
                    f"Only str, int, float, bool, None allowed."
                )

    def update_metadata(
        self,
        updates: Dict[str, Any],
        mode: str = 'merge'
    ) -> Dict[str, Any]:
        """
        Update metadata with specified mode.

        Args:
            updates: Dictionary of key-value pairs to apply
            mode: 'merge', 'replace' (default: 'merge')

        Returns:
            Updated metadata dictionary

        Raises:
            ValueError: If mode is invalid or updates contain nested/complex structures
        """
        if mode not in ('merge', 'replace'):
            raise ValueError(f"Invalid mode: {mode}. Use 'merge' or 'replace'")

        # Validate flat structure
        self._validate_flat_structure(updates)

        if mode == 'replace':
            self.meta_data = updates
        else:  # merge
            current = self.meta_data or {}
            current.update(updates)
            self.meta_data = current

        return self.meta_data

    def merge_metadata(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method: merge updates into existing metadata."""
        return self.update_metadata(updates, mode='merge')

    def remove_metadata_keys(self, keys: List[str]) -> Dict[str, Any]:
        """
        Remove specific keys from metadata.

        Args:
            keys: List of keys to remove

        Returns:
            Updated metadata dictionary
        """
        if not self.meta_data:
            return {}

        for key in keys:
            self.meta_data.pop(key, None)

        return self.meta_data

    def clear_metadata(self) -> None:
        """Remove all metadata."""
        self.meta_data = None

    def get_metadata_value(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """Get a specific metadata value with optional default."""
        if not self.meta_data:
            return default
        return self.meta_data.get(key, default)

    def has_metadata_key(self, key: str) -> bool:
        """Check if a metadata key exists."""
        return bool(self.meta_data and key in self.meta_data)
```

#### Database persistence layer

```python
# src/timelines/persistence/metadata.py
import json
import sqlite3
from typing import Dict, List, Any, Optional

class MetadataRepository:
    """Handle metadata CRUD operations at database level."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def merge_metadata(
        self,
        table: str,
        entity_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge metadata updates into existing metadata.

        Uses SQLite json_patch for atomic updates.
        """
        updates_json = json.dumps(updates)

        cursor = self.conn.execute(f"""
            UPDATE {table}
            SET meta_data = json_patch(
                COALESCE(meta_data, '{{}}'),
                ?
            )
            WHERE id = ?
            RETURNING meta_data
        """, (updates_json, entity_id))

        result = cursor.fetchone()
        return json.loads(result[0]) if result and result[0] else {}

    def remove_metadata_keys(
        self,
        table: str,
        entity_id: int,
        keys: List[str]
    ) -> Dict[str, Any]:
        """
        Remove specific keys from metadata.

        Uses SQLite json_remove for atomic deletion.
        """
        # Build json_remove path arguments
        paths = [f'$.{key}' for key in keys]

        # SQLite json_remove takes variable arguments, so we need dynamic SQL
        placeholders = ', '.join(['?'] * len(paths))

        cursor = self.conn.execute(f"""
            UPDATE {table}
            SET meta_data = json_remove(meta_data, {placeholders})
            WHERE id = ?
            RETURNING meta_data
        """, (*paths, entity_id))

        result = cursor.fetchone()
        return json.loads(result[0]) if result and result[0] else {}

    def replace_metadata(
        self,
        table: str,
        entity_id: int,
        new_metadata: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Replace entire metadata object."""
        new_json = json.dumps(new_metadata) if new_metadata else None

        cursor = self.conn.execute(f"""
            UPDATE {table}
            SET meta_data = ?
            WHERE id = ?
            RETURNING meta_data
        """, (new_json, entity_id))

        result = cursor.fetchone()
        return json.loads(result[0]) if result and result[0] else None

    def clear_metadata(
        self,
        table: str,
        entity_id: int
    ) -> None:
        """Clear all metadata (set to NULL)."""
        self.conn.execute(f"""
            UPDATE {table}
            SET meta_data = NULL
            WHERE id = ?
        """, (entity_id,))

    def get_metadata(
        self,
        table: str,
        entity_id: int
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for an entity."""
        cursor = self.conn.execute(f"""
            SELECT meta_data FROM {table} WHERE id = ?
        """, (entity_id,))

        result = cursor.fetchone()
        return json.loads(result[0]) if result and result[0] else None
```

### CLI Interface

#### Command structure

```bash
# Add/update metadata keys (merge mode - default)
timeline city update <city_id> --meta-set key:value --meta-set another:value

# Remove specific keys
timeline city update <city_id> --meta-remove key --meta-remove another

# Replace entire metadata object
timeline city update <city_id> --meta-replace '{"new": "metadata"}'

# Clear all metadata
timeline city update <city_id> --meta-clear

# Combined operations (applied in order: merge, remove, replace)
timeline city update <city_id> \
  --meta-set tag:important \
  --meta-remove old_flag \
  --meta-set note:"Needs review"
```

#### CLI implementation (Click-based)

```python
# src/timelines/cli/city.py
import click
import json
from typing import List, Tuple

def parse_key_value(ctx, param, values: List[str]) -> List[Tuple[str, str]]:
    """Parse key:value pairs from CLI arguments."""
    pairs = []
    for value in values:
        if ':' not in value:
            raise click.BadParameter(f"Invalid format: {value}. Use key:value")
        key, val = value.split(':', 1)
        pairs.append((key.strip(), val.strip()))
    return pairs

@click.command()
@click.argument('city_id', type=int)
@click.option(
    '--meta-set',
    multiple=True,
    callback=parse_key_value,
    help='Add or update metadata key:value pair (can be used multiple times)'
)
@click.option(
    '--meta-remove',
    multiple=True,
    help='Remove metadata key (can be used multiple times)'
)
@click.option(
    '--meta-replace',
    type=str,
    help='Replace entire metadata with JSON object'
)
@click.option(
    '--meta-clear',
    is_flag=True,
    help='Clear all metadata'
)
def update(city_id, meta_set, meta_remove, meta_replace, meta_clear):
    """Update city metadata."""
    db = get_database()
    repo = MetadataRepository(db)

    # Validate: can't combine --meta-replace with other operations
    if meta_replace and (meta_set or meta_remove or meta_clear):
        raise click.UsageError(
            "--meta-replace cannot be combined with other metadata options"
        )

    # Validate: can't combine --meta-clear with other operations
    if meta_clear and (meta_set or meta_remove or meta_replace):
        raise click.UsageError(
            "--meta-clear cannot be combined with other metadata options"
        )

    try:
        # Operation: Clear
        if meta_clear:
            repo.clear_metadata('cities', city_id)
            click.echo(f"Cleared metadata for city {city_id}")
            return

        # Operation: Replace
        if meta_replace:
            new_metadata = json.loads(meta_replace)
            result = repo.replace_metadata('cities', city_id, new_metadata)
            click.echo(f"Replaced metadata for city {city_id}: {result}")
            return

        # Operation: Merge and/or Remove
        if meta_set:
            updates = dict(meta_set)
            result = repo.merge_metadata('cities', city_id, updates)
            click.echo(f"Merged metadata for city {city_id}")

        if meta_remove:
            result = repo.remove_metadata_keys('cities', city_id, list(meta_remove))
            click.echo(f"Removed keys from city {city_id}: {list(meta_remove)}")

        # Show final state
        final_metadata = repo.get_metadata('cities', city_id)
        click.echo(f"Current metadata: {json.dumps(final_metadata, indent=2)}")

    except json.JSONDecodeError as e:
        raise click.BadParameter(f"Invalid JSON in --meta-replace: {e}")
    except Exception as e:
        raise click.ClickException(f"Failed to update metadata: {e}")
```

#### Usage examples

```bash
# Add worldbuilding notes
timeline city update 12 \
  --meta-set worldanvil_id:WA-12345 \
  --meta-set story_arc:"The Pollinator Quest"

# Flag for review
timeline city update 12 --meta-set needs_review:true

# Remove flag after review
timeline city update 12 --meta-remove needs_review

# Update multiple values at once
timeline city update 12 \
  --meta-set importance:high \
  --meta-set climate_notes:"Unusual rainfall patterns" \
  --meta-set population_trend:declining

# Replace everything (useful for imports)
timeline city update 12 --meta-replace '{
  "source": "migration_from_legacy_system",
  "verified": false,
  "import_date": "2024-12-30"
}'

# Start fresh
timeline city update 12 --meta-clear
```

### Consistency Across Entity Types

#### All entities with metadata support the same operations

```bash
# Cities
timeline city update <id> --meta-set key:value

# Regions
timeline region update <id> --meta-set key:value

# Events
timeline event update <id> --meta-set key:value

# Snapshots (if applicable)
timeline snapshot update <city_id> <year> --meta-set key:value
```

#### Implementation via base class

```python
# src/timelines/models/base.py
class Entity(DescriptionMixin, MetadataMixin):
    """Base class for all entities."""

    def __init__(self, id: int, description: Optional[str] = None, meta_data: Optional[str] = None):
        self.id = id
        self.description = description
        # Parse JSON string to dict
        self.meta_data = json.loads(meta_data) if meta_data else None

# All entity classes inherit:
class City(Entity):
    pass

class Region(Entity):
    pass

class Event(Entity):
    pass
```

---

## Character Encoding and Unicode Support

### Minimum Required Support

#### Description and metadata fields must support

- **All Western diacritics:** é, ñ, ü, à, ø, ç, etc. (Latin Extended-A,
  Extended-B)
- **Common symbols:** €, £, ¥, °, ±, ×, ÷, •, †, ‡
- **Punctuation:** ", ", ', ', —, –, …
- **Basic emoji:** ✓, ✗, ★, ☆, ♠, ♣, ♥, ♦ (useful for flags/markers)

#### Database configuration

```sql
-- SQLite uses UTF-8 by default, but ensure it's explicit
PRAGMA encoding = "UTF-8";
```

#### Python handling

```python
# Python 3 strings are Unicode by default
description = "Beshquahoek: A city of hot springs and 'fatúnik' pilgrims…"
meta_data = {"climate_note": "Unusually dry — rainfall < 500mm/year"}
```

#### Testing coverage

```python
def test_unicode_in_description():
    """Verify Unicode support in descriptions."""
    city = City(id=1)
    text = "Café Español — población: 50,000 personas"
    city.update_description(text)
    assert city.description == text

def test_unicode_in_metadata():
    """Verify Unicode support in metadata."""
    city = City(id=1)
    city.merge_metadata({"note": "Température: 25°C"})
    assert city.meta_data["note"] == "Température: 25°C"
```

### Internationalization (i18n) - Deferred

Full internationalization support (CJK characters, RTL languages,
locale-specific sorting) is deferred to a future ADR. Current scope is limited
to:

- Western European languages (English, Spanish, French, German, Italian,
  Portuguese)
- Common mathematical/scientific symbols
- Basic decorative symbols and emoji

If broader Unicode plane support is needed (e.g., for story content in other
languages), that decision should be documented separately with consideration
for:

- Database collation settings
- Text normalization (NFC vs NFD)
- Bidirectional text handling
- Full-text search implications

---

## Validation and Deferred Concerns

### What This ADR Covers

#### ✅ Covered

- Update/clear operations for description and metadata
- Flat key-value structure enforcement for metadata
- CLI interface and service layer API
- Unicode support for Western diacritics and common symbols

### What This ADR Defers

#### ⏸️ Deferred to future ADRs

- **Strong typing for metadata values** (e.g., enforcing "importance" must be
  "low"|"medium"|"high")
- **JSON Schema validation** (formal schema for metadata structure)
- **JSON predicates/queries** (e.g., indexing metadata for fast queries)
- **Full internationalization** (CJK, RTL, locale-specific handling)
- **Metadata versioning** (tracking changes to metadata over time)
- **Metadata inheritance** (e.g., regions passing default metadata to cities)

These topics require deeper analysis and may conflict with the "lightweight,
flexible" philosophy of metadata. They should be addressed when concrete
requirements emerge.

---

## Consequences

### Positive

- **Simple text updates:** Description fields easy to update via CLI or API

  ```bash
  timeline city update 1 --description "New summary text"
  ```

- **Narrative flexibility:** Store AI-generated drafts in description, curate
  later

  ```python
  city.update_description(ai_generated_text)
  # Review and edit
  city.update_description(curated_text)
  ```

- **Metadata flexibility without schema changes:** Add new attributes without
  ALTER TABLE

  ```python
  # Experiment with new attribute
  city.merge_metadata({"experimental_rating": 8.5})

  # If useful, later formalize:
  # ALTER TABLE cities ADD COLUMN rating REAL;
  ```

- **Structure enforcement:** Validation prevents complex nested JSON

  ```python
  # This will raise ValueError
  city.merge_metadata({"config": {"nested": "not allowed"}})
  ```

- **User annotations:** Support WorldAnvil IDs, story arc tags, review flags

  ```python
  city.merge_metadata({
      "worldanvil_id": "WA-12345",
      "story_arc": "The Pollinator Quest",
      "needs_review": "false"
  })
  ```

- **Atomic operations:** SQLite JSON functions ensure consistency

  ```sql
  -- This is atomic - no race conditions
  UPDATE cities SET meta_data = json_patch(meta_data, '{"count": 5}');
  ```

- **Backward compatibility:** Existing NULL/empty fields handled gracefully

  ```python
  # Works even if description/meta_data is NULL
  city.update_description("New text")
  city.merge_metadata({"new_key": "value"})
  ```

- **Consistent interface:** Same CLI/API across all entity types

  ```bash
  # Same pattern everywhere
  timeline city update 1 --description "..." --meta-set key:val
  timeline region update 2 --description "..." --meta-set key:val
  timeline event update 3 --description "..." --meta-set key:val
  ```

- **Unicode support:** Western diacritics and common symbols work correctly

  ```python
  city.update_description("Café España — población: 50,000")
  city.merge_metadata({"temp": "25°C"})
  ```

### Negative

- **Not queryable efficiently:** JSON columns aren't indexed
  - **Mitigation:** Use formal columns for attributes you need to query/filter
  - **Rule of thumb:** If you query it often, it should be a column, not
    metadata

- **Type safety limited:** JSON values are untyped strings

  ```python
  # Both valid, but different types
  city.meta_data = {"count": 5}       # integer
  city.meta_data = {"count": "5"}     # string
  ```

  - **Mitigation:** Validate in application layer if needed
  - **Mitigation:** Consider JSON Schema validation for critical metadata

- **Schema evolution hidden:** Changes to metadata structure aren't tracked in
  migrations
  - **Mitigation:** Document metadata conventions in wiki/docs
  - **Mitigation:** Use consistent key naming (e.g., `worldanvil_id` not
    `wa_id` or `worldAnvilId`)

- **Merge behavior can be surprising:** Nested objects are replaced, not
  recursively merged

  ```python
  existing = {"config": {"a": 1, "b": 2}}
  merge_with = {"config": {"c": 3}}
  result = {"config": {"c": 3}}  # "a" and "b" are gone!
  ```

  - **Mitigation:** Document merge semantics clearly
  - **Mitigation:** Avoid deeply nested metadata structures

### Neutral

- **Storage overhead:** JSON is less space-efficient than columns
  - Typical metadata: 100-500 bytes per record
  - Not significant for 1000s of records
  - Concern only at 100k+ scale

- **JSON validation:** SQLite validates JSON syntax, but not structure
  - Can add CHECK constraints if needed:

  ```sql
  CHECK (
    meta_data IS NULL
    OR (
      json_valid(meta_data)
      AND json_type(meta_data) = 'object'
    )
  )
  ```

## Validation and Testing

### Unit tests for description operations

```python
# tests/test_description.py
import pytest
from timelines.models.city import City

def test_update_description():
    """Update description text."""
    city = City(id=1, description=None)
    result = city.update_description("New description")
    assert result == "New description"
    assert city.description == "New description"

def test_update_description_replaces():
    """Update replaces existing description."""
    city = City(id=1, description="Old description")
    result = city.update_description("New description")
    assert result == "New description"

def test_clear_description():
    """Clear removes description."""
    city = City(id=1, description="Some text")
    city.clear_description()
    assert city.description is None

def test_unicode_in_description():
    """Verify Unicode support."""
    city = City(id=1)
    text = "Café Español — población: 50,000 personas"
    city.update_description(text)
    assert city.description == text
```

### Unit tests for metadata operations

```python
# tests/test_metadata.py
import pytest
from timelines.models.city import City

def test_merge_metadata_with_empty():
    """Merge into empty metadata."""
    city = City(id=1, meta_data=None)
    result = city.merge_metadata({"key": "value"})
    assert result == {"key": "value"}

def test_merge_metadata_preserves_existing():
    """Merge preserves existing keys."""
    city = City(id=1, meta_data='{"existing": "value"}')
    result = city.merge_metadata({"new": "value"})
    assert result == {"existing": "value", "new": "value"}

def test_merge_metadata_overwrites_keys():
    """Merge overwrites existing keys with same name."""
    city = City(id=1, meta_data='{"key": "old"}')
    result = city.merge_metadata({"key": "new"})
    assert result == {"key": "new"}

def test_remove_metadata_keys():
    """Remove specific keys."""
    city = City(id=1, meta_data='{"a": 1, "b": 2, "c": 3}')
    result = city.remove_metadata_keys(["b", "c"])
    assert result == {"a": 1}

def test_remove_nonexistent_key():
    """Removing nonexistent key is safe."""
    city = City(id=1, meta_data='{"a": 1}')
    result = city.remove_metadata_keys(["nonexistent"])
    assert result == {"a": 1}

def test_clear_metadata():
    """Clear removes all metadata."""
    city = City(id=1, meta_data='{"a": 1, "b": 2}')
    city.clear_metadata()
    assert city.meta_data is None

def test_replace_metadata():
    """Replace completely replaces metadata."""
    city = City(id=1, meta_data='{"old": "data"}')
    result = city.update_metadata({"new": "data"}, mode='replace')
    assert result == {"new": "data"}

def test_unicode_in_metadata():
    """Verify Unicode support in metadata."""
    city = City(id=1)
    city.merge_metadata({"note": "Température: 25°C", "currency": "€50"})
    assert city.meta_data["note"] == "Température: 25°C"
    assert city.meta_data["currency"] == "€50"
```

### Validation tests for flat structure enforcement

```python
# tests/test_metadata_validation.py
import pytest
from timelines.models.city import City

def test_flat_structure_allowed():
    """Flat key-value pairs are valid."""
    city = City(id=1)
    # These should all work
    city.merge_metadata({
        "string_val": "text",
        "int_val": 42,
        "float_val": 3.14,
        "bool_val": True,
        "null_val": None
    })
    assert len(city.meta_data) == 5

def test_nested_object_rejected():
    """Nested objects raise ValueError."""
    city = City(id=1)
    with pytest.raises(ValueError, match="Nested objects not allowed"):
        city.merge_metadata({
            "config": {
                "setting1": "value1",
                "setting2": "value2"
            }
        })

def test_array_rejected():
    """Arrays/lists raise ValueError."""
    city = City(id=1)
    with pytest.raises(ValueError, match="Arrays not allowed"):
        city.merge_metadata({
            "tags": ["important", "review", "arc3"]
        })

def test_tuple_rejected():
    """Tuples raise ValueError."""
    city = City(id=1)
    with pytest.raises(ValueError, match="Arrays not allowed"):
        city.merge_metadata({
            "coords": (10.5, 20.3)
        })

def test_invalid_type_rejected():
    """Invalid types (e.g., custom objects) raise ValueError."""
    city = City(id=1)

    class CustomObject:
        pass

    with pytest.raises(ValueError, match="Invalid value type"):
        city.merge_metadata({
            "custom": CustomObject()
        })

def test_replace_mode_also_validates():
    """Replace mode enforces validation."""
    city = City(id=1, meta_data='{"old": "data"}')

    with pytest.raises(ValueError, match="Nested objects not allowed"):
        city.update_metadata(
            {"new": {"nested": "not allowed"}},
            mode='replace'
        )
```

### Integration tests with database

```python
# tests/integration/test_metadata_persistence.py
def test_merge_metadata_in_database(db):
    """Test merge persists correctly."""
    repo = MetadataRepository(db)

    # Create city with initial metadata
    db.execute("INSERT INTO cities (id, name, meta_data) VALUES (1, 'Test', '{\"a\": 1}')")

    # Merge new data
    result = repo.merge_metadata('cities', 1, {"b": 2})
    assert result == {"a": 1, "b": 2}

    # Verify persistence
    cursor = db.execute("SELECT meta_data FROM cities WHERE id = 1")
    stored = json.loads(cursor.fetchone()[0])
    assert stored == {"a": 1, "b": 2}

def test_update_description_in_database(db):
    """Test description update persists correctly."""
    db.execute("INSERT INTO cities (id, name, description) VALUES (1, 'Test', 'Old')")

    # Update description
    db.execute("UPDATE cities SET description = ? WHERE id = ?", ("New description", 1))
    db.commit()

    # Verify persistence
    cursor = db.execute("SELECT description FROM cities WHERE id = 1")
    stored = cursor.fetchone()[0]
    assert stored == "New description"
```

## Migration Path

### For existing databases without metadata update capability

1. **Add metadata column if missing:**

```sql
-- Safe to run even if column exists
ALTER TABLE cities ADD COLUMN meta_data TEXT
  CHECK (meta_data IS NULL OR json_valid(meta_data));
```

1. **Migrate legacy flag columns to metadata (optional):**

```sql
-- Example: Migrate "needs_review" boolean column to metadata
UPDATE cities
SET meta_data = json_patch(
  COALESCE(meta_data, '{}'),
  json_object('needs_review', CASE WHEN needs_review THEN 'true' ELSE 'false' END)
)
WHERE needs_review IS NOT NULL;

-- Then drop old column
ALTER TABLE cities DROP COLUMN needs_review;
```

1. **Update application code:**
   - Add `MetadataMixin` to entity classes
   - Add CLI commands for metadata operations
   - Update documentation

## Best Practices

### When to use description vs. metadata vs. formal columns

| Use Description When... | Use Metadata When... | Use Formal Column When... |
|------------------------|---------------------|-------------------------|
| Human-readable summary needed | Attribute is optional/sparse | Attribute is required |
| Narrative context important | Value structure is simple (scalar) | Value structure is consistent |
| AI-generated drafts | Rarely queried/filtered | Frequently queried/filtered |
| Working notes/comments | Experimental/temporary | Permanent part of domain model |
| Longer text (paragraphs) | Short values (flags, IDs) | System-defined attributes |

### Description field conventions

- **Keep concise:** 1-3 paragraphs maximum (use separate documents for longer
  content)
- **Use for summaries:** Overview, not exhaustive detail
- **Temporary drafts OK:** Store AI-generated text, refine later
- **Include Unicode freely:** Use proper diacritics, symbols (e.g., "Café
  España — población: 50°C")

### Metadata structure rules

#### ALWAYS flat key-value pairs

```python
# ✅ CORRECT - Flat structure
{
    "worldanvil_id": "WA-12345",
    "story_arc": "The Pollinator Quest",
    "importance": "high",
    "climate_rainfall_mm": 450,
    "climate_temp_avg_c": 18.5
}

# ❌ WRONG - Nested object
{
    "climate": {
        "rainfall_mm": 450,
        "temp_avg_c": 18.5
    }
}

# ❌ WRONG - Array
{
    "story_arcs": ["Arc1", "Arc2", "Arc3"]
}
```

#### Use descriptive key names to avoid nesting

- Instead of `climate.rainfall` → use `climate_rainfall_mm`
- Instead of `config.setting1` → use `config_setting1`
- Instead of `tags` array → use boolean flags: `tag_important`, `tag_review`

#### Metadata naming conventions

- Use snake_case: `story_arc` not `storyArc`
- Prefix external IDs: `worldanvil_id`, `github_issue`
- Include units in key name: `rainfall_mm`, `temp_c` (not just `rainfall`,
  `temp`)
- Use boolean strings consistently: `"true"`/`"false"` (lowercase strings, not
  JSON booleans)
- Namespace related keys: `climate_rainfall_mm`, `climate_temp_c` (not just
  `rainfall`, `temperature`)

#### Value type guidance

```python
# Allowed value types
"string_value": "text"           # str
"int_value": 42                  # int
"float_value": 3.14              # float
"bool_value": True               # bool (will be serialized to JSON true/false)
"null_value": None               # None (will be serialized to JSON null)

# For booleans in strings (recommended for consistency):
"flag": "true"   # or "false" - always lowercase strings
```

### Documentation

#### Maintain a metadata registry in docs

```markdown
# Metadata Keys Registry

## Cities
- `worldanvil_id` (string): WorldAnvil article ID
- `story_arc` (string): Primary story arc featuring this city
- `needs_review` (bool string): Flagged for content review ("true"/"false")
- `importance` (string): "low" | "medium" | "high"
- `climate_rainfall_mm` (int): Annual rainfall in millimeters
- `climate_temp_avg_c` (float): Average annual temperature in Celsius
- `population_trend` (string): "growing" | "stable" | "declining"

## Events
- `source` (string): Where this event came from (e.g., "migration_script", "manual")
- `verified` (bool string): Has this been reviewed by author? ("true"/"false")
- `narrative_draft` (string): AI-generated description (pending curation)
- `confidence` (string): "low" | "medium" | "high"

## Regions
- `climate_zone` (string): "temperate" | "arid" | "tropical" | "cold"
- `terrain_primary` (string): "plains" | "forest" | "mountains" | "coast"
- `exploration_status` (string): "fully_detailed" | "in_progress" | "placeholder"
```

## Alternatives Considered

### EAV (Entity-Attribute-Value) tables

```sql
CREATE TABLE entity_metadata (
    entity_type TEXT,
    entity_id INTEGER,
    key TEXT,
    value TEXT,
    PRIMARY KEY (entity_type, entity_id, key)
);
```

- Pro: More "relational", easier to query all values for a key
- Con: More complex joins, harder to get "all metadata for entity"
- Con: Still not typed, same limitations as JSON
- **Rejected:** JSON simpler for sparse, unstructured data

### Separate metadata tables per entity

```sql
CREATE TABLE city_metadata (city_id, key, value, PRIMARY KEY (city_id, key));
CREATE TABLE region_metadata (region_id, key, value, PRIMARY KEY (region_id, key));
```

- Pro: Slightly more normalized
- Con: Proliferation of tables, inconsistent interface
- **Rejected:** One JSON column per entity is simpler

### PostgreSQL JSONB with indexing

- Pro: Can index JSON fields, GIN indexes for queries
- Con: Requires PostgreSQL (we're using SQLite per ADR-001)
- **Deferred:** If we migrate to PostgreSQL later, can add JSON indexing

### No metadata at all, force schema changes

- Pro: Everything is typed and queryable
- Con: Too rigid for exploratory worldbuilding
- Con: Requires migration for every new attribute
- **Rejected:** Defeats purpose of flexible annotations

## References

- SQLite JSON Functions:
  <https://www.sqlite.org/json1.html>
- JSON in SQLite (best practices):
  <https://til.simonwillison.net/sqlite/json-techniques>
- When to use JSON columns:
  <https://www.cybertec-postgresql.com/en/json-postgresql-how-to-use-it-right/>
