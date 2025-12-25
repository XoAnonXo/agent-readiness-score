"""Scan engine that orchestrates all scanners with language and package detection."""

import time
from datetime import datetime, timezone
from pathlib import Path

from agent_readiness_score.core.models import (
    ScanReport, CategoryScore, Finding, PackageScore, SharedInfraFinding,
    RepoStructure, Package, calculate_grade, CATEGORY_WEIGHTS,
)
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import detect_languages, LanguageStats, Language
from agent_readiness_score.core.detector import detect_repo_structure, SHARED_CONFIGS


# Shared infrastructure bonus weight
SHARED_CONFIG_WEIGHT = 2.0

# Critical missing penalty
CRITICAL_PENALTY = 5.0

# Directories to exclude from scanning (performance optimization)
EXCLUDED_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "target", ".next", ".nuxt", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
    ".cargo", ".rustup", "Pods", ".gradle", ".idea", ".vscode",
    ".turbo", ".vercel", ".netlify", "out", ".output",
}


class ScanEngine:
    """Orchestrates the scanning process across all categories."""

    def __init__(self, registry: type[ScannerRegistry] | None = None):
        self.registry = registry or ScannerRegistry

    def scan(self, repo_path: Path) -> ScanReport:
        """Scan a repository and generate a complete report.

        For polyrepo/monorepo structures, scans each package independently
        and aggregates scores with shared infrastructure bonuses.

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

        # Detect repository structure (single, monorepo, polyrepo)
        repo_structure = detect_repo_structure(repo_path)

        # Detect languages at root level
        lang_stats = detect_languages(repo_path)

        # Check shared infrastructure
        shared_infra = self._check_shared_infrastructure(repo_path)

        # Run scanning based on repo structure
        if repo_structure.is_multi_package and repo_structure.packages:
            # Per-package scanning for multi-package repos
            package_scores = self._scan_packages(repo_path, repo_structure.packages)
            category_scores = self._aggregate_package_scores(
                repo_path, repo_structure, package_scores, shared_infra, lang_stats
            )
            total_score = self._calculate_multi_package_score(
                package_scores, shared_infra, repo_path
            )
        else:
            # Standard scanning for single-package repos
            package_scores = []
            category_scores = []
            for scanner in self.registry.get_all():
                score = scanner.scan(repo_path, lang_stats)
                category_scores.append(score)
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
            repo_structure=repo_structure,
            package_scores=package_scores,
            shared_infra=shared_infra,
        )

    def _scan_packages(
        self, repo_path: Path, packages: list[Package]
    ) -> list[PackageScore]:
        """Scan each package independently."""
        package_scores: list[PackageScore] = []

        for pkg in packages:
            pkg_path = repo_path / pkg.path if pkg.path != Path(".") else repo_path

            # Create language stats for this package
            pkg_lang_stats = LanguageStats()
            for lang in pkg.languages:
                pkg_lang_stats.add_language(lang, 1000)  # Approximate

            # Run scanners on this package
            pkg_findings: list[Finding] = []
            total_weight = 0.0
            weighted_found = 0.0

            for scanner in self.registry.get_all():
                checks = scanner.get_checks(pkg_lang_stats)
                for check_tuple in checks:
                    # Handle both formats
                    if len(check_tuple) == 4:
                        check_name, patterns, weight, applicable_langs = check_tuple
                        scope = "any"
                    else:
                        check_name, patterns, weight, applicable_langs, scope, _ = check_tuple

                    # Skip root-only checks for package scanning
                    if scope == "root":
                        continue

                    # Skip checks that don't apply to this package's languages
                    if applicable_langs is not None:
                        if not any(lang in pkg.languages for lang in applicable_langs):
                            continue

                    # Search in package directory
                    found_path = self._find_in_package(pkg_path, repo_path, patterns)

                    pkg_findings.append(Finding(
                        name=check_name,
                        found=found_path is not None,
                        path=found_path,
                        weight=weight,
                    ))

                    total_weight += weight
                    if found_path is not None:
                        weighted_found += weight

            # Calculate package score
            if total_weight > 0:
                pkg_score = (weighted_found / total_weight) * 100
            else:
                pkg_score = 0.0

            package_scores.append(PackageScore(
                package=pkg,
                score=pkg_score,
                findings=pkg_findings,
            ))

        return package_scores

    def _find_in_package(
        self, pkg_path: Path, repo_path: Path, patterns: list[str]
    ) -> Path | None:
        """Find a file matching patterns within a package, including subdirs and root."""
        # First check in package directory (direct patterns)
        for pattern in patterns:
            if "**" not in pattern:
                # Direct pattern - check package root
                for match in pkg_path.glob(pattern):
                    if not self._is_excluded(match):
                        try:
                            return match.relative_to(repo_path)
                        except ValueError:
                            return match

        # Check subdirectories within package (max 2 levels deep for performance)
        for pattern in patterns:
            if "**" in pattern:
                continue  # Skip recursive patterns, handle manually
            # Search in immediate subdirs
            result = self._search_with_depth(pkg_path, pattern, repo_path, max_depth=2)
            if result:
                return result

        # Also check root for shared configs
        for pattern in patterns:
            if "**" not in pattern:
                for match in repo_path.glob(pattern):
                    if not self._is_excluded(match):
                        try:
                            return match.relative_to(repo_path)
                        except ValueError:
                            return match

        return None

    def _search_with_depth(
        self, base_path: Path, pattern: str, repo_path: Path, max_depth: int = 2
    ) -> Path | None:
        """Search for pattern in base_path and subdirs up to max_depth."""
        # Check base first
        for match in base_path.glob(pattern):
            if not self._is_excluded(match):
                try:
                    return match.relative_to(repo_path)
                except ValueError:
                    return match

        # Check subdirectories
        if max_depth > 0:
            try:
                for subdir in base_path.iterdir():
                    if subdir.is_dir() and subdir.name not in EXCLUDED_DIRS:
                        result = self._search_with_depth(
                            subdir, pattern, repo_path, max_depth - 1
                        )
                        if result:
                            return result
            except PermissionError:
                pass

        return None

    def _is_excluded(self, path: Path) -> bool:
        """Check if path is in an excluded directory."""
        return any(excluded in path.parts for excluded in EXCLUDED_DIRS)

    def _check_shared_infrastructure(self, repo_path: Path) -> list[SharedInfraFinding]:
        """Check for shared infrastructure at repo root."""
        findings: list[SharedInfraFinding] = []

        for config_pattern, name in SHARED_CONFIGS:
            if config_pattern.endswith("/"):
                # Directory check
                dir_path = repo_path / config_pattern.rstrip("/")
                found = dir_path.is_dir()
                path = Path(config_pattern.rstrip("/")) if found else None
            else:
                # File check
                file_path = repo_path / config_pattern
                found = file_path.exists()
                path = Path(config_pattern) if found else None

            findings.append(SharedInfraFinding(
                name=name,
                found=found,
                path=path,
            ))

        return findings

    def _aggregate_package_scores(
        self,
        repo_path: Path,
        repo_structure: RepoStructure,
        package_scores: list[PackageScore],
        shared_infra: list[SharedInfraFinding],
        lang_stats: LanguageStats,
    ) -> list[CategoryScore]:
        """Aggregate package scores into category scores for display."""
        # For multi-package repos, we still want category breakdown
        # Run standard scanning but with awareness of packages
        category_scores = []

        for scanner in self.registry.get_all():
            # Combine findings from all packages for this category
            all_findings: list[Finding] = []
            checks = scanner.get_checks(lang_stats)

            for check_tuple in checks:
                if len(check_tuple) == 4:
                    check_name, patterns, weight, applicable_langs = check_tuple
                    scope = "any"
                else:
                    check_name, patterns, weight, applicable_langs, scope, _ = check_tuple

                # Handle scope-based searching
                found_path = None

                if scope == "root":
                    # Only check root
                    found_path = self._find_at_root(repo_path, patterns)
                elif scope == "package":
                    # Check all packages
                    for pkg in repo_structure.packages:
                        pkg_path = repo_path / pkg.path if pkg.path != Path(".") else repo_path
                        # Check language applicability
                        if applicable_langs is not None:
                            if not any(lang in pkg.languages for lang in applicable_langs):
                                continue
                        found_path = self._find_at_root(pkg_path, patterns)
                        if found_path:
                            break
                else:  # scope == "any"
                    # Check root first, then packages
                    found_path = self._find_at_root(repo_path, patterns)
                    if not found_path:
                        for pkg in repo_structure.packages:
                            pkg_path = repo_path / pkg.path if pkg.path != Path(".") else repo_path
                            if applicable_langs is not None:
                                if not any(lang in pkg.languages for lang in applicable_langs):
                                    continue
                            found_path = self._find_at_root(pkg_path, patterns)
                            if found_path:
                                try:
                                    found_path = found_path.relative_to(repo_path)
                                except ValueError:
                                    pass
                                break

                # Skip checks that don't apply
                if applicable_langs is not None and lang_stats is not None:
                    if not any(lang_stats.has_language(lang) for lang in applicable_langs):
                        continue

                all_findings.append(Finding(
                    name=check_name,
                    found=found_path is not None,
                    path=found_path,
                    weight=weight,
                ))

            # Calculate category score
            total_weight = sum(f.weight for f in all_findings)
            if total_weight > 0:
                weighted_found = sum(f.weight for f in all_findings if f.found)
                score = (weighted_found / total_weight) * 100
            else:
                score = 0.0

            category_weight = CATEGORY_WEIGHTS[scanner.category]

            category_scores.append(CategoryScore(
                category=scanner.category,
                score=score,
                weight=category_weight,
                weighted_score=score * category_weight,
                findings=all_findings,
            ))

        return category_scores

    def _find_at_root(self, path: Path, patterns: list[str], max_depth: int = 2) -> Path | None:
        """Find a file matching patterns at a specific path with limited recursion."""
        # Check direct patterns first
        for pattern in patterns:
            if "**" not in pattern:
                for match in path.glob(pattern):
                    if not self._is_excluded(match):
                        return match

        # Search subdirs with depth limit
        for pattern in patterns:
            if "**" not in pattern:
                result = self._search_with_depth(path, pattern, path, max_depth=max_depth)
                if result:
                    return result

        return None

    def _calculate_multi_package_score(
        self,
        package_scores: list[PackageScore],
        shared_infra: list[SharedInfraFinding],
        repo_path: Path,
    ) -> float:
        """Calculate overall score for multi-package repositories."""
        if not package_scores:
            return 0.0

        # Base: weighted average of package scores
        total_weight = sum(ps.weight for ps in package_scores)
        if total_weight > 0:
            base_score = sum(ps.score * ps.weight for ps in package_scores) / total_weight
        else:
            base_score = sum(ps.score for ps in package_scores) / len(package_scores)

        # Bonus: shared configs that benefit all packages
        shared_found = sum(1 for si in shared_infra if si.found)
        shared_bonus = min(shared_found * SHARED_CONFIG_WEIGHT, 15.0)  # Cap at 15 points

        # Penalty: critical missing items
        critical_missing = 0
        # Check for README
        if not (repo_path / "README.md").exists():
            critical_missing += 1
        # Check for CI
        if not (repo_path / ".github" / "workflows").is_dir():
            if not list(repo_path.glob(".github/workflows/*.yml")):
                critical_missing += 1

        critical_penalty = critical_missing * CRITICAL_PENALTY

        return min(100.0, max(0.0, base_score + shared_bonus - critical_penalty))
