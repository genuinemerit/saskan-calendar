"""
app_timeline.cli_list

CLI commands for listing and querying timeline data.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .services import (
    EntityService,
    EpochService,
    EventService,
    ProvinceService,
    RegionService,
    RouteService,
    SettlementService,
    SnapshotService,
)

list_app = typer.Typer(help="List and query timeline data")
console = Console()


@list_app.command("epochs")
def list_epochs(
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive records"
    ),
):
    """List all epochs (named time periods)."""
    try:
        with EpochService() as service:
            epochs = service.list_all(active_only=not all_records, order_by="start_astro_day")

        if not epochs:
            rprint("[yellow]No epochs found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nEpochs ({len(epochs)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Start Day", justify="right")
        table.add_column("End Day", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Description")

        for epoch in epochs:
            table.add_row(
                str(epoch.id),
                epoch.name,
                str(epoch.start_astro_day),
                str(epoch.end_astro_day),
                str(epoch.duration),
                epoch.description or "",
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("regions")
def list_regions(
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive records"
    ),
):
    """List all regions (top-level geographic areas)."""
    try:
        with RegionService() as service:
            regions = service.list_all(active_only=not all_records, order_by="name")

        if not regions:
            rprint("[yellow]No regions found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nRegions ({len(regions)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")

        for region in regions:
            table.add_row(str(region.id), region.name)

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("provinces")
def list_provinces(
    region_id: Optional[int] = typer.Option(None, "--region", "-r", help="Filter by region ID"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive records"
    ),
):
    """List all provinces (administrative divisions)."""
    try:
        with ProvinceService() as service:
            if region_id is not None:
                provinces = service.get_provinces_by_region(region_id, active_only=not all_records)
            else:
                provinces = service.list_all(active_only=not all_records, order_by="name")

        if not provinces:
            rprint("[yellow]No provinces found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nProvinces ({len(provinces)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Region ID", justify="right")

        for province in provinces:
            table.add_row(
                str(province.id),
                province.name,
                str(province.region_id) if province.region_id else "",
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("settlements")
def list_settlements(
    province_id: Optional[int] = typer.Option(None, "--province", "-p", help="Filter by province ID"),
    settlement_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type (city/town/village)"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive records"
    ),
):
    """List all settlements (cities, towns, villages)."""
    try:
        with SettlementService() as service:
            if province_id is not None:
                settlements = service.get_settlements_by_province(province_id, active_only=not all_records)
            elif settlement_type is not None:
                settlements = service.get_settlements_by_type(settlement_type, active_only=not all_records)
            else:
                settlements = service.list_all(active_only=not all_records, order_by="name")

        if not settlements:
            rprint("[yellow]No settlements found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nSettlements ({len(settlements)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Type")
        table.add_column("Province ID", justify="right")
        table.add_column("Grid Location")

        for settlement in settlements:
            grid_loc = ""
            if settlement.grid_x and settlement.grid_y:
                grid_loc = f"({settlement.grid_x}, {settlement.grid_y})"

            table.add_row(
                str(settlement.id),
                settlement.name,
                settlement.settlement_type,
                str(settlement.province_id) if settlement.province_id else "",
                grid_loc,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("entities")
def list_entities(
    entity_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type (person/organization/faction)"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="Filter entities alive at this day"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive records"
    ),
):
    """List all entities (people, organizations, factions)."""
    try:
        with EntityService() as service:
            if day is not None:
                entities = service.get_entities_alive_at_day(day)
            elif entity_type is not None:
                entities = service.get_entities_by_type(entity_type, active_only=not all_records)
            else:
                entities = service.list_all(active_only=not all_records, order_by="name")

        if not entities:
            rprint("[yellow]No entities found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nEntities ({len(entities)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Type")
        table.add_column("Founded", justify="right")
        table.add_column("Dissolved", justify="right")

        for entity in entities:
            founded = str(entity.founded_astro_day) if entity.founded_astro_day is not None else ""
            dissolved = str(entity.dissolved_astro_day) if entity.dissolved_astro_day is not None else ""

            table.add_row(
                str(entity.id),
                entity.name,
                entity.entity_type,
                founded,
                dissolved,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("events")
def list_events(
    event_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by event type"),
    settlement_id: Optional[int] = typer.Option(None, "--settlement", "-s", help="Filter by settlement ID"),
    entity_id: Optional[int] = typer.Option(None, "--entity", "-e", help="Filter by entity ID"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="Filter events on this day"),
    start_day: Optional[int] = typer.Option(None, "--start", help="Filter events from this day"),
    end_day: Optional[int] = typer.Option(None, "--end", help="Filter events until this day"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include deprecated events"
    ),
):
    """List all historical events."""
    try:
        with EventService() as service:
            if day is not None:
                events = service.get_events_at_day(day, active_only=not all_records)
            elif start_day is not None and end_day is not None:
                events = service.get_events_in_range(start_day, end_day, active_only=not all_records)
            elif settlement_id is not None:
                events = service.get_events_for_settlement(settlement_id, active_only=not all_records)
            elif entity_id is not None:
                events = service.get_events_for_entity(entity_id, active_only=not all_records)
            elif event_type is not None:
                events = service.get_events_by_type(event_type, active_only=not all_records)
            else:
                # Get all events ordered by day
                from sqlalchemy import select
                from app_timeline.models.event import Event

                stmt = select(Event).order_by(Event.astro_day, Event.title)
                if not all_records:
                    stmt = stmt.where(Event.is_deprecated == False)
                result = service.session.execute(stmt)
                events = list(result.scalars().all())

        if not events:
            rprint("[yellow]No events found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nEvents ({len(events)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Day", justify="right")
        table.add_column("Type")
        table.add_column("Title", style="green")
        table.add_column("Settlement", justify="right")
        table.add_column("Entity", justify="right")

        for event in events:
            table.add_row(
                str(event.id),
                str(event.astro_day),
                event.event_type,
                event.title,
                str(event.settlement_id) if event.settlement_id else "",
                str(event.entity_id) if event.entity_id else "",
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("routes")
def list_routes(
    settlement_id: Optional[int] = typer.Option(None, "--settlement", "-s", help="Filter by settlement ID (origin or destination)"),
    route_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by route type"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive routes"
    ),
):
    """List all routes connecting settlements."""
    try:
        with RouteService() as service:
            if settlement_id is not None:
                routes = service.get_routes_for_settlement(settlement_id, active_only=not all_records)
            elif route_type is not None:
                routes = service.get_routes_by_type(route_type, active_only=not all_records)
            else:
                routes = service.list_all(active_only=not all_records)

        if not routes:
            rprint("[yellow]No routes found.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nRoutes ({len(routes)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Origin", justify="right")
        table.add_column("Destination", justify="right")
        table.add_column("Distance (km)", justify="right")
        table.add_column("Type")
        table.add_column("Difficulty")

        for route in routes:
            distance = f"{route.distance_km:.1f}" if route.distance_km else ""

            table.add_row(
                str(route.id),
                str(route.origin_settlement_id),
                str(route.destination_settlement_id),
                distance,
                route.route_type or "",
                route.difficulty or "",
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@list_app.command("snapshots")
def list_snapshots(
    settlement_id: int = typer.Option(..., "--settlement", "-s", help="Settlement ID (required)"),
    start_day: Optional[int] = typer.Option(None, "--start", help="Filter snapshots from this day"),
    end_day: Optional[int] = typer.Option(None, "--end", help="Filter snapshots until this day"),
    all_records: bool = typer.Option(
        False, "--all", "-a", help="Include inactive snapshots"
    ),
):
    """List population snapshots for a settlement."""
    try:
        with SnapshotService() as service:
            if start_day is not None and end_day is not None:
                snapshots = service.get_snapshots_in_range(settlement_id, start_day, end_day, active_only=not all_records)
            else:
                snapshots = service.get_snapshots_for_settlement(settlement_id, active_only=not all_records)

        if not snapshots:
            rprint(f"[yellow]No snapshots found for settlement {settlement_id}.[/yellow]")
            return

        # Create table
        table = Table(title=f"\nSnapshots for Settlement {settlement_id} ({len(snapshots)} found)", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Day", justify="right")
        table.add_column("Population", justify="right", style="green")

        for snapshot in snapshots:
            table.add_row(
                str(snapshot.id),
                str(snapshot.astro_day),
                f"{snapshot.population_total:,}",
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
