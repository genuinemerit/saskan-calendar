"""
app_timeline.cli_import_export

CLI commands for importing and exporting timeline data.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

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

io_app = typer.Typer(help="Import and export timeline data")


@io_app.command("export")
def export_data(
    output: Optional[Path] = typer.Argument(None, help="Output JSON file path (default: data/timeline/exports/[type]_[timestamp].json)"),
    entity_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Export specific entity type (epochs/regions/provinces/settlements/entities/events/routes/snapshots/region_snapshots/province_snapshots)",
    ),
    include_inactive: bool = typer.Option(
        False, "--include-inactive", help="Include inactive/deprecated records"
    ),
):
    """
    Export timeline data to JSON file.

    Exports all or filtered timeline entities. By default, only active records
    are exported. If no output path is provided, exports to
    data/timeline/exports/[type]_[timestamp].json
    """
    try:
        # Generate default output path if not provided
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_name = entity_type if entity_type else "all"
            default_dir = Path("data/timeline/exports")
            default_dir.mkdir(parents=True, exist_ok=True)
            output = default_dir / f"{type_name}_{timestamp}.json"
            rprint(f"[dim]No output path specified, using: {output}[/dim]")

        data = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Determine what to export
            export_all = entity_type is None

            # Export epochs
            if export_all or entity_type == "epochs":
                _ = progress.add_task(description="Exporting epochs...", total=None)
                with EpochService() as service:
                    epochs = service.list_all(active_only=not include_inactive)
                    data["epochs"] = [
                        {
                            "name": e.name,
                            "start_astro_day": e.start_astro_day,
                            "end_astro_day": e.end_astro_day,
                            "description": e.description,
                            "meta_data": e.meta_data,
                        }
                        for e in epochs
                    ]

            # Export regions
            if export_all or entity_type == "regions":
                _ = progress.add_task(description="Exporting regions...", total=None)
                with RegionService() as service:
                    regions = service.list_all(active_only=not include_inactive)
                    data["regions"] = [
                        {
                            "name": r.name,
                            "meta_data": r.meta_data,
                        }
                        for r in regions
                    ]

            # Export provinces
            if export_all or entity_type == "provinces":
                _ = progress.add_task(description="Exporting provinces...", total=None)
                with ProvinceService() as service:
                    provinces = service.list_all(active_only=not include_inactive)
                    data["provinces"] = [
                        {
                            "name": p.name,
                            "region_id": p.region_id,
                            "meta_data": p.meta_data,
                        }
                        for p in provinces
                    ]

            # Export settlements
            if export_all or entity_type == "settlements":
                _ = progress.add_task(
                    description="Exporting settlements...", total=None
                )
                with SettlementService() as service:
                    settlements = service.list_all(active_only=not include_inactive)
                    data["settlements"] = [
                        {
                            "name": s.name,
                            "settlement_type": s.settlement_type,
                            "province_id": s.province_id,
                            "grid_x": s.grid_x,
                            "grid_y": s.grid_y,
                            "meta_data": s.meta_data,
                        }
                        for s in settlements
                    ]

            # Export entities
            if export_all or entity_type == "entities":
                _ = progress.add_task(description="Exporting entities...", total=None)
                with EntityService() as service:
                    entities = service.list_all(active_only=not include_inactive)
                    data["entities"] = [
                        {
                            "name": e.name,
                            "entity_type": e.entity_type,
                            "founded_astro_day": e.founded_astro_day,
                            "dissolved_astro_day": e.dissolved_astro_day,
                            "description": e.description,
                            "meta_data": e.meta_data,
                        }
                        for e in entities
                    ]

            # Export events
            if export_all or entity_type == "events":
                _ = progress.add_task(description="Exporting events...", total=None)
                with EventService() as service:
                    events = service.list_all(active_only=not include_inactive)
                    data["events"] = [
                        {
                            "title": ev.title,
                            "event_type": ev.event_type,
                            "astro_day": ev.astro_day,
                            "description": ev.description,
                            "settlement_id": ev.settlement_id,
                            "entity_id": ev.entity_id,
                            "meta_data": ev.meta_data,
                        }
                        for ev in events
                    ]

            # Export routes
            if export_all or entity_type == "routes":
                _ = progress.add_task(description="Exporting routes...", total=None)
                with RouteService() as service:
                    routes = service.list_all(active_only=not include_inactive)
                    data["routes"] = [
                        {
                            "origin_settlement_id": r.origin_settlement_id,
                            "destination_settlement_id": r.destination_settlement_id,
                            "distance_km": r.distance_km,
                            "route_type": r.route_type,
                            "difficulty": r.difficulty,
                            "meta_data": r.meta_data,
                        }
                        for r in routes
                    ]

            # Export snapshots (settlement snapshots)
            if export_all or entity_type == "snapshots":
                _ = progress.add_task(description="Exporting snapshots...", total=None)
                with SnapshotService() as service:
                    snapshots = service.list_all()
                    data["snapshots"] = [
                        {
                            "settlement_id": s.settlement_id,
                            "astro_day": s.astro_day,
                            "population_total": s.population_total,
                            "population_by_species": s.population_by_species,
                            "population_by_habitat": s.population_by_habitat,
                            "cultural_composition": s.cultural_composition,
                            "economic_data": s.economic_data,
                            "snapshot_type": s.snapshot_type,
                            "granularity": s.granularity,
                            "meta_data": s.meta_data,
                        }
                        for s in snapshots
                    ]

            # Export region snapshots
            if export_all or entity_type == "region_snapshots":
                _ = progress.add_task(
                    description="Exporting region snapshots...", total=None
                )
                with RegionSnapshotService() as service:
                    region_snapshots = service.list_all()
                    data["region_snapshots"] = [
                        {
                            "region_id": s.region_id,
                            "astro_day": s.astro_day,
                            "population_total": s.population_total,
                            "population_by_species": s.population_by_species,
                            "population_by_habitat": s.population_by_habitat,
                            "cultural_composition": s.cultural_composition,
                            "economic_data": s.economic_data,
                            "snapshot_type": s.snapshot_type,
                            "granularity": s.granularity,
                            "meta_data": s.meta_data,
                        }
                        for s in region_snapshots
                    ]

            # Export province snapshots
            if export_all or entity_type == "province_snapshots":
                _ = progress.add_task(
                    description="Exporting province snapshots...", total=None
                )
                with ProvinceSnapshotService() as service:
                    province_snapshots = service.list_all()
                    data["province_snapshots"] = [
                        {
                            "province_id": s.province_id,
                            "astro_day": s.astro_day,
                            "population_total": s.population_total,
                            "population_by_species": s.population_by_species,
                            "population_by_habitat": s.population_by_habitat,
                            "cultural_composition": s.cultural_composition,
                            "economic_data": s.economic_data,
                            "snapshot_type": s.snapshot_type,
                            "granularity": s.granularity,
                            "meta_data": s.meta_data,
                        }
                        for s in province_snapshots
                    ]

        # Write to file
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(data, f, indent=2)

        # Count records
        total_records = sum(len(v) for v in data.values())

        rprint(f"[green]✓ Exported {total_records} records to {output}[/green]")
        for entity, records in data.items():
            rprint(f"  {entity}: {len(records)} records")

    except Exception as e:
        rprint(f"[red]✗ Export failed: {e}[/red]")
        raise typer.Exit(code=1)


@io_app.command("import")
def import_data(
    input_file: Path = typer.Argument(..., help="Input JSON file path"),
    skip_existing: bool = typer.Option(
        False, "--skip-existing", help="Skip records that already exist (by name)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be imported without making changes"
    ),
):
    """
    Import timeline data from JSON file.

    Reads a JSON file containing timeline entities and imports them into the database.
    The JSON format should match the structure produced by the export command. Can
    import partial data (only the entity types present in the file will be imported).

    The Progress context manager (from Rich library) is used to display spinners
    during import. The progress.add_task() calls register tasks for display but
    don't require tracking since we use indeterminate spinners (total=None).

    For entities with unique names (epochs, regions, provinces, settlements, entities),
    the --skip-existing flag can be used to skip records that already exist (matched
    by name). This is useful for incremental imports or merging datasets.

    For entities without unique names (events, routes, snapshots), records are always
    created (skip_existing does not apply).

    :param input_file: Path to JSON file to import from
    :param skip_existing: If True, skip records with names that already exist in database
    :param dry_run: If True, show what would be imported without making changes
    :raises typer.Exit: On import failure (file not found, invalid JSON, import errors) with code 1
    """
    try:
        # Read input file
        if not input_file.exists():
            rprint(f"[red]✗ File not found: {input_file}[/red]")
            raise typer.Exit(code=1)

        with open(input_file) as f:
            data = json.load(f)

        if dry_run:
            rprint("[yellow]DRY RUN - No changes will be made[/yellow]\n")

        stats = {
            "created": 0,
            "skipped": 0,
            "errors": 0,
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Import epochs
            if "epochs" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['epochs'])} epochs...", total=None
                )
                for epoch_data in data["epochs"]:
                    try:
                        if dry_run:
                            rprint(f"  Would create epoch: {epoch_data['name']}")
                            stats["created"] += 1
                            continue

                        with EpochService() as service:
                            # Check if exists
                            if skip_existing:
                                existing = service.get_by_name(epoch_data["name"])
                                if existing:
                                    stats["skipped"] += 1
                                    continue

                            service.create_epoch(**epoch_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing epoch '{epoch_data.get('name')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import regions
            if "regions" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['regions'])} regions...",
                    total=None,
                )
                for region_data in data["regions"]:
                    try:
                        if dry_run:
                            rprint(f"  Would create region: {region_data['name']}")
                            stats["created"] += 1
                            continue

                        with RegionService() as service:
                            if skip_existing:
                                existing = service.get_by_name(region_data["name"])
                                if existing:
                                    stats["skipped"] += 1
                                    continue

                            service.create_region(**region_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing region '{region_data.get('name')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import provinces
            if "provinces" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['provinces'])} provinces...",
                    total=None,
                )
                for province_data in data["provinces"]:
                    try:
                        if dry_run:
                            rprint(f"  Would create province: {province_data['name']}")
                            stats["created"] += 1
                            continue

                        with ProvinceService() as service:
                            if skip_existing:
                                existing = service.get_by_name(province_data["name"])
                                if existing:
                                    stats["skipped"] += 1
                                    continue

                            service.create_province(**province_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing province '{province_data.get('name')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import settlements
            if "settlements" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['settlements'])} settlements...",
                    total=None,
                )
                for settlement_data in data["settlements"]:
                    try:
                        if dry_run:
                            rprint(
                                f"  Would create settlement: {settlement_data['name']}"
                            )
                            stats["created"] += 1
                            continue

                        with SettlementService() as service:
                            if skip_existing:
                                existing = service.get_by_name(settlement_data["name"])
                                if existing:
                                    stats["skipped"] += 1
                                    continue

                            service.create_settlement(**settlement_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing settlement '{settlement_data.get('name')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import entities
            if "entities" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['entities'])} entities...",
                    total=None,
                )
                for entity_data in data["entities"]:
                    try:
                        if dry_run:
                            rprint(f"  Would create entity: {entity_data['name']}")
                            stats["created"] += 1
                            continue

                        with EntityService() as service:
                            if skip_existing:
                                existing = service.get_by_name(entity_data["name"])
                                if existing:
                                    stats["skipped"] += 1
                                    continue

                            service.create_entity(**entity_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing entity '{entity_data.get('name')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import events
            if "events" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['events'])} events...", total=None
                )
                for event_data in data["events"]:
                    try:
                        if dry_run:
                            rprint(f"  Would create event: {event_data['title']}")
                            stats["created"] += 1
                            continue

                        with EventService() as service:
                            # Events don't have unique names, so skip_existing doesn't apply
                            service.create_event(**event_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(
                            f"[red]  Error importing event '{event_data.get('title')}': {e}[/red]"
                        )
                        stats["errors"] += 1

            # Import routes
            if "routes" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['routes'])} routes...", total=None
                )
                for route_data in data["routes"]:
                    try:
                        if dry_run:
                            rprint(
                                f"  Would create route: {route_data['origin_settlement_id']} → {route_data['destination_settlement_id']}"
                            )
                            stats["created"] += 1
                            continue

                        with RouteService() as service:
                            # Routes don't have unique names, so skip_existing doesn't apply
                            service.create_route(**route_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(f"[red]  Error importing route: {e}[/red]")
                        stats["errors"] += 1

            # Import settlement snapshots
            if "snapshots" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['snapshots'])} snapshots...",
                    total=None,
                )
                for snapshot_data in data["snapshots"]:
                    try:
                        if dry_run:
                            rprint(
                                f"  Would create snapshot: Settlement {snapshot_data['settlement_id']} @ Day {snapshot_data['astro_day']}"
                            )
                            stats["created"] += 1
                            continue

                        with SnapshotService() as service:
                            # Snapshots don't have unique names, so skip_existing doesn't apply
                            service.create_snapshot(**snapshot_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(f"[red]  Error importing snapshot: {e}[/red]")
                        stats["errors"] += 1

            # Import region snapshots
            if "region_snapshots" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['region_snapshots'])} region snapshots...",
                    total=None,
                )
                for snapshot_data in data["region_snapshots"]:
                    try:
                        if dry_run:
                            rprint(
                                f"  Would create region snapshot: Region {snapshot_data['region_id']} @ Day {snapshot_data['astro_day']}"
                            )
                            stats["created"] += 1
                            continue

                        with RegionSnapshotService() as service:
                            # Snapshots don't have unique names, so skip_existing doesn't apply
                            service.create_snapshot(**snapshot_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(f"[red]  Error importing region snapshot: {e}[/red]")
                        stats["errors"] += 1

            # Import province snapshots
            if "province_snapshots" in data:
                _ = progress.add_task(
                    description=f"Importing {len(data['province_snapshots'])} province snapshots...",
                    total=None,
                )
                for snapshot_data in data["province_snapshots"]:
                    try:
                        if dry_run:
                            rprint(
                                f"  Would create province snapshot: Province {snapshot_data['province_id']} @ Day {snapshot_data['astro_day']}"
                            )
                            stats["created"] += 1
                            continue

                        with ProvinceSnapshotService() as service:
                            # Snapshots don't have unique names, so skip_existing doesn't apply
                            service.create_snapshot(**snapshot_data)
                            stats["created"] += 1
                    except Exception as e:
                        rprint(f"[red]  Error importing province snapshot: {e}[/red]")
                        stats["errors"] += 1

        # Print summary
        rprint()
        if dry_run:
            rprint(f"[yellow]DRY RUN COMPLETE[/yellow]")
            rprint(f"  Would create: {stats['created']} records")
        else:
            rprint(f"[green]✓ Import complete[/green]")
            rprint(f"  Created: {stats['created']} records")
            if stats["skipped"] > 0:
                rprint(f"  Skipped: {stats['skipped']} records")

        if stats["errors"] > 0:
            rprint(f"[red]  Errors: {stats['errors']} records[/red]")
            raise typer.Exit(code=1)

    except json.JSONDecodeError as e:
        rprint(f"[red]✗ Invalid JSON file: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Import failed: {e}[/red]")
        raise typer.Exit(code=1)
