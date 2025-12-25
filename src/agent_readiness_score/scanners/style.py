"""Style and validation scanner with multi-language support."""

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, ts, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats


@ScannerRegistry.register
class StyleScanner(BaseScanner):
    """Scans for linter and formatter configurations across all languages."""

    @property
    def category(self) -> Category:
        return Category.STYLE

    @property
    def name(self) -> str:
        return "Style & Validation"

    @property
    def description(self) -> str:
        return "Checks for linter configs, formatters, and code style enforcement"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal =====
            universal(".editorconfig", name="EditorConfig", weight=1.0),
            universal(".pre-commit-config.yaml", ".pre-commit-config.yml", name="Pre-commit hooks", weight=1.5),
            universal(".github/workflows/*.yml", name="CI linting workflow", weight=1.0),

            # ===== Python =====
            py("ruff.toml", ".ruff.toml", "pyproject.toml", name="Ruff (Python)", weight=1.5),
            py("pyproject.toml", ".black.toml", name="Black (Python)", weight=1.0),
            py(".flake8", "setup.cfg", "tox.ini", name="Flake8 (Python)", weight=1.0),
            py(".pylintrc", "pylintrc", name="Pylint (Python)", weight=1.0),
            py(".isort.cfg", "pyproject.toml", name="isort (Python)", weight=0.8),
            py("mypy.ini", ".mypy.ini", "pyproject.toml", name="mypy (Python)", weight=1.2),
            py(".bandit", ".bandit.yaml", name="Bandit security (Python)", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js(".eslintrc*", "eslint.config.*", ".eslintrc.json", ".eslintrc.js", "eslint.config.mjs", name="ESLint", weight=1.5),
            js(".prettierrc*", "prettier.config.*", ".prettierrc.json", name="Prettier", weight=1.2),
            js("biome.json", "biome.jsonc", name="Biome", weight=1.5),
            js(".stylelintrc*", "stylelint.config.*", name="Stylelint (CSS)", weight=1.0),
            js(".huskyrc*", ".husky/*", name="Husky git hooks", weight=1.0),
            js(".lintstagedrc*", "lint-staged.config.*", name="lint-staged", weight=0.8),
            ts("tslint.json", name="TSLint (deprecated)", weight=0.5),

            # ===== Go =====
            go(".golangci.yml", ".golangci.yaml", ".golangci.toml", name="golangci-lint", weight=1.5),
            go(".revive.toml", name="Revive linter", weight=1.0),
            go(".staticcheck.conf", name="Staticcheck", weight=1.0),
            go("gofmt", name="gofmt config", weight=0.8),

            # ===== Rust =====
            rust("rustfmt.toml", ".rustfmt.toml", name="rustfmt", weight=1.5),
            rust("clippy.toml", ".clippy.toml", name="Clippy lints", weight=1.5),
            rust(".cargo/config.toml", name="Cargo config", weight=0.8),

            # ===== Ruby =====
            ruby(".rubocop.yml", ".rubocop.yaml", name="RuboCop", weight=1.5),
            ruby(".standard.yml", name="Standard Ruby", weight=1.2),
            ruby(".reek.yml", name="Reek (code smells)", weight=1.0),
            ruby(".haml-lint.yml", name="HAML Lint", weight=0.8),
            ruby(".erb-lint.yml", name="ERB Lint", weight=0.8),

            # ===== Java/Kotlin =====
            java("checkstyle.xml", ".checkstyle", name="Checkstyle", weight=1.5),
            java("pmd.xml", ".pmd", name="PMD", weight=1.2),
            java("spotbugs.xml", name="SpotBugs", weight=1.2),
            java(".editorconfig", "google-java-format", name="Google Java Format", weight=1.0),
            java("detekt.yml", ".detekt.yml", name="Detekt (Kotlin)", weight=1.5),
            java("ktlint", ".ktlint", name="ktlint (Kotlin)", weight=1.2),

            # ===== Swift =====
            swift(".swiftlint.yml", ".swiftlint.yaml", name="SwiftLint", weight=1.5),
            swift(".swift-format", name="swift-format", weight=1.2),

            # ===== C# =====
            csharp(".editorconfig", name="C# EditorConfig", weight=1.0),
            csharp("stylecop.json", ".stylecop", name="StyleCop", weight=1.2),
            csharp(".globalconfig", name="Global analyzer config", weight=1.0),

            # ===== C/C++ =====
            cpp(".clang-format", "_clang-format", name="clang-format", weight=1.5),
            cpp(".clang-tidy", name="clang-tidy", weight=1.5),
            cpp(".cppcheck", "cppcheck.cfg", name="cppcheck", weight=1.2),
            cpp(".cpplint", "CPPLINT.cfg", name="cpplint", weight=1.0),

            # ===== PHP =====
            php("phpcs.xml", ".phpcs.xml", "phpcs.xml.dist", name="PHP_CodeSniffer", weight=1.5),
            php(".php-cs-fixer.php", ".php-cs-fixer.dist.php", name="PHP-CS-Fixer", weight=1.5),
            php("phpstan.neon", "phpstan.neon.dist", name="PHPStan", weight=1.2),
            php("psalm.xml", name="Psalm", weight=1.2),
            php("pint.json", name="Laravel Pint", weight=1.0),

            # ===== Elixir =====
            elixir(".credo.exs", name="Credo", weight=1.5),
            elixir(".formatter.exs", name="Elixir Formatter", weight=1.2),
            elixir("dialyzer.ignore-warnings", ".dialyzer_ignore.exs", name="Dialyzer", weight=1.0),

            # ===== Dart/Flutter =====
            dart("analysis_options.yaml", name="Dart Analyzer", weight=1.5),
            dart(".dart_tool", name="Dart tooling", weight=0.8),

            # ===== Other =====
            universal("megalinter.yml", ".mega-linter.yml", name="MegaLinter", weight=1.5),
            universal(".trunk/trunk.yaml", name="Trunk.io", weight=1.2),
            universal("lefthook.yml", ".lefthook.yml", name="Lefthook", weight=1.0),
        ]
