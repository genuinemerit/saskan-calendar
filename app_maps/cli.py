import typer
from pathlib import Path
from typing import Optional

from .geo import demo_distance
from .graphs import demo_shortest_path
from .saskan import run_simulation
from .saskan.engine import SaskanEngine
from .saskan.map_utils import render_coarse_map, summarize_settlements
from .saskan.plotting import plot_state
from .saskan.settings import SimulationConfig

app = typer.Typer(help="Geo/graph experiments sandbox")


@app.command()
def geo(kind: str = "distance"):
    if kind == "distance":
        typer.echo(demo_distance())
    else:
        typer.echo("unknown geo experiment")


@app.command()
def graph(kind: str = "shortest"):
    if kind == "shortest":
        typer.echo(demo_shortest_path())
    else:
        typer.echo("unknown graph experiment")


@app.command("saskan-sim")
def saskan_sim(
    steps: int = typer.Option(8, help="Number of simulation steps to run."),
    seed: Optional[int] = typer.Option(
        None, help="Optional seed for deterministic runs."
    ),
    scenario: Optional[str] = typer.Option(
        None, help="Named scenario preset (sets seed if provided)."
    ),
    tick_unit: str = typer.Option(
        "year", help="Label for a time step (year/season/generation/etc.)."
    ),
    tick_length: float = typer.Option(
        1.0, help="Length of one tick in the chosen unit."
    ),
    snapshot_every: int = typer.Option(
        0, help="Persist a JSON snapshot every N steps (0 to disable)."
    ),
    snapshot_dir: Path = typer.Option(
        Path("data/experiments/saskan"),
        help="Directory for JSON snapshots when enabled.",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
):
    """Run the Saskan Lands settlement growth simulation."""
    for line in run_simulation(
        steps=steps,
        seed=seed,
        scenario=scenario,
        tick_unit=tick_unit,
        tick_length=tick_length,
        snapshot_every=snapshot_every,
        snapshot_dir=str(snapshot_dir),
    ):
        typer.echo(line)


@app.command("saskan-map")
def saskan_map(
    steps: int = typer.Option(
        30, help="Number of simulation steps to run before rendering."
    ),
    seed: Optional[int] = typer.Option(
        None, help="Optional seed for deterministic runs."
    ),
    scenario: Optional[str] = typer.Option(
        "great-migration", help="Named scenario preset."
    ),
    col_min: int = typer.Option(30, help="Min column (C#) for coarse map window."),
    col_max: int = typer.Option(38, help="Max column (C#) for coarse map window."),
    row_min: int = typer.Option(8, help="Min row (R#) for coarse map window."),
    row_max: int = typer.Option(20, help="Max row (R#) for coarse map window."),
):
    """Run a simulation and print a coarse block map plus settlement summary."""
    engine = SaskanEngine(
        config=SimulationConfig(
            steps=steps,
            seed=seed,
            scenario=scenario,
        )
    )
    for _ in range(steps):
        engine.step()
    for line in render_coarse_map(
        engine.state,
        block_size_km=engine.config.block_size_km,
        col_min=col_min,
        col_max=col_max,
        row_min=row_min,
        row_max=row_max,
    ):
        typer.echo(line)
    typer.echo("")
    for line in summarize_settlements(
        engine.state, block_size_km=engine.config.block_size_km
    ):
        typer.echo(line)


@app.command("saskan-plot")
def saskan_plot(
    steps: int = typer.Option(
        30, help="Number of simulation steps to run before plotting."
    ),
    seed: Optional[int] = typer.Option(
        None, help="Optional seed for deterministic runs."
    ),
    scenario: Optional[str] = typer.Option(
        "great-migration", help="Named scenario preset."
    ),
    col_min: int = typer.Option(30, help="Min column (C#) for plot window."),
    col_max: int = typer.Option(38, help="Max column (C#) for plot window."),
    row_min: int = typer.Option(8, help="Min row (R#) for plot window."),
    row_max: int = typer.Option(20, help="Max row (R#) for plot window."),
    outfile: Path = typer.Option(
        Path("data/experiments/saskan/maps/ingar.png"),
        help="Output PNG path for the map.",
        writable=True,
    ),
):
    """Run a simulation and save a matplotlib map (requires matplotlib)."""
    try:
        engine = SaskanEngine(
            config=SimulationConfig(
                steps=steps,
                seed=seed,
                scenario=scenario,
            )
        )
        for _ in range(steps):
            engine.step()
        outfile = outfile.expanduser()
        plot_state(
            engine.state,
            block_size_km=engine.config.block_size_km,
            outfile=outfile,
            col_min=col_min,
            col_max=col_max,
            row_min=row_min,
            row_max=row_max,
        )
        typer.echo(f"Saved plot to {outfile}")
    except ImportError:
        typer.echo(
            "matplotlib is required for plotting; install with `poetry add matplotlib` or `pip install matplotlib`.",
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
