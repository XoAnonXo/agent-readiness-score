"""Scan engine that orchestrates all scanners with language detection."""

import time
from datetime import datetime, timezone
from pathlib import Path

from agent_readiness_score.core.models import ScanReport, calculate_grade
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import detect_languages, LanguageStats


class ScanEngine:
    """Orchestrates the scanning process across all categories."""

    def __init__(self, registry: type[ScannerRegistry] | None = None):
        self.registry = registry or ScannerRegistry

    def scan(self, repo_path: Path) -> ScanReport:
        """Scan a repository and generate a complete report.

        Args:
            repo_path: Path to the repository root.

        Returns:
            Complete ScanReport with all category scores.

        Raises:
            ValueError: If repo_path doesn't exist or isn't a directory.
        """
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        if not repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repo_path}")

        start_time = time.perf_counter()

        # Detect languages in the repository
        lang_stats = detect_languages(repo_path)

        # Run all scanners with language stats
        category_scores = []
        for scanner in self.registry.get_all():
            score = scanner.scan(repo_path, lang_stats)
            category_scores.append(score)

        # Calculate total score
        total_score = sum(cs.weighted_score for cs in category_scores)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ScanReport(
            repo_path=repo_path.resolve(),
            total_score=total_score,
            grade=calculate_grade(total_score),
            category_scores=category_scores,
            scan_duration_ms=elapsed_ms,
            timestamp=datetime.now(timezone.utc).isoformat(),
            detected_languages=[lang.value for lang in lang_stats.primary_languages()],
        )
