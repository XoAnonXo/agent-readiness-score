"""Static typing scanner with multi-language support."""

import re
from pathlib import Path

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, ts, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category, CategoryScore, Finding
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats, SKIP_DIRS

# Maximum Python files to sample for type hints
MAX_PYTHON_FILES_TO_CHECK = 10

# Regex pattern for Python type hints
TYPE_HINT_PATTERN = re.compile(r"def\s+\w+\([^)]*\)\s*->\s*\w+")


@ScannerRegistry.register
class TypingScanner(BaseScanner):
    """Scans for static typing configurations across all languages."""

    @property
    def category(self) -> Category:
        return Category.TYPING

    @property
    def name(self) -> str:
        return "Static Typing"

    @property
    def description(self) -> str:
        return "Checks for type definitions, type checkers, and type annotations"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal =====
            universal("**/*.graphql", "schema.graphql", name="GraphQL schema", weight=1.0),
            universal("**/*.proto", "proto/", name="Protobuf definitions", weight=1.0),
            universal("**/*.schema.json", "schemas/", name="JSON Schema", weight=0.8),
            universal("**/*.avsc", name="Avro schema", weight=0.8),
            universal("openapi.yaml", "openapi.json", "swagger.yaml", name="OpenAPI spec", weight=1.0),
            universal("**/*.thrift", name="Thrift definitions", weight=0.8),

            # ===== Python =====
            py("mypy.ini", ".mypy.ini", name="mypy config", weight=1.5),
            py("pyrightconfig.json", name="Pyright config", weight=1.5),
            py("pyproject.toml", name="pyproject.toml (typing)", weight=1.0),
            py("**/py.typed", "src/**/py.typed", name="py.typed marker", weight=1.5),
            py("**/*.pyi", "stubs/", "typings/", name="Type stubs (.pyi)", weight=1.0),
            py(".pytype", name="pytype config", weight=1.0),

            # ===== TypeScript =====
            ts("tsconfig.json", name="tsconfig.json", weight=2.0),
            ts("tsconfig.*.json", name="Extended tsconfigs", weight=1.0),
            ts("**/*.d.ts", name="Type declarations (.d.ts)", weight=1.0),
            ts("@types/", "types/", "typings/", name="Type definitions dir", weight=1.0),

            # ===== JavaScript (JSDoc) =====
            js("jsconfig.json", name="jsconfig.json", weight=1.2),

            # ===== Go =====
            # Go is statically typed by default, check for interfaces
            go("**/*_interface.go", "**/interfaces.go", name="Go interfaces", weight=1.0),
            go("**/*.go", name="Go source (typed)", weight=0.8),

            # ===== Rust =====
            # Rust is statically typed by default
            rust("**/*.rs", name="Rust source (typed)", weight=0.8),
            rust("**/lib.rs", "**/mod.rs", name="Rust modules", weight=1.0),

            # ===== Java/Kotlin =====
            java("**/*.java", name="Java source (typed)", weight=0.8),
            java("**/*.kt", name="Kotlin source (typed)", weight=0.8),
            java("lombok.config", name="Lombok config", weight=0.5),

            # ===== Swift =====
            swift("**/*.swift", name="Swift source (typed)", weight=0.8),

            # ===== C# =====
            csharp("**/*.cs", name="C# source (typed)", weight=0.8),
            csharp("Directory.Build.props", name="MSBuild (nullable)", weight=1.0),

            # ===== C/C++ =====
            cpp("**/*.cpp", "**/*.cc", "**/*.hpp", name="C++ source (typed)", weight=0.8),
            cpp("**/*.h", name="C/C++ headers", weight=1.0),

            # ===== PHP =====
            php("phpstan.neon", "phpstan.neon.dist", name="PHPStan (static)", weight=1.5),
            php("psalm.xml", name="Psalm (static)", weight=1.5),
            php("phan.php", ".phan/config.php", name="Phan config", weight=1.2),

            # ===== Elixir =====
            elixir("dialyzer.ignore-warnings", ".dialyzer_ignore.exs", name="Dialyzer", weight=1.5),
            elixir("**/*.ex", name="Elixir source", weight=0.5),

            # ===== Dart =====
            dart("analysis_options.yaml", name="Dart analysis", weight=1.5),
            dart("**/*.dart", name="Dart source (typed)", weight=0.8),

            # ===== Ruby (Sorbet) =====
            ruby("sorbet/", "sorbet/config", name="Sorbet config", weight=2.0),
            ruby("**/*.rbi", name="Sorbet RBI files", weight=1.5),
            ruby("tapioca.yml", name="Tapioca config", weight=1.0),
            ruby("steep/", "Steepfile", name="Steep config", weight=1.5),

            # ===== Haskell =====
            ("Haskell source (typed)", ["**/*.hs"], 0.8, {Language.HASKELL}),

            # ===== Scala =====
            ("Scala source (typed)", ["**/*.scala"], 0.8, {Language.SCALA}),

            # ===== Zig =====
            ("Zig source (typed)", ["**/*.zig"], 0.8, {Language.ZIG}),
        ]

    def scan(self, repo_path: Path, lang_stats: LanguageStats | None = None) -> CategoryScore:
        """Scan with content analysis for type annotations."""
        # Run standard checks
        findings = self._run_standard_checks(repo_path, lang_stats)

        # ===== Content Analysis: Python type hints =====
        if lang_stats is None or lang_stats.has_language(Language.PYTHON):
            has_type_hints = self._check_python_type_hints(repo_path)
            findings.append(
                Finding(
                    name="Python type annotations",
                    found=has_type_hints,
                    details="Found `def func() -> type:` patterns" if has_type_hints else None,
                    weight=1.5,
                )
            )

            # Check for mypy in pyproject.toml
            pyproject = repo_path / "pyproject.toml"
            if pyproject.exists():
                try:
                    content = pyproject.read_text()
                    has_mypy = "[tool.mypy]" in content
                    findings.append(
                        Finding(
                            name="mypy in pyproject.toml",
                            found=has_mypy,
                            path=Path("pyproject.toml") if has_mypy else None,
                            weight=1.2,
                        )
                    )
                except (UnicodeDecodeError, PermissionError):
                    pass

        # ===== Content Analysis: TypeScript strict mode =====
        if lang_stats is None or lang_stats.has_language(Language.TYPESCRIPT):
            tsconfig = repo_path / "tsconfig.json"
            if tsconfig.exists():
                try:
                    content = tsconfig.read_text()
                    has_strict = '"strict": true' in content or '"strict":true' in content
                    findings.append(
                        Finding(
                            name="TypeScript strict mode",
                            found=has_strict,
                            path=Path("tsconfig.json") if has_strict else None,
                            details="strict: true enabled" if has_strict else "strict mode not enabled",
                            weight=1.5,
                        )
                    )
                except (UnicodeDecodeError, PermissionError):
                    pass

        return self._calculate_category_score(findings)

    def _check_python_type_hints(self, repo_path: Path) -> bool:
        """Sample Python files for type hints."""
        py_files_checked = 0
        for py_file in repo_path.rglob("*.py"):
            if any(skip_dir in py_file.parts for skip_dir in SKIP_DIRS):
                continue

            try:
                content = py_file.read_text()
                if TYPE_HINT_PATTERN.search(content):
                    return True
            except (UnicodeDecodeError, PermissionError):
                continue

            py_files_checked += 1
            if py_files_checked >= MAX_PYTHON_FILES_TO_CHECK:
                break

        return False
