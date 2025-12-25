"""Scanner protocol and base implementation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable

from agent_readiness_score.core.models import Category, CategoryScore, Finding, CATEGORY_WEIGHTS
from agent_readiness_score.core.language import Language, LanguageStats

# Directories to skip during scanning (performance optimization)
EXCLUDED_DIRS = {
    "node_modules", ".git", ".venv", "venv", "env", "__pycache__",
    "dist", "build", "target", ".next", ".nuxt", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
    ".cargo", ".rustup", "Pods", ".gradle", ".idea", ".vscode",
}


@runtime_checkable
class Scanner(Protocol):
    """Protocol defining the scanner interface."""

    @property
    def category(self) -> Category:
        """The category this scanner evaluates."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name for the scanner."""
        ...

    @property
    def description(self) -> str:
        """Description of what this scanner checks."""
        ...

    def scan(self, repo_path: Path, lang_stats: LanguageStats | None = None) -> CategoryScore:
        """Scan the repository and return a category score."""
        ...


class BaseScanner(ABC):
    """Abstract base class for scanners with common functionality."""

    @property
    @abstractmethod
    def category(self) -> Category:
        """The category this scanner evaluates."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for the scanner."""
        pass

    @property
    def description(self) -> str:
        """Description of what this scanner checks."""
        return f"Scans for {self.category.value} indicators"

    @abstractmethod
    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[tuple[str, list[str], float, set[Language] | None]]:
        """Return list of checks: (name, file_patterns, weight, applicable_languages).

        If applicable_languages is None, the check applies to all languages.
        If it's a set, the check only applies (and counts) if the repo uses those languages.
        """
        pass

    def scan(self, repo_path: Path, lang_stats: LanguageStats | None = None) -> CategoryScore:
        """Execute all checks and calculate category score."""
        findings = self._run_standard_checks(repo_path, lang_stats)
        return self._calculate_category_score(findings)

    def _run_standard_checks(
        self, repo_path: Path, lang_stats: LanguageStats | None = None
    ) -> list[Finding]:
        """Run all standard checks and return findings.

        Subclasses can call this and extend the findings list with custom checks.
        """
        findings: list[Finding] = []
        checks = self.get_checks(lang_stats)

        for check_tuple in checks:
            # Handle both old 4-tuple and new 6-tuple format
            if len(check_tuple) == 4:
                check_name, patterns, weight, applicable_langs = check_tuple
                scope, critical = "any", False
            else:
                check_name, patterns, weight, applicable_langs, scope, critical = check_tuple

            # Skip checks that don't apply to this repo's languages
            if applicable_langs is not None and lang_stats is not None:
                if not any(lang_stats.has_language(lang) for lang in applicable_langs):
                    continue  # Skip this check entirely

            found_path = self._find_first_match(repo_path, patterns)
            findings.append(
                Finding(
                    name=check_name,
                    found=found_path is not None,
                    path=found_path,
                    weight=weight,
                )
            )

        return findings

    def _calculate_category_score(self, findings: list[Finding]) -> CategoryScore:
        """Calculate category score from findings.

        Subclasses that override scan() should use this method
        to maintain consistent score calculation.
        """
        total_weight = sum(f.weight for f in findings)
        if total_weight > 0:
            weighted_found = sum(f.weight for f in findings if f.found)
            score = (weighted_found / total_weight) * 100
        else:
            score = 0.0

        category_weight = CATEGORY_WEIGHTS[self.category]

        return CategoryScore(
            category=self.category,
            score=score,
            weight=category_weight,
            weighted_score=score * category_weight,
            findings=findings,
        )

    def _find_first_match(self, repo_path: Path, patterns: list[str]) -> Path | None:
        """Find the first file matching any of the patterns.

        Searches root level first, then subdirectories for polyrepo/monorepo support.
        Excludes node_modules, .git, and other heavy directories for performance.
        """
        # First pass: check root level and explicit patterns
        for pattern in patterns:
            for match in repo_path.glob(pattern):
                if not self._is_excluded(match):
                    try:
                        return match.relative_to(repo_path)
                    except ValueError:
                        return match

        # Second pass: recursive search in subdirectories
        # Skip patterns that already have ** or are directories
        for pattern in patterns:
            if "**" in pattern or pattern.endswith("/"):
                continue
            # Try recursive pattern with exclusion filtering
            recursive_pattern = f"**/{pattern}"
            for match in repo_path.glob(recursive_pattern):
                if not self._is_excluded(match):
                    try:
                        return match.relative_to(repo_path)
                    except ValueError:
                        return match

        return None

    def _is_excluded(self, path: Path) -> bool:
        """Check if path is in an excluded directory."""
        return any(excluded in path.parts for excluded in EXCLUDED_DIRS)


# Type alias for check tuples
# (name, patterns, weight, applicable_languages, scope, critical)
Check = tuple[str, list[str], float, set[Language] | None, str, bool]


def check(
    name: str,
    patterns: list[str],
    weight: float = 1.0,
    langs: set[Language] | None = None,
    scope: str = "any",
    critical: bool = False,
) -> Check:
    """Helper to create a check tuple with cleaner syntax."""
    return (name, patterns, weight, langs, scope, critical)


def py(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Python-specific check."""
    return (name, list(patterns), weight, {Language.PYTHON}, scope, critical)


def js(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """JavaScript-specific check."""
    return (name, list(patterns), weight, {Language.JAVASCRIPT, Language.TYPESCRIPT}, scope, critical)


def ts(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """TypeScript-specific check."""
    return (name, list(patterns), weight, {Language.TYPESCRIPT}, scope, critical)


def go(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Go-specific check."""
    return (name, list(patterns), weight, {Language.GO}, scope, critical)


def rust(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Rust-specific check."""
    return (name, list(patterns), weight, {Language.RUST}, scope, critical)


def ruby(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Ruby-specific check."""
    return (name, list(patterns), weight, {Language.RUBY}, scope, critical)


def java(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Java-specific check."""
    return (name, list(patterns), weight, {Language.JAVA, Language.KOTLIN}, scope, critical)


def swift(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Swift-specific check."""
    return (name, list(patterns), weight, {Language.SWIFT}, scope, critical)


def csharp(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """C#-specific check."""
    return (name, list(patterns), weight, {Language.CSHARP}, scope, critical)


def cpp(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """C/C++-specific check."""
    return (name, list(patterns), weight, {Language.C, Language.CPP}, scope, critical)


def php(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """PHP-specific check."""
    return (name, list(patterns), weight, {Language.PHP}, scope, critical)


def elixir(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Elixir-specific check."""
    return (name, list(patterns), weight, {Language.ELIXIR}, scope, critical)


def dart(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Dart-specific check."""
    return (name, list(patterns), weight, {Language.DART}, scope, critical)


def universal(*patterns: str, name: str, weight: float = 1.0, scope: str = "any", critical: bool = False) -> Check:
    """Language-agnostic check."""
    return (name, list(patterns), weight, None, scope, critical)


# Convenience functions for root-only checks
def root(*patterns: str, name: str, weight: float = 1.0, critical: bool = False) -> Check:
    """Root-level only check (applies to whole repo)."""
    return (name, list(patterns), weight, None, "root", critical)


def pkg(*patterns: str, name: str, weight: float = 1.0, langs: set[Language] | None = None, critical: bool = False) -> Check:
    """Package-level only check."""
    return (name, list(patterns), weight, langs, "package", critical)
