"""Data models for agent-ready."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from agent_readiness_score.core.language import Language


class RepoType(str, Enum):
    """Type of repository structure."""
    SINGLE = "single"
    MONOREPO = "monorepo"
    POLYREPO = "polyrepo"


class CheckScope(str, Enum):
    """Where a check should look for files."""
    ROOT = "root"      # Only at repo root
    PACKAGE = "package"  # Only within packages
    ANY = "any"        # Root or package level


@dataclass
class Package:
    """A detected package/workspace within a repository."""
    path: Path
    name: str
    languages: set["Language"] = field(default_factory=set)
    package_manager: str | None = None
    has_tests: bool = False
    has_lockfile: bool = False
    has_types: bool = False
    line_count: int = 0  # For weighting

    @property
    def weight(self) -> float:
        """Weight for aggregation based on size/importance."""
        if self.line_count > 10000:
            return 2.0
        elif self.line_count > 1000:
            return 1.5
        return 1.0


@dataclass
class RepoStructure:
    """Detected repository structure."""
    type: RepoType
    packages: list[Package] = field(default_factory=list)
    root_configs: list[Path] = field(default_factory=list)
    root_languages: set["Language"] = field(default_factory=set)

    @property
    def is_multi_package(self) -> bool:
        return self.type in (RepoType.MONOREPO, RepoType.POLYREPO)

    @property
    def all_languages(self) -> set["Language"]:
        """Get all languages across all packages."""
        langs = set(self.root_languages)
        for pkg in self.packages:
            langs.update(pkg.languages)
        return langs


@dataclass
class PackageScore:
    """Score for a single package."""
    package: Package
    score: float
    findings: list["Finding"] = field(default_factory=list)

    @property
    def weight(self) -> float:
        return self.package.weight


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
class SharedInfraFinding:
    """A finding for shared infrastructure at repo root."""
    name: str
    found: bool
    path: Path | None = None


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
    repo_structure: RepoStructure | None = None
    package_scores: list[PackageScore] = field(default_factory=list)
    shared_infra: list[SharedInfraFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
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

        # Add repo structure info if available
        if self.repo_structure:
            result["repo_structure"] = {
                "type": self.repo_structure.type.value,
                "package_count": len(self.repo_structure.packages),
                "packages": [
                    {
                        "name": pkg.name,
                        "path": str(pkg.path),
                        "languages": [l.value for l in pkg.languages],
                        "package_manager": pkg.package_manager,
                    }
                    for pkg in self.repo_structure.packages
                ],
            }

        # Add package scores if available
        if self.package_scores:
            result["package_scores"] = [
                {
                    "name": ps.package.name,
                    "path": str(ps.package.path),
                    "score": round(ps.score, 1),
                    "languages": [l.value for l in ps.package.languages],
                }
                for ps in self.package_scores
            ]

        # Add shared infrastructure
        if self.shared_infra:
            result["shared_infrastructure"] = [
                {
                    "name": si.name,
                    "found": si.found,
                    "path": str(si.path) if si.path else None,
                }
                for si in self.shared_infra
            ]

        return result


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
