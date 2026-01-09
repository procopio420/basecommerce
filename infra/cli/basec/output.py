"""Output helpers using Rich for formatted CLI output."""

from contextlib import contextmanager
from typing import Any, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str, end: str = "\n") -> None:
    """Print error message in red.
    
    Args:
        message: Error message to print
        end: End character (default: newline, use "" for streaming)
    """
    console.print(f"[red]✗[/red] {message}", end=end)


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[Any]],
    show_header: bool = True,
) -> None:
    """Print a formatted table using Rich."""
    table = Table(title=title, show_header=show_header, header_style="bold magenta")
    
    for col in columns:
        table.add_column(col)
    
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    console.print(table)


@contextmanager
def spinner(message: str):
    """Context manager for showing a spinner during long operations."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(message, total=None)
        yield progress


def print_header(text: str) -> None:
    """Print a formatted header."""
    console.print(f"\n[bold cyan]{'=' * 60}[/bold cyan]")
    console.print(f"[bold cyan]{text}[/bold cyan]")
    console.print(f"[bold cyan]{'=' * 60}[/bold cyan]\n")


def print_section(text: str) -> None:
    """Print a section header."""
    console.print(f"\n[bold yellow]{text}[/bold yellow]")


def print_json(data: dict) -> None:
    """Print JSON data in a formatted way."""
    from rich.json import JSON
    
    console.print(JSON.from_data(data))


def confirm(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    default_text = "Y/n" if default else "y/N"
    response = console.input(f"{message} [{default_text}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ("y", "yes")

