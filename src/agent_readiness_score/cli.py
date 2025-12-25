"""Agent-Ready CLI application."""

from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

# Import scanners to trigger auto-registration
from agent_readiness_score import scanners  # noqa: F401

from agent_readiness_score.core.engine import ScanEngine
from agent_readiness_score.core.models import Category, CATEGORY_WEIGHTS
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.output.console import ConsoleFormatter
from agent_readiness_score.output.json_output import JSONFormatter


class OutputFormat(str, Enum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"
    BOTH = "both"


app = typer.Typer(
    name="agent-ready",
    help="Calculate Agent Readiness Score (0-100) for software repositories.",
    add_completion=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from agent_readiness_score import __version__

        console.print(f"agent-ready version {__version__}")
        raise typer.Exit()


@app.command()
def scan(
    path: Path = typer.Argument(
        ".",
        help="Path to the repository to scan.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.BOTH,
        "--output",
        "-o",
        help="Output format: table, json, or both.",
    ),
    json_file: Path | None = typer.Option(
        None,
        "--json-file",
        "-j",
        help="Save JSON report to file.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed findings for each category.",
    ),
    min_score: int | None = typer.Option(
        None,
        "--min-score",
        help="Exit with error if score is below this threshold.",
        min=0,
        max=100,
    ),
) -> None:
    """Scan a repository and calculate its Agent Readiness Score.

    The score (0-100) indicates how well the repository is prepared
    for AI agent-assisted development based on 8 categories:

    - Style & Validation (15%): Linter and formatter configs
    - Build Systems (10%): Build tools and CI/CD
    - Dev Environments (15%): Containerization and reproducibility
    - Observability (10%): Logging and monitoring
    - Testing (20%): Test frameworks and coverage
    - Dependencies (10%): Lockfiles and security scanning
    - Documentation (10%): README, docs, and API specs
    - Static Typing (10%): Type definitions and checkers
    """
    engine = ScanEngine()

    try:
        with console.status("[bold blue]Scanning repository..."):
            report = engine.scan(path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    # Output results
    console_formatter = ConsoleFormatter(console, verbose=verbose)
    json_formatter = JSONFormatter()

    if output in (OutputFormat.TABLE, OutputFormat.BOTH):
        console_formatter.format(report)

    if output in (OutputFormat.JSON, OutputFormat.BOTH):
        json_output = json_formatter.format(report)
        if output == OutputFormat.JSON:
            console.print(json_output)

    if json_file:
        json_formatter.save(report, json_file)
        console.print(f"\n[dim]JSON report saved to:[/dim] {json_file}")

    # Check minimum score threshold
    if min_score is not None and report.total_score < min_score:
        console.print(
            f"\n[red]Score {report.total_score:.1f} is below minimum threshold {min_score}[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def categories() -> None:
    """List all scoring categories and their weights."""
    from rich.table import Table

    table = Table(title="Agent Readiness Scoring Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Weight", justify="right", style="green")
    table.add_column("Description", style="dim")

    for category in Category:
        scanner = ScannerRegistry.get(category)
        weight = CATEGORY_WEIGHTS[category]
        description = scanner.description if scanner else "No scanner registered"
        table.add_row(
            category.value.replace("_", " ").title(),
            f"{weight * 100:.0f}%",
            description,
        )

    console.print(table)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Agent-Ready: Repository readiness scanner for AI agents."""
    pass


if __name__ == "__main__":
    app()
