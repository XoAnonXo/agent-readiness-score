"""Package and repository structure detection."""

from pathlib import Path

from agent_readiness_score.core.language import Language, LanguageStats
from agent_readiness_score.core.models import Package, RepoStructure, RepoType


# Package manifest files that indicate a package root
PACKAGE_MANIFESTS = {
    "package.json": ("npm", {Language.JAVASCRIPT, Language.TYPESCRIPT}),
    "pyproject.toml": ("python", {Language.PYTHON}),
    "setup.py": ("python", {Language.PYTHON}),
    "Cargo.toml": ("cargo", {Language.RUST}),
    "go.mod": ("go", {Language.GO}),
    "Gemfile": ("bundler", {Language.RUBY}),
    "pom.xml": ("maven", {Language.JAVA}),
    "build.gradle": ("gradle", {Language.JAVA, Language.KOTLIN}),
    "build.gradle.kts": ("gradle", {Language.KOTLIN}),
    "Package.swift": ("spm", {Language.SWIFT}),
    "*.csproj": ("dotnet", {Language.CSHARP}),
    "composer.json": ("composer", {Language.PHP}),
    "mix.exs": ("mix", {Language.ELIXIR}),
    "pubspec.yaml": ("pub", {Language.DART}),
}

# Lockfiles that indicate dependency management
LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
    "Cargo.lock", "go.sum", "Gemfile.lock", "poetry.lock", "uv.lock",
    "composer.lock", "mix.lock", "pubspec.lock", "Package.resolved",
    "packages.lock.json",
}

# Test directory patterns
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs", "_tests"}

# Type config patterns
TYPE_CONFIGS = {"tsconfig.json", "mypy.ini", ".mypy.ini", "pyrightconfig.json"}

# Directories to skip when scanning for packages
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "target", ".next", ".nuxt", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
    ".cargo", ".rustup", "Pods", ".gradle", ".idea", ".vscode",
}


def _is_excluded(path: Path) -> bool:
    """Check if path is in an excluded directory."""
    return any(excluded in path.parts for excluded in SKIP_DIRS)


def _filtered_glob(path: Path, pattern: str, limit: int = 1) -> list[Path]:
    """Glob with exclusion filtering for performance."""
    results = []
    try:
        for match in path.glob(pattern):
            if not _is_excluded(match):
                results.append(match)
                if len(results) >= limit:
                    break
    except (PermissionError, OSError):
        pass
    return results

# Shared config files at root that benefit all packages
SHARED_CONFIGS = [
    (".editorconfig", "EditorConfig"),
    (".prettierrc", "Prettier"),
    (".prettierrc.json", "Prettier"),
    (".prettierrc.yaml", "Prettier"),
    ("prettier.config.js", "Prettier"),
    (".github/workflows/", "CI/CD Workflows"),
    (".github/dependabot.yml", "Dependabot"),
    (".devcontainer/", "Dev Container"),
    ("CONTRIBUTING.md", "Contributing Guide"),
    ("README.md", "README"),
    (".pre-commit-config.yaml", "Pre-commit hooks"),
    ("Makefile", "Makefile"),
    ("docker-compose.yml", "Docker Compose"),
    ("docker-compose.yaml", "Docker Compose"),
]


def detect_repo_structure(repo_path: Path) -> RepoStructure:
    """Detect the repository structure (single, monorepo, or polyrepo)."""
    packages = _detect_packages(repo_path)
    root_configs = _detect_root_configs(repo_path)
    root_languages = _detect_root_languages(repo_path)

    # Determine repo type
    if len(packages) == 0:
        repo_type = RepoType.SINGLE
    elif _has_workspace_config(repo_path):
        repo_type = RepoType.MONOREPO
    elif len(packages) > 1:
        repo_type = RepoType.POLYREPO
    else:
        # Single package detected, but at a subdirectory
        repo_type = RepoType.SINGLE if packages[0].path == Path(".") else RepoType.POLYREPO

    return RepoStructure(
        type=repo_type,
        packages=packages,
        root_configs=root_configs,
        root_languages=root_languages,
    )


def _detect_packages(repo_path: Path, max_depth: int = 3) -> list[Package]:
    """Detect packages/workspaces in the repository."""
    packages: list[Package] = []
    seen_paths: set[Path] = set()

    def scan_dir(path: Path, depth: int = 0) -> None:
        if depth > max_depth:
            return

        rel_path = path.relative_to(repo_path) if path != repo_path else Path(".")

        # Skip if already seen or in skip list
        if rel_path in seen_paths:
            return
        if any(part in SKIP_DIRS for part in rel_path.parts):
            return

        # Check for package manifests
        for manifest, (pm, langs) in PACKAGE_MANIFESTS.items():
            if "*" in manifest:
                pattern = manifest
                matches = list(path.glob(pattern))
                if matches:
                    pkg = _create_package(repo_path, path, pm, langs)
                    if pkg:
                        packages.append(pkg)
                        seen_paths.add(rel_path)
                    return
            elif (path / manifest).exists():
                pkg = _create_package(repo_path, path, pm, langs)
                if pkg:
                    packages.append(pkg)
                    seen_paths.add(rel_path)
                return

        # Recurse into subdirectories
        try:
            for subdir in path.iterdir():
                if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                    scan_dir(subdir, depth + 1)
        except PermissionError:
            pass

    scan_dir(repo_path)

    # If no packages found, treat root as single package
    if not packages and _has_any_code(repo_path):
        pkg = _create_package(repo_path, repo_path, None, set())
        if pkg:
            packages.append(pkg)

    return packages


def _create_package(
    repo_path: Path, pkg_path: Path, package_manager: str | None, langs: set[Language]
) -> Package | None:
    """Create a Package object with detected properties."""
    rel_path = pkg_path.relative_to(repo_path) if pkg_path != repo_path else Path(".")
    name = rel_path.name if rel_path != Path(".") else repo_path.name

    # Detect languages from files if not provided
    if not langs:
        langs = _detect_languages_in_dir(pkg_path)

    if not langs:
        return None  # No recognizable code

    # Check for tests
    has_tests = any((pkg_path / td).exists() for td in TEST_DIRS)
    if not has_tests:
        # Check for test files (with exclusion filtering)
        has_tests = bool(
            _filtered_glob(pkg_path, "**/test_*.py") or
            _filtered_glob(pkg_path, "**/*.test.ts") or
            _filtered_glob(pkg_path, "**/*.test.js") or
            _filtered_glob(pkg_path, "**/*_test.go")
        )

    # Check for lockfile
    has_lockfile = any((pkg_path / lf).exists() for lf in LOCKFILES)
    if not has_lockfile:
        # Check parent for shared lockfile (monorepo pattern)
        has_lockfile = any((repo_path / lf).exists() for lf in LOCKFILES)

    # Check for type configs
    has_types = any((pkg_path / tc).exists() for tc in TYPE_CONFIGS)
    if not has_types:
        has_types = any((repo_path / tc).exists() for tc in TYPE_CONFIGS)

    return Package(
        path=rel_path,
        name=name,
        languages=langs,
        package_manager=package_manager,
        has_tests=has_tests,
        has_lockfile=has_lockfile,
        has_types=has_types,
    )


def _detect_languages_in_dir(path: Path) -> set[Language]:
    """Detect languages present in a directory."""
    langs: set[Language] = set()

    # Quick check based on common files
    lang_indicators = {
        Language.PYTHON: ["*.py"],
        Language.JAVASCRIPT: ["*.js", "*.jsx"],
        Language.TYPESCRIPT: ["*.ts", "*.tsx", "tsconfig.json"],
        Language.GO: ["*.go", "go.mod"],
        Language.RUST: ["*.rs", "Cargo.toml"],
        Language.RUBY: ["*.rb", "Gemfile"],
        Language.JAVA: ["*.java"],
        Language.KOTLIN: ["*.kt", "*.kts"],
        Language.SWIFT: ["*.swift"],
        Language.CSHARP: ["*.cs"],
        Language.PHP: ["*.php"],
        Language.ELIXIR: ["*.ex", "*.exs"],
        Language.DART: ["*.dart"],
    }

    for lang, patterns in lang_indicators.items():
        for pattern in patterns:
            if _filtered_glob(path, f"**/{pattern}", limit=1):
                langs.add(lang)
                break

    return langs


def _detect_root_configs(repo_path: Path) -> list[Path]:
    """Detect shared config files at repository root."""
    configs: list[Path] = []
    for config_pattern, _ in SHARED_CONFIGS:
        if config_pattern.endswith("/"):
            # Directory
            if (repo_path / config_pattern.rstrip("/")).is_dir():
                configs.append(Path(config_pattern.rstrip("/")))
        else:
            if (repo_path / config_pattern).exists():
                configs.append(Path(config_pattern))
    return configs


def _detect_root_languages(repo_path: Path) -> set[Language]:
    """Detect languages at repo root (outside of packages)."""
    return _detect_languages_in_dir(repo_path)


def _has_workspace_config(repo_path: Path) -> bool:
    """Check if repo has workspace/monorepo configuration."""
    # Check package.json for workspaces
    pkg_json = repo_path / "package.json"
    if pkg_json.exists():
        try:
            import json
            with open(pkg_json) as f:
                data = json.load(f)
                if "workspaces" in data:
                    return True
        except (json.JSONDecodeError, IOError):
            pass

    # Check for pnpm-workspace.yaml
    if (repo_path / "pnpm-workspace.yaml").exists():
        return True

    # Check for lerna.json
    if (repo_path / "lerna.json").exists():
        return True

    # Check for Cargo workspace
    cargo_toml = repo_path / "Cargo.toml"
    if cargo_toml.exists():
        try:
            content = cargo_toml.read_text()
            if "[workspace]" in content:
                return True
        except IOError:
            pass

    return False


def _has_any_code(repo_path: Path) -> bool:
    """Check if directory has any recognizable code files."""
    code_patterns = ["*.py", "*.js", "*.ts", "*.go", "*.rs", "*.rb", "*.java", "*.swift", "*.cs"]
    for pattern in code_patterns:
        if _filtered_glob(repo_path, f"**/{pattern}", limit=1):
            return True
    return False


def get_shared_config_checks() -> list[tuple[str, str]]:
    """Get list of shared config checks for display."""
    return [(pattern, name) for pattern, name in SHARED_CONFIGS]
