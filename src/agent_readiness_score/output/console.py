"""Rich console output formatter."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agent_readiness_score.core.models import ScanReport, RepoType

# Progress bar configuration
PROGRESS_BAR_WIDTH = 10


class ConsoleFormatter:
    """Rich console output formatter with tables and colors."""

    def __init__(self, console: Console | None = None, verbose: bool = False):
        self.console = console or Console()
        self.verbose = verbose

    def format(self, report: ScanReport) -> None:
        """Print formatted report to console."""
        self._print_header(report)

        # For multi-package repos, show per-package breakdown
        if report.repo_structure and report.repo_structure.is_multi_package and report.package_scores:
            self._print_package_table(report)
            self._print_shared_infrastructure(report)

        self._print_category_table(report)

        if self.verbose:
            self._print_findings(report)

        self._print_summary(report)

    def _print_header(self, report: ScanReport) -> None:
        """Print report header with repo info."""
        languages = ", ".join(report.detected_languages) if report.detected_languages else "None detected"

        # Add structure info for multi-package repos
        structure_info = ""
        if report.repo_structure and report.repo_structure.is_multi_package:
            pkg_count = len(report.repo_structure.packages)
            structure_type = report.repo_structure.type.value.title()
            structure_info = f"\n[bold]Structure:[/bold] {structure_type} ({pkg_count} packages detected)"

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Repository:[/bold] {report.repo_path}\n"
                f"[bold]Languages:[/bold] {languages}\n"
                f"[bold]Scanned:[/bold] {report.timestamp}\n"
                f"[bold]Duration:[/bold] {report.scan_duration_ms:.1f}ms{structure_info}",
                title="[bold blue]Agent Readiness Scan[/bold blue]",
                border_style="blue",
            )
        )

    def _print_package_table(self, report: ScanReport) -> None:
        """Print per-package scores table."""
        table = Table(title="Per-Package Scores", show_header=True)
        table.add_column("Package", style="cyan", width=24)
        table.add_column("Languages", width=16)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Key Findings", width=36)

        for ps in sorted(report.package_scores, key=lambda x: x.score, reverse=True):
            score_color = self._get_score_color(ps.score)
            langs = ", ".join(sorted(l.value.upper()[:2] for l in ps.package.languages)[:3])
            if len(ps.package.languages) > 3:
                langs += "..."

            # Build key findings summary
            findings_parts = []
            if ps.package.has_lockfile:
                findings_parts.append("[green]✓[/green] lockfile")
            else:
                findings_parts.append("[red]✗[/red] lockfile")

            if ps.package.has_tests:
                findings_parts.append("[green]✓[/green] tests")
            else:
                findings_parts.append("[red]✗[/red] tests")

            if ps.package.has_types:
                findings_parts.append("[green]✓[/green] types")
            else:
                findings_parts.append("[red]✗[/red] types")

            findings_str = " ".join(findings_parts)

            table.add_row(
                str(ps.package.path) + "/" if str(ps.package.path) != "." else "(root)",
                langs,
                f"[{score_color}]{ps.score:.0f}[/{score_color}]",
                findings_str,
            )

        self.console.print()
        self.console.print(table)

    def _print_shared_infrastructure(self, report: ScanReport) -> None:
        """Print shared infrastructure table."""
        if not report.shared_infra:
            return

        table = Table(title="Shared Infrastructure", show_header=True)
        table.add_column("Check", style="cyan", width=32)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Path", width=36)

        # Deduplicate by name (same config can match multiple patterns)
        seen_names: set[str] = set()
        for si in report.shared_infra:
            if si.name in seen_names:
                continue
            seen_names.add(si.name)

            status = "[green]✓[/green]" if si.found else "[red]✗[/red]"
            path = str(si.path) if si.path else "-"

            table.add_row(si.name, status, path)

        self.console.print()
        self.console.print(table)

    def _print_category_table(self, report: ScanReport) -> None:
        """Print category scores as a table."""
        table = Table(title="Category Scores", show_header=True)
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Weight", justify="right", width=8)
        table.add_column("Weighted", justify="right", width=10)
        table.add_column("Progress", width=12)
        table.add_column("Found", justify="center", width=10)

        for cs in sorted(report.category_scores, key=lambda x: x.category.value):
            score_color = self._get_score_color(cs.score)
            progress_bar = self._create_progress_bar(cs.score)

            table.add_row(
                cs.category.value.replace("_", " ").title(),
                f"[{score_color}]{cs.score:.0f}[/{score_color}]",
                f"{cs.weight * 100:.0f}%",
                f"{cs.weighted_score:.1f}",
                progress_bar,
                f"{cs.found_count}/{cs.total_count}",
            )

        self.console.print()
        self.console.print(table)

    def _print_findings(self, report: ScanReport) -> None:
        """Print detailed findings for each category."""
        self.console.print("\n[bold]Detailed Findings:[/bold]\n")

        for cs in report.category_scores:
            self.console.print(
                f"[bold cyan]{cs.category.value.replace('_', ' ').title()}[/bold cyan]"
            )

            for finding in cs.findings:
                icon = "[green]✓[/green]" if finding.found else "[red]✗[/red]"
                path_info = f" ([dim]{finding.path}[/dim])" if finding.path else ""
                details = f" - {finding.details}" if finding.details else ""
                self.console.print(f"  {icon} {finding.name}{path_info}{details}")

            self.console.print()

    def _print_summary(self, report: ScanReport) -> None:
        """Print final score summary."""
        grade_color = self._get_grade_color(report.grade)
        score_color = self._get_score_color(report.total_score)

        readiness_level = self._get_readiness_level(report.total_score, report.repo_structure)

        summary = Text()
        summary.append("\n")
        summary.append("Final Score: ", style="bold")
        summary.append(f"{report.total_score:.1f}", style=f"bold {score_color}")
        summary.append("/100  ")
        summary.append("Grade: ", style="bold")
        summary.append(report.grade, style=f"bold {grade_color}")
        summary.append(f"\n{readiness_level}", style="dim")

        self.console.print(
            Panel(
                summary,
                title="[bold]Agent Readiness Score[/bold]",
                border_style=grade_color,
            )
        )

    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange1"
        else:
            return "red"

    def _get_grade_color(self, grade: str) -> str:
        """Get color based on grade."""
        return {
            "A": "green",
            "B": "blue",
            "C": "yellow",
            "D": "orange1",
            "F": "red",
        }.get(grade, "white")

    def _create_progress_bar(self, score: float) -> str:
        """Create a text-based progress bar."""
        filled = int(score / PROGRESS_BAR_WIDTH)
        empty = PROGRESS_BAR_WIDTH - filled
        color = self._get_score_color(score)
        return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"

    def _get_readiness_level(self, score: float, repo_structure=None) -> str:
        """Get descriptive readiness level."""
        # Add context for multi-package repos
        suffix = ""
        if repo_structure and repo_structure.is_multi_package:
            if score >= 70:
                suffix = " - good package-level setup"
            else:
                suffix = " - some packages need attention"

        if score >= 90:
            return f"Excellent agent readiness - ready for autonomous development{suffix}"
        elif score >= 80:
            return f"Good agent readiness - minor improvements recommended{suffix}"
        elif score >= 70:
            return f"Moderate agent readiness - several areas need attention{suffix}"
        elif score >= 60:
            return f"Limited agent readiness - significant gaps exist{suffix}"
        else:
            return f"Poor agent readiness - major infrastructure missing{suffix}"
