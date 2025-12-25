"""Data models for agent-ready."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Category(str, Enum):
    """Scoring categories with their identifiers."""

    STYLE = "style"
    BUILD = "build"
    DEVENV = "devenv"
    OBSERVABILITY = "observability"
    TESTING = "testing"
    DEPENDENCIES = "dependencies"
    DOCUMENTATION = "documentation"
    TYPING = "typing"


# Category weights (must sum to 1.0)
CATEGORY_WEIGHTS: dict[Category, float] = {
    Category.STYLE: 0.15,
    Category.BUILD: 0.10,
    Category.DEVENV: 0.15,
    Category.OBSERVABILITY: 0.10,
    Category.TESTING: 0.20,
    Category.DEPENDENCIES: 0.10,
    Category.DOCUMENTATION: 0.10,
    Category.TYPING: 0.10,
}


@dataclass
class Finding:
    """A single finding from a scanner."""

    name: str
    found: bool
    path: Path | None = None
    details: str | None = None
    weight: float = 1.0


@dataclass
class CategoryScore:
    """Score for a single category."""

    category: Category
    score: float  # 0-100
    weight: float
    weighted_score: float
    findings: list[Finding] = field(default_factory=list)

    @property
    def found_count(self) -> int:
        return sum(1 for f in self.findings if f.found)

    @property
    def total_count(self) -> int:
        return len(self.findings)


@dataclass
class ScanReport:
    """Complete scan report for a repository."""

    repo_path: Path
    total_score: float
    grade: str
    category_scores: list[CategoryScore]
    scan_duration_ms: float
    timestamp: str
    detected_languages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "repo_path": str(self.repo_path),
            "total_score": round(self.total_score, 1),
            "grade": self.grade,
            "detected_languages": self.detected_languages,
            "scan_duration_ms": round(self.scan_duration_ms, 2),
            "timestamp": self.timestamp,
            "categories": [
                {
                    "name": cs.category.value,
                    "score": round(cs.score, 1),
                    "weight": cs.weight,
                    "weighted_score": round(cs.weighted_score, 2),
                    "found": cs.found_count,
                    "total": cs.total_count,
                    "findings": [
                        {
                            "name": f.name,
                            "found": f.found,
                            "path": str(f.path) if f.path else None,
                            "details": f.details,
                        }
                        for f in cs.findings
                    ],
                }
                for cs in self.category_scores
            ],
        }


def calculate_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
