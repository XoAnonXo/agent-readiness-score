"""Dependency management scanner with multi-language support."""

from pathlib import Path

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category, CategoryScore, Finding
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats

# Critical weight for missing lockfiles
CRITICAL_LOCKFILE_WEIGHT = 3.0


@ScannerRegistry.register
class DependenciesScanner(BaseScanner):
    """Scans for dependency management and lockfiles across all languages."""

    @property
    def category(self) -> Category:
        return Category.DEPENDENCIES

    @property
    def name(self) -> str:
        return "Dependency Management"

    @property
    def description(self) -> str:
        return "Checks for lockfiles, dependency pinning, and security scanning"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal =====
            universal(".github/dependabot.yml", ".github/dependabot.yaml", name="Dependabot", weight=1.5),
            universal("renovate.json", "renovate.json5", ".renovaterc", ".renovaterc.json", name="Renovate", weight=1.5),
            universal("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", name="License file", weight=1.0),
            universal(".snyk", name="Snyk config", weight=1.0),
            universal("SECURITY.md", ".github/SECURITY.md", name="Security policy", weight=1.0),

            # ===== Python =====
            py("poetry.lock", name="Poetry lockfile", weight=2.0),
            py("Pipfile.lock", name="Pipenv lockfile", weight=2.0),
            py("pdm.lock", name="PDM lockfile", weight=2.0),
            py("uv.lock", name="uv lockfile", weight=2.0),
            py("requirements.lock", "requirements-lock.txt", name="pip-tools lockfile", weight=1.5),
            py("requirements.txt", "requirements/*.txt", name="Requirements file", weight=1.0),
            py("constraints.txt", name="Pip constraints", weight=0.8),
            py(".safety-policy.yml", name="Safety config", weight=1.0),
            py("pip-audit.toml", ".pip-audit.toml", name="pip-audit config", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js("package-lock.json", name="npm lockfile", weight=2.0),
            js("yarn.lock", name="Yarn lockfile", weight=2.0),
            js("pnpm-lock.yaml", name="pnpm lockfile", weight=2.0),
            js("bun.lockb", name="Bun lockfile", weight=2.0),
            js("shrinkwrap.json", name="npm shrinkwrap", weight=1.5),
            js(".npmrc", name="npm config", weight=0.8),
            js(".yarnrc", ".yarnrc.yml", name="Yarn config", weight=0.8),
            js(".nvmrc", ".node-version", name="Node version", weight=0.8),

            # ===== Go =====
            go("go.sum", name="Go checksum", weight=2.0),
            go("go.mod", name="Go modules", weight=1.5),
            go("vendor/", name="Go vendor dir", weight=1.0),
            go("go.work", "go.work.sum", name="Go workspace", weight=0.8),

            # ===== Rust =====
            rust("Cargo.lock", name="Cargo lockfile", weight=2.0),
            rust("Cargo.toml", name="Cargo manifest", weight=1.5),
            rust("rust-toolchain.toml", "rust-toolchain", name="Rust toolchain", weight=1.0),
            rust(".cargo/config.toml", name="Cargo config", weight=0.8),
            rust("deny.toml", name="cargo-deny", weight=1.2),
            rust("audit.toml", name="cargo-audit config", weight=1.0),

            # ===== Ruby =====
            ruby("Gemfile.lock", name="Bundler lockfile", weight=2.0),
            ruby("Gemfile", name="Gemfile", weight=1.5),
            ruby(".ruby-version", name="Ruby version", weight=1.0),
            ruby(".ruby-gemset", name="RVM gemset", weight=0.8),
            ruby(".bundle/config", name="Bundler config", weight=0.8),
            ruby("bundler-audit.yml", name="bundler-audit", weight=1.0),

            # ===== Java/Kotlin =====
            java("pom.xml", name="Maven POM", weight=1.5),
            java("build.gradle.lockfile", "gradle.lockfile", name="Gradle lockfile", weight=2.0),
            java("gradle/verification-metadata.xml", name="Gradle verification", weight=1.5),
            java("mvnw", ".mvn/", name="Maven wrapper", weight=1.0),
            java("gradlew", "gradle/wrapper/", name="Gradle wrapper", weight=1.0),
            java(".sdkmanrc", name="SDKMAN config", weight=0.8),

            # ===== Swift =====
            swift("Package.resolved", name="Swift Package resolved", weight=2.0),
            swift("Podfile.lock", name="CocoaPods lockfile", weight=2.0),
            swift("Cartfile.resolved", name="Carthage resolved", weight=1.5),
            swift(".swift-version", name="Swift version", weight=1.0),

            # ===== C# =====
            csharp("packages.lock.json", name="NuGet lockfile", weight=2.0),
            csharp("Directory.Packages.props", name="Central package management", weight=1.5),
            csharp("nuget.config", name="NuGet config", weight=0.8),
            csharp("global.json", name=".NET global.json", weight=1.0),

            # ===== C/C++ =====
            cpp("conan.lock", name="Conan lockfile", weight=2.0),
            cpp("vcpkg.json", name="vcpkg manifest", weight=1.5),
            cpp("vcpkg-configuration.json", name="vcpkg config", weight=1.0),
            cpp("conanfile.txt", "conanfile.py", name="Conan manifest", weight=1.2),

            # ===== PHP =====
            php("composer.lock", name="Composer lockfile", weight=2.0),
            php("composer.json", name="Composer manifest", weight=1.5),
            php("auth.json", name="Composer auth", weight=0.5),

            # ===== Elixir =====
            elixir("mix.lock", name="Mix lockfile", weight=2.0),
            elixir("mix.exs", name="Mix manifest", weight=1.5),
            elixir("rebar.lock", name="Rebar3 lockfile", weight=1.5),

            # ===== Dart/Flutter =====
            dart("pubspec.lock", name="Pub lockfile", weight=2.0),
            dart("pubspec.yaml", name="Pub manifest", weight=1.5),

            # ===== Haskell =====
            ("Haskell lockfile", ["cabal.project.freeze", "stack.yaml.lock"], 2.0, {Language.HASKELL}),

            # ===== Zig =====
            ("Zig lockfile", ["build.zig.zon"], 1.5, {Language.ZIG}),
        ]

    def scan(self, repo_path: Path, lang_stats: LanguageStats | None = None) -> CategoryScore:
        """Scan with critical check for missing lockfiles."""
        # Run standard checks
        findings = self._run_standard_checks(repo_path, lang_stats)

        # Add critical checks for manifest without lockfile
        findings.extend(self._check_missing_lockfiles(repo_path))

        return self._calculate_category_score(findings)

    def _check_missing_lockfiles(self, repo_path: Path) -> list[Finding]:
        """Check for manifest files without corresponding lockfiles."""
        findings: list[Finding] = []

        critical_pairs = [
            ("package.json", ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"], "Node"),
            ("Gemfile", ["Gemfile.lock"], "Ruby"),
            ("composer.json", ["composer.lock"], "PHP"),
            ("pubspec.yaml", ["pubspec.lock"], "Dart"),
            ("mix.exs", ["mix.lock"], "Elixir"),
        ]

        for manifest, lockfiles, lang_name in critical_pairs:
            manifest_path = repo_path / manifest
            if manifest_path.exists():
                has_lockfile = any((repo_path / lf).exists() for lf in lockfiles)
                if not has_lockfile:
                    findings.append(
                        Finding(
                            name=f"{lang_name} lockfile (CRITICAL)",
                            found=False,
                            details=f"{manifest} exists without lockfile - agents cannot reliably install",
                            weight=CRITICAL_LOCKFILE_WEIGHT,
                        )
                    )

        return findings
