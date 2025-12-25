"""Scanner protocol and base implementation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable

from agent_readiness_score.core.models import Category, CategoryScore, Finding, CATEGORY_WEIGHTS
from agent_readiness_score.core.language import Language, LanguageStats


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

        for check in checks:
            check_name, patterns, weight, applicable_langs = check

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
        """
        # First pass: check root level and explicit patterns
        for pattern in patterns:
            matches = list(repo_path.glob(pattern))
            if matches:
                try:
                    return matches[0].relative_to(repo_path)
                except ValueError:
                    return matches[0]

        # Second pass: recursive search in subdirectories
        # Skip patterns that already have ** or are directories
        for pattern in patterns:
            if "**" in pattern or pattern.endswith("/"):
                continue
            # Try recursive pattern
            recursive_pattern = f"**/{pattern}"
            matches = list(repo_path.glob(recursive_pattern))
            if matches:
                try:
                    return matches[0].relative_to(repo_path)
                except ValueError:
                    return matches[0]

        return None


# Type alias for check tuples
Check = tuple[str, list[str], float, set[Language] | None]


def check(name: str, patterns: list[str], weight: float = 1.0, langs: set[Language] | None = None) -> Check:
    """Helper to create a check tuple with cleaner syntax."""
    return (name, patterns, weight, langs)


def py(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Python-specific check."""
    return (name, list(patterns), weight, {Language.PYTHON})


def js(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """JavaScript-specific check."""
    return (name, list(patterns), weight, {Language.JAVASCRIPT, Language.TYPESCRIPT})


def ts(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """TypeScript-specific check."""
    return (name, list(patterns), weight, {Language.TYPESCRIPT})


def go(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Go-specific check."""
    return (name, list(patterns), weight, {Language.GO})


def rust(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Rust-specific check."""
    return (name, list(patterns), weight, {Language.RUST})


def ruby(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Ruby-specific check."""
    return (name, list(patterns), weight, {Language.RUBY})


def java(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Java-specific check."""
    return (name, list(patterns), weight, {Language.JAVA, Language.KOTLIN})


def swift(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Swift-specific check."""
    return (name, list(patterns), weight, {Language.SWIFT})


def csharp(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """C#-specific check."""
    return (name, list(patterns), weight, {Language.CSHARP})


def cpp(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """C/C++-specific check."""
    return (name, list(patterns), weight, {Language.C, Language.CPP})


def php(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """PHP-specific check."""
    return (name, list(patterns), weight, {Language.PHP})


def elixir(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Elixir-specific check."""
    return (name, list(patterns), weight, {Language.ELIXIR})


def dart(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Dart-specific check."""
    return (name, list(patterns), weight, {Language.DART})


def universal(*patterns: str, name: str, weight: float = 1.0) -> Check:
    """Language-agnostic check."""
    return (name, list(patterns), weight, None)
