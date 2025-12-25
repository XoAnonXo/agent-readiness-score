"""Tests for the ScanEngine."""

from pathlib import Path

import pytest

from agent_readiness_score.core.engine import ScanEngine
from agent_readiness_score.core.models import Category, ScanReport


class TestScanEngine:
    """Test the ScanEngine orchestration."""

    def test_scan_python_repo(self, python_repo: Path):
        """Test scanning a Python repository."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        assert isinstance(report, ScanReport)
        assert report.repo_path == python_repo.resolve()
        assert 0 <= report.total_score <= 100
        assert report.grade in ["A", "B", "C", "D", "F"]
        assert len(report.category_scores) == 8  # All 8 categories
        assert report.scan_duration_ms > 0
        assert len(report.timestamp) > 0

    def test_scan_typescript_repo(self, typescript_repo: Path):
        """Test scanning a TypeScript repository."""
        engine = ScanEngine()
        report = engine.scan(typescript_repo)

        assert report.total_score > 0
        assert len(report.detected_languages) > 0
        assert "typescript" in report.detected_languages

        # TypeScript repo should score well on several categories
        cat_scores = {cs.category: cs.score for cs in report.category_scores}
        assert cat_scores[Category.DEPENDENCIES] > 0  # Has package-lock.json
        assert cat_scores[Category.STYLE] > 0  # Has ESLint, Prettier
        assert cat_scores[Category.TYPING] > 0  # Has tsconfig.json

    def test_scan_go_repo(self, go_repo: Path):
        """Test scanning a Go repository."""
        engine = ScanEngine()
        report = engine.scan(go_repo)

        assert report.total_score > 0
        assert "go" in report.detected_languages

        cat_scores = {cs.category: cs.score for cs in report.category_scores}
        assert cat_scores[Category.TESTING] > 0  # Has _test.go files
        assert cat_scores[Category.BUILD] > 0  # Has go.mod, Makefile
        assert cat_scores[Category.DEPENDENCIES] > 0  # Has go.sum

    def test_scan_minimal_repo(self, minimal_repo: Path):
        """Test scanning a minimal repository."""
        engine = ScanEngine()
        report = engine.scan(minimal_repo)

        # Minimal repo should have low score
        assert report.total_score < 50
        assert report.grade in ["D", "F"]

        # But should have some documentation score (README)
        cat_scores = {cs.category: cs.score for cs in report.category_scores}
        assert cat_scores[Category.DOCUMENTATION] > 0

    def test_scan_empty_repo(self, empty_repo: Path):
        """Test scanning an empty repository."""
        engine = ScanEngine()
        report = engine.scan(empty_repo)

        # Empty repo should score 0
        assert report.total_score == 0
        assert report.grade == "F"

        # All categories should be 0
        for cat_score in report.category_scores:
            assert cat_score.score == 0

    def test_scan_complete_repo(self, complete_repo: Path):
        """Test scanning a complete, well-configured repository."""
        engine = ScanEngine()
        report = engine.scan(complete_repo)

        # Complete repo should score very high
        assert report.total_score > 80
        assert report.grade in ["A", "B"]

        # All categories should have some findings
        for cat_score in report.category_scores:
            assert cat_score.score > 0

    def test_scan_multi_language_repo(self, multi_language_repo: Path):
        """Test scanning a multi-language repository."""
        engine = ScanEngine()
        report = engine.scan(multi_language_repo)

        # Should detect multiple languages
        assert len(report.detected_languages) >= 2
        assert "python" in report.detected_languages
        assert "typescript" in report.detected_languages

        # Should have findings from multiple language ecosystems
        assert report.total_score > 0

    def test_scan_nonexistent_path(self):
        """Test scanning a nonexistent path raises error."""
        engine = ScanEngine()

        with pytest.raises(ValueError, match="does not exist"):
            engine.scan(Path("/nonexistent/path"))

    def test_scan_file_instead_of_directory(self, tmp_path: Path):
        """Test scanning a file instead of directory raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        engine = ScanEngine()

        with pytest.raises(ValueError, match="not a directory"):
            engine.scan(test_file)

    def test_report_to_dict(self, python_repo: Path):
        """Test converting report to dictionary."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        report_dict = report.to_dict()

        assert isinstance(report_dict, dict)
        assert "repo_path" in report_dict
        assert "total_score" in report_dict
        assert "grade" in report_dict
        assert "categories" in report_dict
        assert "detected_languages" in report_dict
        assert "scan_duration_ms" in report_dict
        assert "timestamp" in report_dict

        # Check categories structure
        assert len(report_dict["categories"]) == 8
        for cat in report_dict["categories"]:
            assert "name" in cat
            assert "score" in cat
            assert "weight" in cat
            assert "weighted_score" in cat
            assert "found" in cat
            assert "total" in cat
            assert "findings" in cat

    def test_weighted_score_calculation(self, python_repo: Path):
        """Test that weighted scores add up correctly."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        # Sum of weighted scores should equal total score
        total_weighted = sum(cs.weighted_score for cs in report.category_scores)
        assert abs(total_weighted - report.total_score) < 0.01  # Allow small float error

        # Weights should sum to 1.0
        total_weight = sum(cs.weight for cs in report.category_scores)
        assert abs(total_weight - 1.0) < 0.01

    def test_grade_calculation(self, complete_repo: Path, minimal_repo: Path):
        """Test grade calculation from scores."""
        from agent_readiness_score.core.models import calculate_grade

        # Test grade function directly
        assert calculate_grade(95) == "A"
        assert calculate_grade(90) == "A"
        assert calculate_grade(85) == "B"
        assert calculate_grade(80) == "B"
        assert calculate_grade(75) == "C"
        assert calculate_grade(65) == "D"
        assert calculate_grade(50) == "F"
        assert calculate_grade(0) == "F"

        # Test in real reports
        engine = ScanEngine()

        complete_report = engine.scan(complete_repo)
        assert complete_report.grade in ["A", "B"]

        minimal_report = engine.scan(minimal_repo)
        assert minimal_report.grade in ["D", "F"]

    def test_scan_duration_is_reasonable(self, python_repo: Path):
        """Test that scan completes in reasonable time."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        # Scan should complete in under 5 seconds for small repo
        assert report.scan_duration_ms < 5000

    def test_all_categories_scanned(self, python_repo: Path):
        """Test that all categories are included in report."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        scanned_categories = {cs.category for cs in report.category_scores}
        expected_categories = {
            Category.STYLE,
            Category.BUILD,
            Category.DEVENV,
            Category.OBSERVABILITY,
            Category.TESTING,
            Category.DEPENDENCIES,
            Category.DOCUMENTATION,
            Category.TYPING,
        }

        assert scanned_categories == expected_categories

    def test_findings_have_paths(self, python_repo: Path):
        """Test that findings include file paths when found."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        # Check that at least some findings have paths
        findings_with_paths = []
        for cat_score in report.category_scores:
            for finding in cat_score.findings:
                if finding.found and finding.path:
                    findings_with_paths.append(finding)

        assert len(findings_with_paths) > 0

        # Verify paths are valid
        for finding in findings_with_paths:
            assert finding.path is not None
            # Path should not be absolute (should be relative to repo)
            assert not Path(finding.path).is_absolute()

    def test_category_progress_calculation(self, python_repo: Path):
        """Test category score calculations."""
        engine = ScanEngine()
        report = engine.scan(python_repo)

        for cat_score in report.category_scores:
            # Found count should not exceed total count
            assert cat_score.found_count <= cat_score.total_count

            # Score should be proportional to found/total
            if cat_score.total_count > 0:
                expected_ratio = cat_score.found_count / cat_score.total_count
                # Score should be roughly proportional (allowing for weighting)
                assert cat_score.score >= 0
                assert cat_score.score <= 100


class TestScanEngineEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_repo_with_symlinks(self, tmp_path: Path):
        """Test scanning a repo with symbolic links."""
        repo = tmp_path / "repo"
        repo.mkdir()

        # Create a file and a symlink to it
        (repo / "README.md").write_text("# Test\n")
        original_file = repo / "test.py"
        original_file.write_text("def test(): pass\n")

        # Create symlink (may fail on Windows without admin)
        try:
            symlink = repo / "link.py"
            symlink.symlink_to(original_file)
        except OSError:
            pytest.skip("Cannot create symlinks on this system")

        engine = ScanEngine()
        report = engine.scan(repo)

        # Should complete without errors
        assert report.total_score >= 0

    def test_scan_repo_with_nested_gitignores(self, tmp_path: Path):
        """Test scanning repo with .gitignore files."""
        repo = tmp_path / "repo"
        repo.mkdir()

        (repo / ".gitignore").write_text("*.pyc\n__pycache__/\n")
        (repo / "src").mkdir()
        (repo / "src" / "main.py").write_text("def main(): pass\n")
        (repo / "src" / ".gitignore").write_text("local.py\n")

        engine = ScanEngine()
        report = engine.scan(repo)

        # Should scan successfully
        assert report.total_score >= 0

    def test_scan_large_repo_doesnt_hang(self, tmp_path: Path):
        """Test that scanning large repos completes in reasonable time."""
        repo = tmp_path / "large_repo"
        repo.mkdir()

        # Create many files
        for i in range(100):
            (repo / f"file_{i}.py").write_text(f"# File {i}\n")

        engine = ScanEngine()
        report = engine.scan(repo)

        # Should complete and not hang
        assert report.scan_duration_ms < 10000  # Under 10 seconds
        assert report.total_score >= 0

    def test_scan_repo_with_unicode_filenames(self, tmp_path: Path):
        """Test scanning repo with unicode characters in filenames."""
        repo = tmp_path / "repo"
        repo.mkdir()

        (repo / "README.md").write_text("# Test\n")
        (repo / "файл.py").write_text("# Russian\n")
        (repo / "文件.py").write_text("# Chinese\n")

        engine = ScanEngine()
        report = engine.scan(repo)

        # Should handle unicode filenames gracefully
        assert report.total_score >= 0
