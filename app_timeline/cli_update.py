"""
app_timeline.cli_update

CLI commands for updating and deleting timeline data.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich import print as rprint
from rich.prompt import Confirm

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

update_app = typer.Typer(help="Update and delete timeline data")


@update_app.command("epoch")
def update_epoch(
    epoch_id: int = typer.Argument(..., help="ID of epoch to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New epoch name"),
    start_day: Optional[int] = typer.Option(
        None, "--start", "-s", help="New start day"
    ),
    end_day: Optional[int] = typer.Option(None, "--end", "-e", help="New end day"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="New description"
    ),
):
    """Update an existing epoch."""
    try:
        # Build update dictionary with only provided values
        updates = {}
        if name is not None:
            updates["name"] = name
        if start_day is not None:
            updates["start_astro_day"] = start_day
        if end_day is not None:
            updates["end_astro_day"] = end_day
        if description is not None:
            updates["description"] = description

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with EpochService() as service:
            epoch = service.update(epoch_id, **updates)

        if epoch is None:
            rprint(f"[red]✗ Epoch {epoch_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(f"[green]✓ Updated epoch '{epoch.name}' (ID: {epoch.id})[/green]")
        rprint(f"  Range: Day {epoch.start_astro_day} → {epoch.end_astro_day}")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("region")
def update_region(
    region_id: int = typer.Argument(..., help="ID of region to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New region name"),
):
    """Update an existing region."""
    try:
        updates = {}
        if name is not None:
            updates["name"] = name

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with RegionService() as service:
            region = service.update(region_id, **updates)

        if region is None:
            rprint(f"[red]✗ Region {region_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(f"[green]✓ Updated region '{region.name}' (ID: {region.id})[/green]")

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("province")
def update_province(
    province_id: int = typer.Argument(..., help="ID of province to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New province name"),
    region_id: Optional[int] = typer.Option(
        None, "--region", "-r", help="New region ID"
    ),
):
    """Update an existing province."""
    try:
        updates = {}
        if name is not None:
            updates["name"] = name
        if region_id is not None:
            updates["region_id"] = region_id

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with ProvinceService() as service:
            province = service.update(province_id, **updates)

        if province is None:
            rprint(f"[red]✗ Province {province_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(
            f"[green]✓ Updated province '{province.name}' (ID: {province.id})[/green]"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("settlement")
def update_settlement(
    settlement_id: int = typer.Argument(..., help="ID of settlement to update"),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="New settlement name"
    ),
    settlement_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="New settlement type"
    ),
    province_id: Optional[int] = typer.Option(
        None, "--province", "-p", help="New province ID"
    ),
    grid_x: Optional[int] = typer.Option(
        None, "--grid-x", help="New grid X coordinate"
    ),
    grid_y: Optional[int] = typer.Option(
        None, "--grid-y", help="New grid Y coordinate"
    ),
):
    """Update an existing settlement."""
    try:
        updates = {}
        if name is not None:
            updates["name"] = name
        if settlement_type is not None:
            updates["settlement_type"] = settlement_type
        if province_id is not None:
            updates["province_id"] = province_id
        if grid_x is not None:
            updates["grid_x"] = grid_x
        if grid_y is not None:
            updates["grid_y"] = grid_y

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with SettlementService() as service:
            settlement = service.update(settlement_id, **updates)

        if settlement is None:
            rprint(f"[red]✗ Settlement {settlement_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(
            f"[green]✓ Updated {settlement.settlement_type} '{settlement.name}' (ID: {settlement.id})[/green]"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("entity")
def update_entity(
    entity_id: int = typer.Argument(..., help="ID of entity to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New entity name"),
    entity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="New entity type"
    ),
    founded: Optional[int] = typer.Option(
        None, "--founded", "-f", help="New founded day"
    ),
    dissolved: Optional[int] = typer.Option(
        None, "--dissolved", "-d", help="New dissolved day"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="New description"
    ),
):
    """Update an existing entity."""
    try:
        updates = {}
        if name is not None:
            updates["name"] = name
        if entity_type is not None:
            updates["entity_type"] = entity_type
        if founded is not None:
            updates["founded_astro_day"] = founded
        if dissolved is not None:
            updates["dissolved_astro_day"] = dissolved
        if description is not None:
            updates["description"] = description

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with EntityService() as service:
            entity = service.update(entity_id, **updates)

        if entity is None:
            rprint(f"[red]✗ Entity {entity_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(
            f"[green]✓ Updated {entity.entity_type} '{entity.name}' (ID: {entity.id})[/green]"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("event")
def update_event(
    event_id: int = typer.Argument(..., help="ID of event to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New event title"),
    event_type: Optional[str] = typer.Option(None, "--type", help="New event type"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="New event day"),
    description: Optional[str] = typer.Option(
        None, "--description", help="New description"
    ),
    settlement_id: Optional[int] = typer.Option(
        None, "--settlement", "-s", help="New settlement ID"
    ),
    entity_id: Optional[int] = typer.Option(
        None, "--entity", "-e", help="New entity ID"
    ),
):
    """Update an existing event."""
    try:
        updates = {}
        if title is not None:
            updates["title"] = title
        if event_type is not None:
            updates["event_type"] = event_type
        if day is not None:
            updates["astro_day"] = day
        if description is not None:
            updates["description"] = description
        if settlement_id is not None:
            updates["settlement_id"] = settlement_id
        if entity_id is not None:
            updates["entity_id"] = entity_id

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with EventService() as service:
            event = service.update(event_id, **updates)

        if event is None:
            rprint(f"[red]✗ Event {event_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(
            f"[green]✓ Updated {event.event_type} event '{event.title}' (ID: {event.id})[/green]"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("route")
def update_route(
    route_id: int = typer.Argument(..., help="ID of route to update"),
    origin: Optional[int] = typer.Option(
        None, "--origin", help="New origin settlement ID"
    ),
    destination: Optional[int] = typer.Option(
        None, "--destination", help="New destination settlement ID"
    ),
    distance: Optional[float] = typer.Option(
        None, "--distance", "-d", help="New distance in km"
    ),
    route_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="New route type"
    ),
    difficulty: Optional[str] = typer.Option(
        None, "--difficulty", help="New difficulty level"
    ),
):
    """Update an existing route."""
    try:
        updates = {}
        if origin is not None:
            updates["origin_settlement_id"] = origin
        if destination is not None:
            updates["destination_settlement_id"] = destination
        if distance is not None:
            updates["distance_km"] = distance
        if route_type is not None:
            updates["route_type"] = route_type
        if difficulty is not None:
            updates["difficulty"] = difficulty

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with RouteService() as service:
            route = service.update(route_id, **updates)

        if route is None:
            rprint(f"[red]✗ Route {route_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(f"[green]✓ Updated route (ID: {route.id})[/green]")
        rprint(
            f"  From: Settlement {route.origin_settlement_id} → Settlement {route.destination_settlement_id}"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("snapshot")
def update_snapshot(
    snapshot_id: int = typer.Argument(..., help="ID of snapshot to update"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="New snapshot day"),
    population: Optional[int] = typer.Option(
        None, "--population", "-p", help="New population total"
    ),
):
    """Update an existing settlement snapshot."""
    try:
        updates = {}
        if day is not None:
            updates["astro_day"] = day
        if population is not None:
            updates["population_total"] = population

        if not updates:
            rprint("[yellow]No fields specified for update.[/yellow]")
            return

        with SnapshotService() as service:
            snapshot = service.update(snapshot_id, **updates)

        if snapshot is None:
            rprint(f"[red]✗ Snapshot {snapshot_id} not found.[/red]")
            raise typer.Exit(code=1)

        rprint(f"[green]✓ Updated snapshot (ID: {snapshot.id})[/green]")
        rprint(
            f"  Settlement: {snapshot.settlement_id}, Day: {snapshot.astro_day}, Population: {snapshot.population_total:,}"
        )

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


# Delete commands
@update_app.command("delete-epoch")
def delete_epoch(
    epoch_id: int = typer.Argument(..., help="ID of epoch to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete an epoch (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} epoch {epoch_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with EpochService() as service:
            # Get epoch info before deleting
            epoch = service.get_by_id(epoch_id)
            if epoch is None:
                rprint(f"[red]✗ Epoch {epoch_id} not found.[/red]")
                raise typer.Exit(code=1)

            epoch_name = epoch.name
            success = service.delete(epoch_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(
                f"[green]✓ {delete_msg} epoch '{epoch_name}' (ID: {epoch_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete epoch {epoch_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-region")
def delete_region(
    region_id: int = typer.Argument(..., help="ID of region to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a region (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} region {region_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with RegionService() as service:
            region = service.get_by_id(region_id)
            if region is None:
                rprint(f"[red]✗ Region {region_id} not found.[/red]")
                raise typer.Exit(code=1)

            region_name = region.name
            success = service.delete(region_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(
                f"[green]✓ {delete_msg} region '{region_name}' (ID: {region_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete region {region_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-province")
def delete_province(
    province_id: int = typer.Argument(..., help="ID of province to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a province (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} province {province_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with ProvinceService() as service:
            province = service.get_by_id(province_id)
            if province is None:
                rprint(f"[red]✗ Province {province_id} not found.[/red]")
                raise typer.Exit(code=1)

            province_name = province.name
            success = service.delete(province_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(
                f"[green]✓ {delete_msg} province '{province_name}' (ID: {province_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete province {province_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-settlement")
def delete_settlement(
    settlement_id: int = typer.Argument(..., help="ID of settlement to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a settlement (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} settlement {settlement_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with SettlementService() as service:
            settlement = service.get_by_id(settlement_id)
            if settlement is None:
                rprint(f"[red]✗ Settlement {settlement_id} not found.[/red]")
                raise typer.Exit(code=1)

            settlement_name = settlement.name
            success = service.delete(settlement_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(
                f"[green]✓ {delete_msg} settlement '{settlement_name}' (ID: {settlement_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete settlement {settlement_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-entity")
def delete_entity(
    entity_id: int = typer.Argument(..., help="ID of entity to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete an entity (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} entity {entity_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with EntityService() as service:
            entity = service.get_by_id(entity_id)
            if entity is None:
                rprint(f"[red]✗ Entity {entity_id} not found.[/red]")
                raise typer.Exit(code=1)

            entity_name = entity.name
            success = service.delete(entity_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(
                f"[green]✓ {delete_msg} entity '{entity_name}' (ID: {entity_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete entity {entity_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-event")
def delete_event(
    event_id: int = typer.Argument(..., help="ID of event to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete an event (deprecates the event)."""
    try:
        if not yes:
            if not Confirm.ask(f"Are you sure you want to deprecate event {event_id}?"):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with EventService() as service:
            event = service.get_by_id(event_id)
            if event is None:
                rprint(f"[red]✗ Event {event_id} not found.[/red]")
                raise typer.Exit(code=1)

            event_title = event.title
            # Events use is_deprecated field, handled by base delete
            success = service.delete(event_id, soft=True)

        if success:
            rprint(
                f"[green]✓ Deprecated event '{event_title}' (ID: {event_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete event {event_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-route")
def delete_route(
    route_id: int = typer.Argument(..., help="ID of route to delete"),
    hard: bool = typer.Option(
        False, "--hard", help="Permanently delete (default: soft delete)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a route (soft delete by default)."""
    try:
        if not yes:
            delete_type = "permanently delete" if hard else "deactivate"
            if not Confirm.ask(
                f"Are you sure you want to {delete_type} route {route_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with RouteService() as service:
            route = service.get_by_id(route_id)
            if route is None:
                rprint(f"[red]✗ Route {route_id} not found.[/red]")
                raise typer.Exit(code=1)

            route_info = (
                f"{route.origin_settlement_id} → {route.destination_settlement_id}"
            )
            success = service.delete(route_id, soft=not hard)

        if success:
            delete_msg = "Permanently deleted" if hard else "Deactivated"
            rprint(f"[green]✓ {delete_msg} route {route_info} (ID: {route_id})[/green]")
        else:
            rprint(f"[red]✗ Failed to delete route {route_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@update_app.command("delete-snapshot")
def delete_snapshot(
    snapshot_id: int = typer.Argument(..., help="ID of snapshot to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a settlement snapshot (permanent deletion)."""
    try:
        if not yes:
            if not Confirm.ask(
                f"Are you sure you want to permanently delete snapshot {snapshot_id}?"
            ):
                rprint("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with SnapshotService() as service:
            snapshot = service.get_by_id(snapshot_id)
            if snapshot is None:
                rprint(f"[red]✗ Snapshot {snapshot_id} not found.[/red]")
                raise typer.Exit(code=1)

            snapshot_info = (
                f"Settlement {snapshot.settlement_id}, Day {snapshot.astro_day}"
            )
            # Snapshots don't have is_active, so always hard delete
            success = service.delete(snapshot_id, soft=False)

        if success:
            rprint(
                f"[green]✓ Deleted snapshot {snapshot_info} (ID: {snapshot_id})[/green]"
            )
        else:
            rprint(f"[red]✗ Failed to delete snapshot {snapshot_id}.[/red]")
            raise typer.Exit(code=1)

    except ValueError as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)
