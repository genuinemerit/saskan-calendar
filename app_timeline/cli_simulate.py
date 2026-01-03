"""
app_timeline.cli_simulate

CLI commands for macro-scale simulation.

PR-003b: Provides `simulate region` and `simulate province` commands
with Rich output formatting and progress tracking.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .simulation import SimulationEngine, load_simulation_config_from_settings

simulate_app = typer.Typer(help="Macro-scale simulation commands")
console = Console()


@simulate_app.command("region")
def simulate_region(
    region_id: int = typer.Argument(..., help="Region ID to simulate"),
    start_day: int = typer.Option(..., "--start", help="Starting astro_day"),
    end_day: int = typer.Option(..., "--end", help="Ending astro_day"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducibility"),
    granularity: str = typer.Option("year", "--granularity", help="Snapshot granularity (year/decade/century)"),
    chunk_size: Optional[int] = typer.Option(None, "--chunk-size", help="Chunk size in days (default: 100 years = 36525 days)")
):
    """
    Run macro-scale simulation for a region.

    Simulates population dynamics using logistic growth, carrying capacity,
    and applies human-authored events from the database.

    Examples:
        # Simulate first 100 years with annual snapshots
        saskan-timeline simulate region 1 --start 0 --end 36525 --granularity year

        # Simulate with decade granularity and reproducible seed
        saskan-timeline simulate region 1 --start 0 --end 36525 --seed 42 --granularity decade

        # Simulate 500 years in 50-year chunks
        saskan-timeline simulate region 2 --start 0 --end 182625 --chunk-size 18262
    """
    try:
        # Load configuration from settings
        config = load_simulation_config_from_settings(
            entity_type="region",
            seed=seed,
            chunk_size_days=chunk_size
        )

        rprint(f"\n[cyan]Starting simulation for region {region_id}[/cyan]")
        rprint(f"  Time range: days {start_day} to {end_day}")
        rprint(f"  Granularity: {granularity}")
        rprint(f"  Seed: {config.seed}")
        rprint(f"  Chunk size: {config.chunk_size_days} days\n")

        # Create engine
        engine = SimulationEngine(
            entity_type="region",
            entity_id=region_id,
            config=config
        )

        # Run simulation
        reports = engine.run(start_day, end_day, granularity)

        # Display results
        _display_simulation_results(reports, "region", region_id)

        rprint("\n[green]✓ Simulation complete![/green]\n")

    except ValueError as e:
        rprint(f"[red]✗ Validation error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Simulation failed: {e}[/red]")
        raise typer.Exit(code=1)


@simulate_app.command("province")
def simulate_province(
    province_id: int = typer.Argument(..., help="Province ID to simulate"),
    start_day: int = typer.Option(..., "--start", help="Starting astro_day"),
    end_day: int = typer.Option(..., "--end", help="Ending astro_day"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducibility"),
    granularity: str = typer.Option("year", "--granularity", help="Snapshot granularity (year/decade/century)"),
    chunk_size: Optional[int] = typer.Option(None, "--chunk-size", help="Chunk size in days (default: 100 years = 36525 days)")
):
    """
    Run macro-scale simulation for a province.

    Simulates population dynamics using logistic growth, carrying capacity,
    and applies human-authored events from the database.

    Examples:
        # Simulate first 100 years
        saskan-timeline simulate province 1 --start 0 --end 36525

        # Simulate with reproducible seed
        saskan-timeline simulate province 1 --start 0 --end 36525 --seed 42
    """
    try:
        # Load configuration from settings
        config = load_simulation_config_from_settings(
            entity_type="province",
            seed=seed,
            chunk_size_days=chunk_size
        )

        rprint(f"\n[cyan]Starting simulation for province {province_id}[/cyan]")
        rprint(f"  Time range: days {start_day} to {end_day}")
        rprint(f"  Granularity: {granularity}")
        rprint(f"  Seed: {config.seed}")
        rprint(f"  Chunk size: {config.chunk_size_days} days\n")

        # Create engine
        engine = SimulationEngine(
            entity_type="province",
            entity_id=province_id,
            config=config
        )

        # Run simulation
        reports = engine.run(start_day, end_day, granularity)

        # Display results
        _display_simulation_results(reports, "province", province_id)

        rprint("\n[green]✓ Simulation complete![/green]\n")

    except ValueError as e:
        rprint(f"[red]✗ Validation error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗ Simulation failed: {e}[/red]")
        raise typer.Exit(code=1)


def _display_simulation_results(
    reports: list,
    entity_type: str,
    entity_id: int
):
    """
    Display simulation results in Rich table.

    :param reports: List of chunk reports from engine
    :param entity_type: "region" or "province"
    :param entity_id: Entity ID
    """
    if not reports:
        rprint("[yellow]No results to display[/yellow]")
        return

    # Create summary table
    table = Table(
        title=f"\nSimulation Results: {entity_type.title()} {entity_id}",
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Chunk", style="cyan", width=8)
    table.add_column("Days", justify="right", width=20)
    table.add_column("Final Pop.", justify="right", style="green", width=15)
    table.add_column("Capacity", justify="right", style="yellow", width=15)
    table.add_column("Utilization", justify="right", width=12)

    for i, report in enumerate(reports, 1):
        days_range = f"{report['start_day']:,} - {report['end_day']:,}"
        pop = report['final_population']
        K = report['carrying_capacity']
        utilization = f"{(pop/K*100):.1f}%" if K > 0 else "N/A"

        table.add_row(
            f"#{i}",
            days_range,
            f"{pop:,}",
            f"{K:,}",
            utilization
        )

    console.print(table)

    # Display species breakdown for final chunk if available
    final_report = reports[-1]
    if final_report.get('population_by_species'):
        rprint("\n[bold]Final Species Breakdown:[/bold]")
        for species, pop in final_report['population_by_species'].items():
            percentage = (pop / final_report['final_population'] * 100) if final_report['final_population'] > 0 else 0
            rprint(f"  {species}: {pop:,} ({percentage:.1f}%)")

    # Display environmental factors
    rprint("\n[bold]Final Environmental Factors:[/bold]")
    rprint(f"  Environmental: {final_report.get('environmental_factor', 0):.3f}")
    rprint(f"  Infrastructure: {final_report.get('infrastructure_factor', 0):.3f}")
    rprint(f"  Location: {final_report.get('location_factor', 0):.3f}")
