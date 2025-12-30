"""
app_timeline.cli_data

CLI commands for adding and managing timeline data.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from .services import (
    EntityService,
    EpochService,
    EventService,
    ProvinceService,
    ProvinceSnapshotService,
    RegionService,
    RegionSnapshotService,
    RouteService,
    SettlementService,
    SnapshotService,
)

data_app = typer.Typer(help="Add and manage timeline data")
console = Console()


def prompt_metadata(prompt_message: str = "Add metadata?") -> Optional[dict]:
    """
    Interactive prompt for adding metadata as key-value pairs.

    :param prompt_message: Message to show when asking if user wants to add metadata
    :return: Dictionary of metadata or None
    """
    if not Confirm.ask(prompt_message, default=False):
        return None

    metadata = {}
    rprint("[cyan]Enter metadata (press Enter with empty key to finish):[/cyan]")

    while True:
        key = Prompt.ask("  Key", default="")
        if not key:
            break

        value = Prompt.ask(f"  Value for '{key}'")
        metadata[key] = value

    return metadata if metadata else None


@data_app.command("add-epoch")
def add_epoch(
    name: str = typer.Option(..., "--name", "-n", help="Epoch name (required)"),
    start_day: int = typer.Option(
        ..., "--start", "-s", help="Start astro_day (required)"
    ),
    end_day: int = typer.Option(..., "--end", "-e", help="End astro_day (required)"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Epoch description"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new epoch (named time period)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create epoch
        with EpochService() as service:
            epoch = service.create_epoch(
                name=name,
                start_astro_day=start_day,
                end_astro_day=end_day,
                description=description,
                meta_data=meta_data,
            )

        rprint(f"[green]✓ Created epoch '{epoch.name}' (ID: {epoch.id})[/green]")
        rprint(
            f"  Range: Day {epoch.start_astro_day} → {epoch.end_astro_day} ({epoch.duration} days)"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-region")
def add_region(
    name: str = typer.Option(..., "--name", "-n", help="Region name (required)"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new region (top-level geographic area)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create region
        with RegionService() as service:
            region = service.create_region(
                name=name,
                meta_data=meta_data,
            )

        rprint(f"[green]✓ Created region '{region.name}' (ID: {region.id})[/green]")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-province")
def add_province(
    name: str = typer.Option(..., "--name", "-n", help="Province name (required)"),
    region_id: Optional[int] = typer.Option(
        None, "--region", "-r", help="Parent region ID"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new province (administrative division within a region)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create province
        with ProvinceService() as service:
            province = service.create_province(
                name=name,
                region_id=region_id,
                meta_data=meta_data,
            )

        region_info = f" in region {province.region_id}" if province.region_id else ""
        rprint(
            f"[green]✓ Created province '{province.name}' (ID: {province.id}){region_info}[/green]"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-settlement")
def add_settlement(
    name: str = typer.Option(..., "--name", "-n", help="Settlement name (required)"),
    settlement_type: str = typer.Option(
        ..., "--type", "-t", help="Type (city/town/village)"
    ),
    province_id: Optional[int] = typer.Option(
        None, "--province", "-p", help="Parent province ID"
    ),
    grid_x: Optional[int] = typer.Option(
        None, "--grid-x", help="Grid X coordinate (1-40)"
    ),
    grid_y: Optional[int] = typer.Option(
        None, "--grid-y", help="Grid Y coordinate (1-30)"
    ),
    location_x: Optional[float] = typer.Option(
        None, "--location-x", help="Precise X coordinate (km)"
    ),
    location_y: Optional[float] = typer.Option(
        None, "--location-y", help="Precise Y coordinate (km)"
    ),
    area_sq_km: Optional[float] = typer.Option(
        None, "--area", help="Settlement area (sq km)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new settlement (city, town, or village)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create settlement
        with SettlementService() as service:
            settlement = service.create_settlement(
                name=name,
                province_id=province_id,
                settlement_type=settlement_type,
                location_x=location_x,
                location_y=location_y,
                grid_x=grid_x,
                grid_y=grid_y,
                area_sq_km=area_sq_km,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created {settlement.settlement_type} '{settlement.name}' (ID: {settlement.id})[/green]"
        )
        if settlement.grid_x and settlement.grid_y:
            rprint(f"  Location: Grid ({settlement.grid_x}, {settlement.grid_y})")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-snapshot")
def add_snapshot(
    settlement_id: int = typer.Option(
        ..., "--settlement", "-s", help="Settlement ID (required)"
    ),
    astro_day: int = typer.Option(..., "--day", "-d", help="Astro day (required)"),
    population_total: int = typer.Option(
        ..., "--population", "-p", help="Total population (required)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a settlement snapshot (population at a point in time)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create snapshot
        with SnapshotService() as service:
            snapshot = service.create_snapshot(
                settlement_id=settlement_id,
                astro_day=astro_day,
                population_total=population_total,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created snapshot for settlement {snapshot.settlement_id} at day {snapshot.astro_day}[/green]"
        )
        rprint(f"  Population: {snapshot.population_total:,}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-route")
def add_route(
    origin: int = typer.Option(..., "--from", help="Origin settlement ID (required)"),
    destination: int = typer.Option(
        ..., "--to", help="Destination settlement ID (required)"
    ),
    distance_km: Optional[float] = typer.Option(
        None, "--distance", "-d", help="Distance in km"
    ),
    route_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Route type (road/trail/river)"
    ),
    difficulty: Optional[str] = typer.Option(
        None, "--difficulty", help="Route difficulty"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new route connecting two settlements."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create route
        with RouteService() as service:
            route = service.create_route(
                origin_settlement_id=origin,
                destination_settlement_id=destination,
                distance_km=distance_km,
                route_type=route_type,
                difficulty=difficulty,
                meta_data=meta_data,
            )

        rprint(f"[green]✓ Created route (ID: {route.id})[/green]")
        rprint(
            f"  From: Settlement {route.origin_settlement_id} → Settlement {route.destination_settlement_id}"
        )
        if route.distance_km:
            rprint(f"  Distance: {route.distance_km} km")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-entity")
def add_entity(
    name: str = typer.Option(..., "--name", "-n", help="Entity name (required)"),
    entity_type: str = typer.Option(
        ..., "--type", "-t", help="Type (person/organization/faction)"
    ),
    founded_day: Optional[int] = typer.Option(
        None, "--founded", "-f", help="Founded/born astro_day"
    ),
    dissolved_day: Optional[int] = typer.Option(
        None, "--dissolved", "-d", help="Dissolved/died astro_day"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Entity description"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new entity (person, organization, or group)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create entity
        with EntityService() as service:
            entity = service.create_entity(
                name=name,
                entity_type=entity_type,
                founded_astro_day=founded_day,
                dissolved_astro_day=dissolved_day,
                description=description,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created {entity.entity_type} '{entity.name}' (ID: {entity.id})[/green]"
        )
        if entity.founded_astro_day is not None:
            lifespan = f"Day {entity.founded_astro_day}"
            if entity.dissolved_astro_day is not None:
                lifespan += f" → {entity.dissolved_astro_day}"
            rprint(f"  Lifespan: {lifespan}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-event")
def add_event(
    title: str = typer.Option(..., "--title", "-t", help="Event title (required)"),
    event_type: str = typer.Option(
        ..., "--type", help="Event type (battle/founding/treaty/etc)"
    ),
    astro_day: int = typer.Option(
        ..., "--day", "-d", help="Day event occurred (required)"
    ),
    settlement_id: Optional[int] = typer.Option(
        None, "--settlement", "-s", help="Settlement where event occurred"
    ),
    entity_id: Optional[int] = typer.Option(
        None, "--entity", "-e", help="Entity involved in event"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Event description"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a new historical event."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create event
        with EventService() as service:
            event = service.create_event(
                title=title,
                event_type=event_type,
                astro_day=astro_day,
                settlement_id=settlement_id,
                entity_id=entity_id,
                description=description,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created {event.event_type} event '{event.title}' (ID: {event.id})[/green]"
        )
        rprint(f"  Occurred: Day {event.astro_day}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-region-snapshot")
def add_region_snapshot(
    region_id: int = typer.Option(..., "--region", "-r", help="Region ID (required)"),
    astro_day: int = typer.Option(..., "--day", "-d", help="Astro day (required)"),
    population_total: int = typer.Option(
        ..., "--population", "-p", help="Total population (required)"
    ),
    snapshot_type: str = typer.Option(
        "simulation",
        "--type",
        "-t",
        help="Snapshot type (simulation/census/estimate/etc)",
    ),
    granularity: str = typer.Option(
        "year", "--granularity", "-g", help="Granularity (year/decade/century/etc)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a region snapshot (population at a point in time)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create snapshot
        with RegionSnapshotService() as service:
            snapshot = service.create_snapshot(
                region_id=region_id,
                astro_day=astro_day,
                population_total=population_total,
                snapshot_type=snapshot_type,
                granularity=granularity,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created region snapshot for region {snapshot.region_id} at day {snapshot.astro_day}[/green]"
        )
        rprint(f"  Population: {snapshot.population_total:,}")
        rprint(f"  Type: {snapshot.snapshot_type}, Granularity: {snapshot.granularity}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@data_app.command("add-province-snapshot")
def add_province_snapshot(
    province_id: int = typer.Option(
        ..., "--province", "-p", help="Province ID (required)"
    ),
    astro_day: int = typer.Option(..., "--day", "-d", help="Astro day (required)"),
    population_total: int = typer.Option(
        ..., "--population", help="Total population (required)"
    ),
    snapshot_type: str = typer.Option(
        "simulation",
        "--type",
        "-t",
        help="Snapshot type (simulation/census/estimate/etc)",
    ),
    granularity: str = typer.Option(
        "year", "--granularity", "-g", help="Granularity (year/decade/century/etc)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for metadata"
    ),
):
    """Add a province snapshot (population at a point in time)."""
    try:
        # Prompt for metadata if interactive
        meta_data = None
        if interactive:
            meta_data = prompt_metadata()

        # Create snapshot
        with ProvinceSnapshotService() as service:
            snapshot = service.create_snapshot(
                province_id=province_id,
                astro_day=astro_day,
                population_total=population_total,
                snapshot_type=snapshot_type,
                granularity=granularity,
                meta_data=meta_data,
            )

        rprint(
            f"[green]✓ Created province snapshot for province {snapshot.province_id} at day {snapshot.astro_day}[/green]"
        )
        rprint(f"  Population: {snapshot.population_total:,}")
        rprint(f"  Type: {snapshot.snapshot_type}, Granularity: {snapshot.granularity}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)
