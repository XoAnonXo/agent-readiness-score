"""JSON output formatter."""

import json
from pathlib import Path

from agent_readiness_score.core.models import ScanReport


class JSONFormatter:
    """JSON output formatter."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format(self, report: ScanReport) -> str:
        """Format report as JSON string."""
        return json.dumps(report.to_dict(), indent=self.indent)

    def save(self, report: ScanReport, path: Path) -> None:
        """Save JSON report to file."""
        path.write_text(self.format(report))
