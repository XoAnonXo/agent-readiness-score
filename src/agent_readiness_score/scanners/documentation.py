"""Documentation scanner with multi-language support."""

from pathlib import Path

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category, CategoryScore, Finding
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats

# Minimum README lines to be considered "substantial"
MIN_README_LINES = 20


@ScannerRegistry.register
class DocumentationScanner(BaseScanner):
    """Scans for documentation files and API docs across all languages."""

    @property
    def category(self) -> Category:
        return Category.DOCUMENTATION

    @property
    def name(self) -> str:
        return "Documentation"

    @property
    def description(self) -> str:
        return "Checks for README, docs directory, API documentation, and contribution guides"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Essential Docs (Universal) =====
            universal("README.md", "README.rst", "README.txt", "README", name="README", weight=2.0),
            universal("CONTRIBUTING.md", "CONTRIBUTING.rst", ".github/CONTRIBUTING.md", name="CONTRIBUTING", weight=1.5),
            universal("CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "CHANGES.md", "RELEASES.md", name="CHANGELOG", weight=1.2),
            universal("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md", name="CODE_OF_CONDUCT", weight=0.8),
            universal("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", name="LICENSE", weight=1.0),
            universal("SECURITY.md", ".github/SECURITY.md", name="SECURITY", weight=1.0),

            # ===== Docs Directory (Universal) =====
            universal("docs/", "doc/", "documentation/", "wiki/", name="Docs directory", weight=1.5),
            universal("examples/", "example/", "samples/", name="Examples directory", weight=1.0),

            # ===== API Docs (Universal) =====
            universal("openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json", name="OpenAPI spec", weight=1.2),
            universal("docs/api/", "api-docs/", "api/", name="API docs dir", weight=1.0),
            universal("api.md", "API.md", "docs/api.md", name="API documentation", weight=1.0),

            # ===== GitHub Templates (Universal) =====
            universal(".github/ISSUE_TEMPLATE/", ".github/ISSUE_TEMPLATE.md", name="Issue templates", weight=1.0),
            universal(".github/PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE/", name="PR template", weight=1.0),
            universal(".github/CODEOWNERS", "CODEOWNERS", name="CODEOWNERS", weight=0.8),
            universal(".github/FUNDING.yml", name="Funding config", weight=0.5),

            # ===== Architecture (Universal) =====
            universal("ARCHITECTURE.md", "docs/architecture*", "ADR/", "docs/adr/", name="Architecture docs", weight=1.2),
            universal("docs/design/", "design/", "rfc/", "docs/rfc/", name="Design docs", weight=1.0),

            # ===== Universal Doc Generators =====
            universal("mkdocs.yml", "mkdocs.yaml", name="MkDocs", weight=1.0),
            universal(".vitepress/config.*", "docs/.vitepress/", name="VitePress", weight=1.0),
            universal("docusaurus.config.*", name="Docusaurus", weight=1.0),
            universal("book.toml", name="mdBook", weight=1.0),
            universal("antora.yml", name="Antora", weight=1.0),
            universal("hugo.toml", "hugo.yaml", "config/_default/", name="Hugo", weight=0.8),
            universal("_config.yml", name="Jekyll", weight=0.8),

            # ===== Python =====
            py("docs/conf.py", "conf.py", name="Sphinx", weight=1.2),
            py("docs/source/", "source/", name="Sphinx source", weight=1.0),
            py("pdoc/", "**/pdoc.py", name="pdoc", weight=1.0),
            py("pydoc/", name="pydoc", weight=0.8),
            py("docs/api.rst", "docs/api.md", name="Python API docs", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js("typedoc.json", "typedoc.js", name="TypeDoc", weight=1.2),
            js("jsdoc.json", "jsdoc.conf.json", name="JSDoc", weight=1.0),
            js("esdoc.json", name="ESDoc", weight=0.8),
            js(".storybook/", "storybook/", name="Storybook", weight=1.0),
            js("api-extractor.json", name="API Extractor", weight=1.0),

            # ===== Go =====
            go("doc.go", "**/doc.go", name="Go doc.go", weight=1.2),
            go("godoc/", "docs/godoc/", name="godoc output", weight=1.0),
            go("examples_test.go", "example_test.go", name="Go examples", weight=1.0),

            # ===== Rust =====
            rust("docs.rs", name="docs.rs config", weight=1.0),
            rust("README.md", "crates/*/README.md", name="Crate READMEs", weight=1.0),
            rust("CHANGELOG.md", "crates/*/CHANGELOG.md", name="Crate changelogs", weight=1.0),
            rust("examples/*.rs", name="Rust examples", weight=1.0),

            # ===== Ruby =====
            ruby(".yardopts", "doc/.yardoc/", name="YARD", weight=1.2),
            ruby(".rdoc_options", name="RDoc", weight=0.8),
            ruby("docs/guides/", "guides/", name="Rails guides", weight=1.0),
            ruby("RAILS_UPGRADE.md", "UPGRADING.md", name="Upgrade guide", weight=1.0),

            # ===== Java/Kotlin =====
            java("javadoc/", "docs/javadoc/", "apidocs/", name="Javadoc", weight=1.2),
            java("dokka.json", "dokka/", name="Dokka (Kotlin)", weight=1.2),
            java("src/main/javadoc/", name="Javadoc sources", weight=1.0),
            java("MIGRATION.md", "docs/migration*", name="Migration guide", weight=1.0),

            # ===== Swift =====
            swift("docs/docc/", "*.docc/", name="DocC", weight=1.2),
            swift("jazzy.yaml", ".jazzy.yaml", name="Jazzy", weight=1.0),
            swift("Package.swift", name="Swift Package manifest", weight=0.8),

            # ===== C# =====
            csharp("docfx.json", name="DocFX", weight=1.2),
            csharp("*.xml", name="XML docs", weight=0.8),
            csharp("api/", "docs/api/", name="API reference", weight=1.0),

            # ===== C/C++ =====
            cpp("Doxyfile", "Doxyfile.in", "doxygen.conf", name="Doxygen", weight=1.2),
            cpp("docs/html/", "html/", name="Generated docs", weight=1.0),
            cpp("man/", "man1/", name="Man pages", weight=0.8),

            # ===== PHP =====
            php("phpdoc.xml", "phpdoc.dist.xml", name="phpDocumentor", weight=1.2),
            php("docs/", name="PHP docs", weight=1.0),
            php("sami.php", name="Sami", weight=0.8),

            # ===== Elixir =====
            elixir(".formatter.exs", name="ExDoc formatter", weight=0.8),
            elixir("guides/", name="Elixir guides", weight=1.0),
            elixir("pages/", name="ExDoc pages", weight=1.0),
            elixir("cheatsheets/", name="Cheatsheets", weight=0.8),

            # ===== Dart/Flutter =====
            dart("dartdoc_options.yaml", name="dartdoc config", weight=1.2),
            dart("doc/api/", "api/", name="Dart API docs", weight=1.0),
            dart("example/", name="Dart examples", weight=1.0),
        ]

    def scan(self, repo_path: Path, lang_stats: LanguageStats | None = None) -> CategoryScore:
        """Scan with bonus check for README length."""
        # Run standard checks
        findings = self._run_standard_checks(repo_path, lang_stats)

        # Bonus check: README length
        findings.extend(self._check_readme_length(repo_path))

        return self._calculate_category_score(findings)

    def _check_readme_length(self, repo_path: Path) -> list[Finding]:
        """Check if README is substantial (has enough lines)."""
        readme_paths = ["README.md", "README.rst", "README.txt", "README"]
        for readme_name in readme_paths:
            readme_path = repo_path / readme_name
            if readme_path.exists():
                try:
                    lines = len(readme_path.read_text().splitlines())
                    is_substantial = lines > MIN_README_LINES
                    return [
                        Finding(
                            name=f"README substantial (>{MIN_README_LINES} lines)",
                            found=is_substantial,
                            path=Path(readme_name) if is_substantial else None,
                            details=f"README has {lines} lines",
                            weight=1.0,
                        )
                    ]
                except (UnicodeDecodeError, PermissionError):
                    pass
                break
        return []
