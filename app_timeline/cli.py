"""
app_timeline.cli

Command-line interface for timeline database management.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .cli_data import data_app
from .cli_list import list_app
from .cli_update import update_app
from .config import get_config
from .db import (
    create_all_tables,
    drop_all_tables,
    get_table_info,
    get_table_row_counts,
    validate_schema,
)

app = typer.Typer(help="Saskan Timeline database management")
db_app = typer.Typer(help="Database management commands")
app.add_typer(db_app, name="db")
app.add_typer(data_app, name="data")
app.add_typer(list_app, name="list")
app.add_typer(update_app, name="update")

console = Console()


@db_app.command("init")
def init_database():
    """Initialize the database by creating all tables."""
    try:
        config = get_config()
        rprint(f"[cyan]Initializing database at: {config.database.path}[/cyan]")

        # Ensure directory exists
        db_path = Path(config.database.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create tables
        create_all_tables()

        rprint("[green] Database initialized successfully![/green]")
        rprint(f"[green] Tables created in: {config.database.path}[/green]")

        # Show what was created
        table_info = get_table_info()
        rprint(f"\n[cyan]Created {len(table_info)} tables:[/cyan]")
        for table_name in sorted(table_info.keys()):
            rprint(f"  • {table_name}")

    except Exception as e:
        rprint(f"[red] Error initializing database: {e}[/red]")
        raise typer.Exit(code=1)


@db_app.command("drop")
def drop_database(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Drop all tables from the database. WARNING: Deletes all data!"""
    config = get_config()

    if not confirm:
        rprint(
            f"[yellow]WARNING: This will delete all tables and data from {config.database.path}[/yellow]"
        )
        response = typer.prompt("Are you sure? (yes/no)")
        if response.lower() not in ["yes", "y"]:
            rprint("[cyan]Operation cancelled.[/cyan]")
            raise typer.Exit()

    try:
        rprint("[cyan]Dropping all tables...[/cyan]")
        drop_all_tables()
        rprint("[green] All tables dropped successfully![/green]")

    except Exception as e:
        rprint(f"[red] Error dropping tables: {e}[/red]")
        raise typer.Exit(code=1)


@db_app.command("info")
def show_database_info():
    """Show database information (path, tables, row counts)."""
    try:
        config = get_config()

        # Database location
        rprint(f"\n[cyan]Database Information[/cyan]")
        rprint(f"  Path: {config.database.path}")
        rprint(f"  Dialect: {config.database.dialect}")

        db_path = Path(config.database.path)
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            rprint(f"  Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        else:
            rprint(f"  Status: [yellow]Database file does not exist[/yellow]")
            return

        # Table information
        table_info = get_table_info()
        if not table_info:
            rprint("\n[yellow]No tables found in database.[/yellow]")
            return

        # Row counts
        row_counts = get_table_row_counts()

        # Create table
        table = Table(
            title="\nDatabase Tables", show_header=True, header_style="bold cyan"
        )
        table.add_column("Table Name", style="cyan")
        table.add_column("Columns", justify="right")
        table.add_column("Rows", justify="right", style="green")

        total_rows = 0
        for table_name in sorted(table_info.keys()):
            info = table_info[table_name]
            rows = row_counts.get(table_name, 0)
            total_rows += rows
            table.add_row(
                table_name,
                str(info["column_count"]),
                f"{rows:,}",
            )

        table.add_row("[bold]TOTAL[/bold]", "", f"[bold]{total_rows:,}[/bold]")

        console.print(table)

    except Exception as e:
        rprint(f"[red] Error getting database info: {e}[/red]")
        raise typer.Exit(code=1)


@db_app.command("validate")
def validate_database():
    """Validate the database schema."""
    try:
        rprint("[cyan]Validating database schema...[/cyan]")

        messages = validate_schema()

        if len(messages) == 1 and "passed" in messages[0].lower():
            rprint(f"[green] {messages[0]}[/green]")
        else:
            rprint("[yellow]Validation messages:[/yellow]")
            for msg in messages:
                rprint(f"  • {msg}")

    except Exception as e:
        rprint(f"[red] Error validating schema: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("version")
def show_version():
    """Show timeline application version."""
    config = get_config()
    rprint(f"[cyan]Saskan Timeline v{config.app.version}[/cyan]")


if __name__ == "__main__":
    app()
