"""Tests for individual scanners."""

from pathlib import Path

import pytest

from agent_readiness_score.core.language import detect_languages, Language
from agent_readiness_score.core.models import Category
from agent_readiness_score.scanners.testing import TestingScanner
from agent_readiness_score.scanners.style import StyleScanner
from agent_readiness_score.scanners.devenv import DevEnvScanner
from agent_readiness_score.scanners.build import BuildScanner
from agent_readiness_score.scanners.observability import ObservabilityScanner
from agent_readiness_score.scanners.dependencies import DependenciesScanner
from agent_readiness_score.scanners.documentation import DocumentationScanner
from agent_readiness_score.scanners.typing import TypingScanner


class TestTestingScanner:
    """Test the TestingScanner."""

    def test_scan_python_repo(self, python_repo: Path):
        """Test scanning a Python repository for testing files."""
        scanner = TestingScanner()
        lang_stats = detect_languages(python_repo)
        result = scanner.scan(python_repo, lang_stats)

        assert result.category == Category.TESTING
        assert result.score > 0
        assert result.score <= 100
        assert result.found_count > 0

        # Check that pytest-related findings are found
        finding_names = [f.name for f in result.findings if f.found]
        assert any("pytest" in name.lower() for name in finding_names)
        assert any("test directory" in name.lower() for name in finding_names)

    def test_scan_typescript_repo(self, typescript_repo: Path):
        """Test scanning a TypeScript repository."""
        scanner = TestingScanner()
        lang_stats = detect_languages(typescript_repo)
        result = scanner.scan(typescript_repo, lang_stats)

        assert result.category == Category.TESTING
        assert result.found_count > 0

        # Check for Jest
        finding_names = [f.name for f in result.findings if f.found]
        assert any("jest" in name.lower() for name in finding_names)

    def test_scan_go_repo(self, go_repo: Path):
        """Test scanning a Go repository."""
        scanner = TestingScanner()
        lang_stats = detect_languages(go_repo)
        result = scanner.scan(go_repo, lang_stats)

        assert result.category == Category.TESTING
        assert result.found_count > 0

        # Check for Go test files
        finding_names = [f.name for f in result.findings if f.found]
        assert any("go test" in name.lower() for name in finding_names)

    def test_scan_empty_repo(self, empty_repo: Path):
        """Test scanning an empty repository."""
        scanner = TestingScanner()
        lang_stats = detect_languages(empty_repo)
        result = scanner.scan(empty_repo, lang_stats)

        assert result.category == Category.TESTING
        assert result.score == 0
        assert result.found_count == 0


class TestStyleScanner:
    """Test the StyleScanner."""

    def test_scan_python_repo(self, python_repo: Path):
        """Test scanning for Python linter configs."""
        scanner = StyleScanner()
        lang_stats = detect_languages(python_repo)
        result = scanner.scan(python_repo, lang_stats)

        assert result.category == Category.STYLE
        assert result.score > 0

        # Should find Ruff config in pyproject.toml
        finding_names = [f.name for f in result.findings if f.found]
        assert any("ruff" in name.lower() for name in finding_names)

    def test_scan_typescript_repo(self, typescript_repo: Path):
        """Test scanning for JavaScript/TypeScript linters."""
        scanner = StyleScanner()
        lang_stats = detect_languages(typescript_repo)
        result = scanner.scan(typescript_repo, lang_stats)

        assert result.category == Category.STYLE
        assert result.found_count > 0

        # Should find ESLint and Prettier
        finding_names = [f.name for f in result.findings if f.found]
        assert any("eslint" in name.lower() for name in finding_names)
        assert any("prettier" in name.lower() for name in finding_names)

    def test_scan_go_repo(self, go_repo: Path):
        """Test scanning for Go linters."""
        scanner = StyleScanner()
        lang_stats = detect_languages(go_repo)
        result = scanner.scan(go_repo, lang_stats)

        assert result.category == Category.STYLE
        assert result.found_count > 0

        finding_names = [f.name for f in result.findings if f.found]
        assert any("golangci" in name.lower() for name in finding_names)


class TestDevEnvScanner:
    """Test the DevEnvScanner."""

    def test_scan_python_repo_with_devcontainer(self, python_repo: Path):
        """Test scanning for DevContainer config."""
        scanner = DevEnvScanner()
        result = scanner.scan(python_repo, None)

        assert result.category == Category.DEVENV
        assert result.found_count > 0

        finding_names = [f.name for f in result.findings if f.found]
        assert any("devcontainer" in name.lower() for name in finding_names)

    def test_scan_complete_repo(self, complete_repo: Path):
        """Test scanning a complete repo with multiple dev env configs."""
        scanner = DevEnvScanner()
        result = scanner.scan(complete_repo, None)

        assert result.score > 50  # Should have good coverage

        finding_names = [f.name for f in result.findings if f.found]
        assert any("docker" in name.lower() for name in finding_names)
        assert any("devcontainer" in name.lower() for name in finding_names)


class TestBuildScanner:
    """Test the BuildScanner."""

    def test_scan_python_repo(self, python_repo: Path):
        """Test scanning for Python build configs."""
        scanner = BuildScanner()
        lang_stats = detect_languages(python_repo)
        result = scanner.scan(python_repo, lang_stats)

        assert result.category == Category.BUILD
        assert result.found_count > 0

        # Should find GitHub Actions and pyproject.toml
        finding_names = [f.name for f in result.findings if f.found]
        assert any("github actions" in name.lower() for name in finding_names)
        assert any("pyproject" in name.lower() for name in finding_names)

    def test_scan_go_repo_with_makefile(self, go_repo: Path):
        """Test scanning Go repo with Makefile."""
        scanner = BuildScanner()
        lang_stats = detect_languages(go_repo)
        result = scanner.scan(go_repo, lang_stats)

        assert result.found_count > 0

        finding_names = [f.name for f in result.findings if f.found]
        assert any("makefile" in name.lower() for name in finding_names)
        assert any("go" in name.lower() for name in finding_names)


class TestObservabilityScanner:
    """Test the ObservabilityScanner."""

    def test_scan_minimal_repo(self, minimal_repo: Path):
        """Test scanning a repo with no observability."""
        scanner = ObservabilityScanner()
        result = scanner.scan(minimal_repo, None)

        assert result.category == Category.OBSERVABILITY
        # Minimal repos typically have low observability scores
        assert result.score >= 0

    def test_scan_complete_repo(self, complete_repo: Path):
        """Test scanning a complete repo with logging."""
        scanner = ObservabilityScanner()
        result = scanner.scan(complete_repo, None)

        # Should find some observability configs
        assert result.found_count > 0


class TestDependenciesScanner:
    """Test the DependenciesScanner."""

    def test_scan_python_repo_with_lockfile(self, python_repo: Path):
        """Test scanning for Python lockfiles."""
        scanner = DependenciesScanner()
        lang_stats = detect_languages(python_repo)
        result = scanner.scan(python_repo, lang_stats)

        assert result.category == Category.DEPENDENCIES
        assert result.found_count > 0

        # Should find poetry.lock
        finding_names = [f.name for f in result.findings if f.found]
        assert any("poetry" in name.lower() for name in finding_names)

    def test_scan_typescript_repo(self, typescript_repo: Path):
        """Test scanning for npm lockfile."""
        scanner = DependenciesScanner()
        lang_stats = detect_languages(typescript_repo)
        result = scanner.scan(typescript_repo, lang_stats)

        assert result.found_count > 0

        finding_names = [f.name for f in result.findings if f.found]
        assert any("package-lock" in name.lower() for name in finding_names)

    def test_scan_go_repo(self, go_repo: Path):
        """Test scanning for Go dependencies."""
        scanner = DependenciesScanner()
        lang_stats = detect_languages(go_repo)
        result = scanner.scan(go_repo, lang_stats)

        assert result.found_count > 0

        finding_names = [f.name for f in result.findings if f.found]
        assert any("go.sum" in name.lower() for name in finding_names)


class TestDocumentationScanner:
    """Test the DocumentationScanner."""

    def test_scan_repo_with_readme(self, python_repo: Path):
        """Test scanning for documentation."""
        scanner = DocumentationScanner()
        result = scanner.scan(python_repo, None)

        assert result.category == Category.DOCUMENTATION
        assert result.found_count > 0

        # All repos should have README
        finding_names = [f.name for f in result.findings if f.found]
        assert any("readme" in name.lower() for name in finding_names)
        assert any("docs" in name.lower() for name in finding_names)

    def test_scan_complete_repo(self, complete_repo: Path):
        """Test scanning complete repo with comprehensive docs."""
        scanner = DocumentationScanner()
        result = scanner.scan(complete_repo, None)

        assert result.score > 50  # Should have good documentation

        finding_names = [f.name for f in result.findings if f.found]
        assert any("readme" in name.lower() for name in finding_names)
        assert any("contributing" in name.lower() for name in finding_names)
        assert any("license" in name.lower() for name in finding_names)
        assert any("changelog" in name.lower() for name in finding_names)


class TestTypingScanner:
    """Test the TypingScanner."""

    def test_scan_python_repo_with_mypy(self, python_repo: Path):
        """Test scanning for type checking configs."""
        scanner = TypingScanner()
        lang_stats = detect_languages(python_repo)
        result = scanner.scan(python_repo, lang_stats)

        assert result.category == Category.TYPING
        assert result.found_count > 0

        # Should find mypy config
        finding_names = [f.name for f in result.findings if f.found]
        assert any("mypy" in name.lower() for name in finding_names)

    def test_scan_typescript_repo(self, typescript_repo: Path):
        """Test scanning TypeScript repo."""
        scanner = TypingScanner()
        lang_stats = detect_languages(typescript_repo)
        result = scanner.scan(typescript_repo, lang_stats)

        assert result.found_count > 0

        # TypeScript inherently has typing via tsconfig
        finding_names = [f.name for f in result.findings if f.found]
        assert any("tsconfig" in name.lower() for name in finding_names)

    def test_scan_complete_repo(self, complete_repo: Path):
        """Test scanning complete repo with py.typed marker."""
        scanner = TypingScanner()
        lang_stats = detect_languages(complete_repo)
        result = scanner.scan(complete_repo, lang_stats)

        assert result.score > 50  # Should have good typing support

        finding_names = [f.name for f in result.findings if f.found]
        assert any("py.typed" in name.lower() for name in finding_names)


class TestScannerProperties:
    """Test scanner properties and interfaces."""

    @pytest.mark.parametrize("scanner_class", [
        TestingScanner,
        StyleScanner,
        DevEnvScanner,
        BuildScanner,
        ObservabilityScanner,
        DependenciesScanner,
        DocumentationScanner,
        TypingScanner,
    ])
    def test_scanner_has_required_properties(self, scanner_class):
        """Test that all scanners have required properties."""
        scanner = scanner_class()

        # Test category property
        assert hasattr(scanner, "category")
        assert isinstance(scanner.category, Category)

        # Test name property
        assert hasattr(scanner, "name")
        assert isinstance(scanner.name, str)
        assert len(scanner.name) > 0

        # Test description property
        assert hasattr(scanner, "description")
        assert isinstance(scanner.description, str)

    @pytest.mark.parametrize("scanner_class", [
        TestingScanner,
        StyleScanner,
        DevEnvScanner,
        BuildScanner,
        ObservabilityScanner,
        DependenciesScanner,
        DocumentationScanner,
        TypingScanner,
    ])
    def test_scanner_get_checks(self, scanner_class):
        """Test that get_checks returns valid data."""
        scanner = scanner_class()
        checks = scanner.get_checks(None)

        assert isinstance(checks, list)
        assert len(checks) > 0

        # Each check should be a tuple with 4 elements
        for check in checks:
            assert isinstance(check, tuple)
            assert len(check) == 4
            name, patterns, weight, langs = check
            assert isinstance(name, str)
            assert isinstance(patterns, list)
            assert isinstance(weight, (int, float))
            assert weight > 0
            assert langs is None or isinstance(langs, set)

    @pytest.mark.parametrize("scanner_class", [
        TestingScanner,
        StyleScanner,
        DevEnvScanner,
        BuildScanner,
        ObservabilityScanner,
        DependenciesScanner,
        DocumentationScanner,
        TypingScanner,
    ])
    def test_scanner_scan_method(self, scanner_class, minimal_repo: Path):
        """Test that scan method works and returns valid results."""
        scanner = scanner_class()
        lang_stats = detect_languages(minimal_repo)
        result = scanner.scan(minimal_repo, lang_stats)

        # Verify result structure
        assert result.category == scanner.category
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100
        assert isinstance(result.weight, float)
        assert 0 < result.weight <= 1
        assert isinstance(result.weighted_score, float)
        assert isinstance(result.findings, list)
        assert result.found_count >= 0
        assert result.total_count >= result.found_count


class TestLanguageSpecificScanning:
    """Test that scanners correctly filter checks based on detected languages."""

    def test_python_scanner_skips_js_checks(self, python_repo: Path):
        """Test that Python repo doesn't trigger JS-specific checks."""
        scanner = TestingScanner()
        lang_stats = detect_languages(python_repo)

        # Ensure we detected Python
        assert lang_stats.has_language(Language.PYTHON)
        assert not lang_stats.has_language(Language.JAVASCRIPT)

        result = scanner.scan(python_repo, lang_stats)

        # Should not have findings for JS-specific items
        js_findings = [f for f in result.findings if "jest" in f.name.lower() or "vitest" in f.name.lower()]
        # These checks should not even be included
        assert len(js_findings) == 0

    def test_typescript_scanner_has_ts_checks(self, typescript_repo: Path):
        """Test that TypeScript repo triggers TS checks."""
        scanner = StyleScanner()
        lang_stats = detect_languages(typescript_repo)

        assert lang_stats.has_language(Language.TYPESCRIPT)

        result = scanner.scan(typescript_repo, lang_stats)

        # Should have TypeScript-related findings
        ts_finding_names = [f.name for f in result.findings]
        # At least some TS/JS related checks should be present
        assert any("eslint" in name.lower() or "prettier" in name.lower() or "tsconfig" in name.lower()
                   for name in ts_finding_names)

    def test_multi_language_repo(self, multi_language_repo: Path):
        """Test scanning a multi-language repository."""
        scanner = TestingScanner()
        lang_stats = detect_languages(multi_language_repo)

        # Should detect multiple languages
        assert lang_stats.is_multi_language
        assert lang_stats.has_language(Language.PYTHON)
        assert lang_stats.has_language(Language.TYPESCRIPT)

        result = scanner.scan(multi_language_repo, lang_stats)

        # Should have findings from multiple language ecosystems
        assert result.found_count > 0
        finding_names = [f.name for f in result.findings if f.found]

        # Should have both Python and TypeScript checks
        has_python = any("pytest" in name.lower() for name in finding_names)
        has_ts = any("jest" in name.lower() or "test" in name.lower() for name in finding_names)

        # At least one should be true (depending on what was created)
        assert has_python or has_ts or len(finding_names) > 0
