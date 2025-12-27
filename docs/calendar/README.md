# Saskan Calendar - User Documentation

The Saskan Calendar system provides astronomical and calendrical calculations for the fictional world of Saskantinon, used in worldbuilding and RPG contexts.

## Overview

The Saskan Calendar simulates the orbital mechanics of the planet Gavor around the star Fatune, including:
- Multiple calendar systems (Rosetta/Astro, Fatunik, Lunar A, Lunar B)
- Eight moon phases and cycles
- Wanderer (planet) positions and visibility
- Star constellations and seasonal sky context
- Time conversion between various calendar systems

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

This will install the `saskan-calendar` package and make the `app_calendar` module available for import.

## Python API Usage

The primary interface is through Python imports. All core functions are available from the `app_calendar` module:

```python
from app_calendar import (
    universal_date_translator,
    get_moon_phases,
    get_wanderers,
    get_star_context,
    AstroCalendar,
    FatunikCalendar,
    StrictLunarCalendar,
    LunarSolarCalendar
)
```

### Universal Date Translator

The main entry point for converting between calendar systems:

```python
from app_calendar import universal_date_translator

# Get comprehensive date information for astro day 1000
date_info = universal_date_translator(day=1000, time=12.0)

# Returns a dictionary with:
# - Rosetta (Canonical) calendar information
# - Turn (year) and day within turn
# - Season information
```

**Parameters:**
- `day` (int): The day number in the Rosetta/Astro calendar (cannot be less than 0)
- `time` (float, optional): Hour of day in 24-hour format (0-24), defaults to 12.0

**Returns:** Dictionary containing date information across multiple calendar systems

### Calendar Classes

#### AstroCalendar (Rosetta Calendar)

The astronomical reference calendar, counting days from the astro epoch:

```python
from app_calendar import AstroCalendar

astro = AstroCalendar(astro_day=1000)

# Get comprehensive date information
date = astro.get_astro_date()
# Returns: {"astro_day": 1000, "Astro": {"turn": ..., "turn_day": ..., "season": {...}, "events": [...]}}

# Get turn and day information
turn_info = astro.get_turn_day()
# Returns: {"ros_turn": <year>, "ros_day_cnt": <day in year>}

# Get season information
season = astro.get_solar_season()
# Returns: {"solar_season": <season name>, "solar_event": <event if any>}
```

#### FatunikCalendar

A strictly solar calendar with 13 months, beginning on the summer solstice:

```python
from app_calendar import FatunikCalendar

fat = FatunikCalendar(astro_day=365472)
date = fat.get_date()

# Returns comprehensive date including:
# - fatunik_turn: Year number
# - fatunik_turn_day: Day within the year
# - fatunik_month_number: Month (1-13)
# - fatunik_month_day: Day within month
# - is_leaturn: Boolean for leap year
# - label: Epoch label
# - Plus all Astro calendar information
```

#### StrictLunarCalendar (Lunar A)

A strict lunar calendar that does not account for leap years:

```python
from app_calendar import StrictLunarCalendar

lunar_a = StrictLunarCalendar(astro_day=500000)
# Calendar slides through seasons as it follows lunar cycles
```

#### LunarSolarCalendar (Lunar B)

A lunisolar calendar with leap year adjustments:

```python
from app_calendar import LunarSolarCalendar

lunar_b = LunarSolarCalendar(astro_day=500000)
# Adjusts to keep alignment with solar seasons
```

### Moon Phases

Get phase information for all eight moons:

```python
from app_calendar import get_moon_phases

phases = get_moon_phases(astro_day=1000)

# Returns dictionary with moon names as keys
# Each moon contains phase calculations based on orbital periods
```

### Wanderers (Planets)

Get positions and visibility of wandering celestial bodies:

```python
from app_calendar import get_wanderers

wanderers = get_wanderers(solar_day=1000)

# Returns dictionary with wanderer information:
# - Aesthra, Lethra, Beyarus, Dramond, Thurnak, Zelven, Kreetha
# - Each includes: Phase (0.0-1.0), Visible (boolean)
# - Special events: "The Spark", "A Rare Comet" (when visible)
```

**Visibility Logic:**
- 0.0 or 1.0: Aligned with Fatune (not visible, lost in solar glare)
- 0.5: Opposite side of sky (maximum visibility)
- Visible range: 0.1 < phase < 0.9 (about 80% of orbital cycle)

### Star Context

Get visible constellations and fixed stars for a given day:

```python
from app_calendar import get_star_context

stars = get_star_context(solar_day=150)

# Returns:
# - Constellation: Current house/constellation visible
# - Fixed Stars: List of visible stars with descriptions
```

Returns different constellations based on season (Greening, Blazing, Withering, Stillness).

### Time Conversion

Convert galactic pulse counts to Saskan time format:

```python
from app_calendar import get_saskan_time_from_pulse

time_info = get_saskan_time_from_pulse(pulse_count=43200)

# Returns:
# - spoken_time: "5-bell-1 of the 2nd Watch"
# - written_time: "2/5:1"
# - earth_time: "12:00:00"
```

**Saskan Time Structure:**
- 6 Watches per day (4 hours each)
- 8 Bells per Watch (30 minutes each)
- 6 Wayts per Bell (5 minutes each)

### Helper Functions

```python
from app_calendar import (
    ordinal,
    get_astro_day_from_pulse,
    get_solar_day_from_pulse,
    get_astro_turn,
    get_solar_season,
    count_visible_wanderers
)

# Convert number to ordinal string
ordinal(3)  # Returns: "3rd"

# Convert pulse count to astro day
get_astro_day_from_pulse(pulse=86400)  # Returns astro day

# Get turn (year) from astro day
get_astro_turn(astro_day=1000)  # Returns turn number

# Count visible wanderers
wanderers = get_wanderers(1000)
count_visible_wanderers(wanderers)  # Returns: {"visible_wanderers": <count>}
```

## Constants

Key astronomical constants are defined in the module:

```python
from app_calendar.core import (
    DAYS_PER_SOLAR_TURN,      # 365.2422
    PULSES_PER_SOLAR_DAY,     # 86400
    ASTRO_EPOCH_PULSE,        # 0
    ASTRO_EPOCH_DAY,          # 1
    FATUNIK_EPOCH_DAY,        # 365472
    LUNAR_A_EPOCH_DAY,        # 182717
    LUNAR_B_EPOCH_DAY         # 182717
)
```

## Calendar Systems

### Rosetta (Astronomical) Calendar
- Reference calendar for all conversions
- Counts days continuously from epoch start (no year wrapping)
- Used for astronomical calculations
- Epoch begins ~6000 turns before game start

### Fatunik Calendar
- Solar calendar with 13 months
- Year begins on summer solstice
- First month: 5 days (6 in leap years)
- Remaining 12 months: 30 days each
- Leap year every 4 years (with 100/400 year exceptions)
- Epoch begins at day 365472 (Astro)

### Terpin Calendar
- Solar calendar (simplified)
- Year begins near spring equinox
- Less complex leap year rules than Fatunik
- (Implementation in progress)

### Lunar Calendars
- **Lunar A (Strict)**: Based on average lunar cycle, slides through seasons
- **Lunar B (Lunisolar)**: Adjusts for solar alignment with leap corrections
- **Lunar C**: Based on longest lunar cycle (planned)
- Epoch begins at day 182717 (Astro)

## Seasons

Four seasons based on northern hemisphere perspective:

- **Stillness** (Winter): Days 0-90
- **Greening** (Spring): Days 91-181
- **Blazing** (Summer): Days 182-272
- **Withering** (Fall): Days 273-365

Each season has associated:
- Equinox/solstice events
- Mid-season events
- Visible star constellations
- Fixed stars

## Examples

### Basic Date Conversion

```python
from app_calendar import universal_date_translator

# Get date info for astro day 500,000
info = universal_date_translator(500000)
print(f"Turn: {info['Rosetta']['Turn']}")
print(f"Day in Turn: {info['Rosetta']['Day in Turn']}")
print(f"Season: {info['Rosetta']['Season']['solar_season']}")
```

### Find Moon Phases for Specific Date

```python
from app_calendar import get_moon_phases

phases = get_moon_phases(1000)
for moon_name, moon_data in phases.items():
    print(f"{moon_name}: {moon_data}")
```

### Check Wanderer Visibility

```python
from app_calendar import get_wanderers

wanderers = get_wanderers(1000)
visible = [name for name, data in wanderers.items() if data.get('Visible')]
print(f"Visible tonight: {', '.join(visible)}")
```

### Get Complete Calendar Information

```python
from app_calendar import AstroCalendar, FatunikCalendar

day = 400000

# Rosetta calendar
astro = AstroCalendar(day)
astro_info = astro.get_astro_date()

# Fatunik calendar
if day >= 365472:  # Check if past Fatunik epoch
    fat = FatunikCalendar(day)
    fat_info = fat.get_date()
    print(f"Fatunik Year: {fat_info['fatunik_turn']}")
    print(f"Fatunik Month: {fat_info['fatunik_month_number']}")
```

## Development and Testing

The module is designed as a library for Python applications. Currently there is no command-line interface.

### Running Tests

```bash
poetry run pytest tests/calendar/
```

Note: The current test suite is outdated and needs to be regenerated to match the current API.

### Import in Your Project

After installing with Poetry:

```python
from app_calendar import (
    universal_date_translator,
    AstroCalendar,
    FatunikCalendar,
    get_moon_phases,
    get_wanderers,
    get_star_context
)
```

## Future Development

Planned features include:
- Command-line interface for quick date conversions
- Database of significant historical dates
- Complete Terpin calendar implementation
- Lunar C calendar
- Enhanced moon phase details (size, distance, appearance)
- Integration with other Saskan simulation systems

## Technical Notes

### Time Systems
- **Astro Day/Pulse**: Continuous count from epoch start
- **Solar Day/Pulse**: Cyclic count within current solar year
- **Pulse**: Equivalent to one second (86,400 per day)

### Coordinate Systems
- Wanderer phase: 0.0 = conjunction, 0.5 = opposition, 1.0 = conjunction again
- All angles and positions normalized to 0.0-1.0 range

### Data Storage
- Calendar calculations are deterministic (no external database required)
- Special events (Spark, Comet) use seeded randomness for consistency

## Support and Contributions

This is a specialized worldbuilding tool for the Saskantinon RPG setting. For questions or contributions, please refer to the project repository.
