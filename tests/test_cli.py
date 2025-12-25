"""Tests for the CLI."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from agent_readiness_score.cli import app


runner = CliRunner()


class TestScanCommand:
    """Test the scan command."""

    def test_scan_current_directory(self, python_repo: Path, monkeypatch):
        """Test scanning the current directory."""
        monkeypatch.chdir(python_repo)

        result = runner.invoke(app, ["scan", "."])

        assert result.exit_code == 0
        assert "Agent Readiness" in result.stdout
        assert "Score" in result.stdout

    def test_scan_specific_path(self, python_repo: Path):
        """Test scanning a specific path."""
        result = runner.invoke(app, ["scan", str(python_repo)])

        assert result.exit_code == 0
        assert "Testing" in result.stdout
        assert "Documentation" in result.stdout

    def test_scan_with_verbose(self, python_repo: Path):
        """Test scanning with verbose output."""
        result = runner.invoke(app, ["scan", str(python_repo), "--verbose"])

        assert result.exit_code == 0
        # Verbose mode should show individual findings
        assert "pytest" in result.stdout.lower() or "findings" in result.stdout.lower()

    def test_scan_json_output_only(self, python_repo: Path):
        """Test JSON-only output."""
        result = runner.invoke(app, ["scan", str(python_repo), "--output", "json"])

        assert result.exit_code == 0
        # Output should be valid JSON
        try:
            output_lines = result.stdout.strip().split("\n")
            # Find the JSON output (might have some status messages before it)
            json_line = None
            for line in output_lines:
                if line.strip().startswith("{"):
                    json_line = line
                    break

            assert json_line is not None
            data = json.loads(json_line)
            assert "total_score" in data
            assert "grade" in data
            assert "categories" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.stdout}")

    def test_scan_table_output_only(self, python_repo: Path):
        """Test table-only output."""
        result = runner.invoke(app, ["scan", str(python_repo), "--output", "table"])

        assert result.exit_code == 0
        assert "Testing" in result.stdout
        assert "Grade" in result.stdout or "Score" in result.stdout

    def test_scan_both_outputs(self, python_repo: Path):
        """Test both table and JSON output."""
        result = runner.invoke(app, ["scan", str(python_repo), "--output", "both"])

        assert result.exit_code == 0
        # Should have table
        assert "Testing" in result.stdout
        # Should also have JSON somewhere

    def test_scan_save_json_file(self, python_repo: Path, tmp_path: Path):
        """Test saving JSON to file."""
        json_file = tmp_path / "report.json"

        result = runner.invoke(
            app,
            ["scan", str(python_repo), "--json-file", str(json_file)]
        )

        assert result.exit_code == 0
        assert json_file.exists()

        # Verify file contains valid JSON
        with open(json_file) as f:
            data = json.load(f)
            assert "total_score" in data
            assert "grade" in data
            assert "categories" in data

    def test_scan_min_score_pass(self, complete_repo: Path):
        """Test min-score threshold when score is above."""
        result = runner.invoke(
            app,
            ["scan", str(complete_repo), "--min-score", "50"]
        )

        # Complete repo should pass 50 threshold
        assert result.exit_code == 0

    def test_scan_min_score_fail(self, minimal_repo: Path):
        """Test min-score threshold when score is below."""
        result = runner.invoke(
            app,
            ["scan", str(minimal_repo), "--min-score", "90"]
        )

        # Minimal repo should fail 90 threshold
        assert result.exit_code == 1
        assert "below minimum threshold" in result.stdout

    def test_scan_nonexistent_path(self):
        """Test scanning nonexistent path."""
        result = runner.invoke(app, ["scan", "/nonexistent/path/xyz"])

        # Typer will handle the path validation
        assert result.exit_code != 0

    def test_scan_file_not_directory(self, tmp_path: Path):
        """Test scanning a file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # Typer should reject this before it reaches our code
        result = runner.invoke(app, ["scan", str(test_file)])

        assert result.exit_code != 0


class TestCategoriesCommand:
    """Test the categories command."""

    def test_categories_list(self):
        """Test listing all categories."""
        result = runner.invoke(app, ["categories"])

        assert result.exit_code == 0
        assert "Category" in result.stdout
        assert "Weight" in result.stdout

        # Should show all category names
        assert "Testing" in result.stdout or "testing" in result.stdout
        assert "Documentation" in result.stdout or "documentation" in result.stdout
        assert "Style" in result.stdout or "style" in result.stdout

        # Should show weights
        assert "%" in result.stdout


class TestVersionOption:
    """Test version command."""

    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()
        assert "0.1.0" in result.stdout

    def test_version_short_flag(self):
        """Test -V flag."""
        result = runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()


class TestHelpMessages:
    """Test help messages."""

    def test_main_help(self):
        """Test main help message."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Agent" in result.stdout
        assert "scan" in result.stdout
        assert "categories" in result.stdout

    def test_scan_help(self):
        """Test scan command help."""
        result = runner.invoke(app, ["scan", "--help"])

        assert result.exit_code == 0
        assert "repository" in result.stdout.lower()
        assert "--output" in result.stdout
        assert "--verbose" in result.stdout
        assert "--min-score" in result.stdout
        assert "--json-file" in result.stdout

    def test_categories_help(self):
        """Test categories command help."""
        result = runner.invoke(app, ["categories", "--help"])

        assert result.exit_code == 0
        assert "categories" in result.stdout.lower()


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_full_workflow(self, python_repo: Path, tmp_path: Path):
        """Test a complete workflow: scan, save JSON, check threshold."""
        json_file = tmp_path / "full_report.json"

        # Run scan with all options
        result = runner.invoke(
            app,
            [
                "scan",
                str(python_repo),
                "--verbose",
                "--output", "both",
                "--json-file", str(json_file),
                "--min-score", "30",  # Low threshold to ensure pass
            ]
        )

        assert result.exit_code == 0

        # Verify JSON file was created
        assert json_file.exists()

        # Verify JSON structure
        with open(json_file) as f:
            data = json.load(f)
            assert isinstance(data["total_score"], (int, float))
            assert data["grade"] in ["A", "B", "C", "D", "F"]
            assert len(data["categories"]) == 8

            # Verify each category
            for cat in data["categories"]:
                assert "name" in cat
                assert "score" in cat
                assert 0 <= cat["score"] <= 100
                assert "weight" in cat
                assert 0 < cat["weight"] <= 1
                assert "findings" in cat
                assert isinstance(cat["findings"], list)

    def test_scan_multiple_repos(self, python_repo: Path, typescript_repo: Path):
        """Test scanning multiple different repositories."""
        # Scan Python repo
        result1 = runner.invoke(app, ["scan", str(python_repo)])
        assert result1.exit_code == 0

        # Scan TypeScript repo
        result2 = runner.invoke(app, ["scan", str(typescript_repo)])
        assert result2.exit_code == 0

        # Both should succeed but may have different scores
        assert "Score" in result1.stdout
        assert "Score" in result2.stdout

    def test_error_handling_graceful(self):
        """Test that errors are handled gracefully."""
        # Invalid min-score value
        result = runner.invoke(app, ["scan", ".", "--min-score", "150"])

        # Should fail with clear error
        assert result.exit_code != 0


class TestCLIOutput:
    """Test CLI output formatting."""

    def test_output_contains_score(self, python_repo: Path):
        """Test that output contains the final score."""
        result = runner.invoke(app, ["scan", str(python_repo)])

        assert result.exit_code == 0
        # Should show a score number
        assert any(char.isdigit() for char in result.stdout)

    def test_output_contains_grade(self, python_repo: Path):
        """Test that output contains a letter grade."""
        result = runner.invoke(app, ["scan", str(python_repo)])

        assert result.exit_code == 0
        # Should contain a grade letter
        assert any(grade in result.stdout for grade in ["Grade: A", "Grade: B", "Grade: C", "Grade: D", "Grade: F"])

    def test_output_shows_all_categories(self, python_repo: Path):
        """Test that output shows all scoring categories."""
        result = runner.invoke(app, ["scan", str(python_repo)])

        assert result.exit_code == 0

        # Should mention categories (exact formatting may vary)
        output_lower = result.stdout.lower()
        category_mentions = sum([
            "test" in output_lower,
            "style" in output_lower or "lint" in output_lower,
            "build" in output_lower,
            "doc" in output_lower,
            "depend" in output_lower,
            "type" in output_lower or "typing" in output_lower,
        ])

        # Should mention at least several categories
        assert category_mentions >= 4

    def test_verbose_shows_more_detail(self, python_repo: Path):
        """Test that verbose mode shows more detail."""
        normal_result = runner.invoke(app, ["scan", str(python_repo)])
        verbose_result = runner.invoke(app, ["scan", str(python_repo), "--verbose"])

        assert normal_result.exit_code == 0
        assert verbose_result.exit_code == 0

        # Verbose should have more output
        assert len(verbose_result.stdout) >= len(normal_result.stdout)

    def test_json_output_is_valid(self, python_repo: Path):
        """Test that JSON output is valid and complete."""
        result = runner.invoke(app, ["scan", str(python_repo), "--output", "json"])

        assert result.exit_code == 0

        # Find and parse JSON
        json_line = None
        for line in result.stdout.split("\n"):
            if line.strip().startswith("{"):
                json_line = line
                break

        assert json_line is not None
        data = json.loads(json_line)

        # Verify required fields
        required_fields = [
            "repo_path",
            "total_score",
            "grade",
            "categories",
            "detected_languages",
            "scan_duration_ms",
            "timestamp",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
