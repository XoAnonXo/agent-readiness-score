"""Package and repository structure detection - optimized for large repos."""

import json
from pathlib import Path

from agent_readiness_score.core.language import Language
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
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs", "_tests", "e2e"}

# Type config patterns per language
TYPE_CONFIGS = {
    Language.TYPESCRIPT: ["tsconfig.json", "tsconfig.*.json"],
    Language.PYTHON: ["mypy.ini", ".mypy.ini", "pyrightconfig.json", "py.typed"],
    Language.GO: [],  # Go has built-in types
    Language.RUST: [],  # Rust has built-in types
}

# Directories to skip
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "target", ".next", ".nuxt", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
    ".cargo", ".rustup", "Pods", ".gradle", ".idea", ".vscode",
    ".turbo", ".vercel", ".netlify", "out", ".output",
}

# Shared config files at root
SHARED_CONFIGS = [
    (".editorconfig", "EditorConfig"),
    (".prettierrc", "Prettier"),
    (".prettierrc.json", "Prettier"),
    (".prettierrc.yaml", "Prettier"),
    ("prettier.config.js", "Prettier"),
    ("prettier.config.mjs", "Prettier"),
    (".github/workflows/", "CI/CD Workflows"),
    (".github/dependabot.yml", "Dependabot"),
    (".devcontainer/", "Dev Container"),
    ("CONTRIBUTING.md", "Contributing Guide"),
    ("README.md", "README"),
    (".pre-commit-config.yaml", "Pre-commit hooks"),
    ("Makefile", "Makefile"),
    ("docker-compose.yml", "Docker Compose"),
    ("docker-compose.yaml", "Docker Compose"),
    ("turbo.json", "Turborepo"),
    ("nx.json", "Nx"),
    ("lerna.json", "Lerna"),
]


def detect_repo_structure(repo_path: Path) -> RepoStructure:
    """Detect the repository structure (single, monorepo, or polyrepo)."""
    # First check for workspace/monorepo config
    workspace_dirs = _get_workspace_directories(repo_path)

    if workspace_dirs:
        # It's a monorepo - scan workspace directories
        packages = _scan_workspace_packages(repo_path, workspace_dirs)
        repo_type = RepoType.MONOREPO
    else:
        # Scan for packages normally
        packages = _detect_packages(repo_path)
        if len(packages) > 1:
            repo_type = RepoType.POLYREPO
        elif len(packages) == 1 and packages[0].path != Path("."):
            repo_type = RepoType.POLYREPO
        else:
            repo_type = RepoType.SINGLE

    root_configs = _detect_root_configs(repo_path)
    root_languages = _detect_languages_fast(repo_path, max_depth=1)

    return RepoStructure(
        type=repo_type,
        packages=packages,
        root_configs=root_configs,
        root_languages=root_languages,
    )


def _get_workspace_directories(repo_path: Path) -> list[Path]:
    """Get workspace directories from monorepo config."""
    workspaces: list[Path] = []

    # Check package.json workspaces
    pkg_json = repo_path / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json) as f:
                data = json.load(f)
                ws = data.get("workspaces", [])
                # Handle both array and object formats
                if isinstance(ws, dict):
                    ws = ws.get("packages", [])
                for pattern in ws:
                    # Expand glob patterns like "packages/*"
                    if "*" in pattern:
                        base = pattern.replace("/*", "").replace("/**", "")
                        base_path = repo_path / base
                        if base_path.is_dir():
                            for subdir in base_path.iterdir():
                                if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                                    workspaces.append(subdir)
                    else:
                        ws_path = repo_path / pattern
                        if ws_path.is_dir():
                            workspaces.append(ws_path)
        except (json.JSONDecodeError, IOError, KeyError):
            pass

    # Check pnpm-workspace.yaml
    pnpm_ws = repo_path / "pnpm-workspace.yaml"
    if pnpm_ws.exists() and not workspaces:
        try:
            content = pnpm_ws.read_text()
            # Simple YAML parsing for packages list
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    pattern = line[2:].strip().strip("'\"")
                    if "*" in pattern:
                        base = pattern.replace("/*", "").replace("/**", "")
                        base_path = repo_path / base
                        if base_path.is_dir():
                            for subdir in base_path.iterdir():
                                if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                                    workspaces.append(subdir)
                    else:
                        ws_path = repo_path / pattern
                        if ws_path.is_dir():
                            workspaces.append(ws_path)
        except IOError:
            pass

    # Check for Cargo workspace
    cargo_toml = repo_path / "Cargo.toml"
    if cargo_toml.exists() and not workspaces:
        try:
            content = cargo_toml.read_text()
            if "[workspace]" in content:
                # Parse members from Cargo.toml
                in_members = False
                for line in content.splitlines():
                    if "members" in line and "=" in line:
                        in_members = True
                    elif in_members:
                        if "]" in line:
                            break
                        member = line.strip().strip('",[]')
                        if member and not member.startswith("#"):
                            if "*" in member:
                                base = member.replace("/*", "")
                                base_path = repo_path / base
                                if base_path.is_dir():
                                    for subdir in base_path.iterdir():
                                        if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                                            workspaces.append(subdir)
                            else:
                                ws_path = repo_path / member
                                if ws_path.is_dir():
                                    workspaces.append(ws_path)
        except IOError:
            pass

    return workspaces


def _scan_workspace_packages(repo_path: Path, workspace_dirs: list[Path]) -> list[Package]:
    """Scan known workspace directories for packages."""
    packages: list[Package] = []

    for ws_dir in workspace_dirs:
        pkg = _create_package_fast(repo_path, ws_dir)
        if pkg:
            packages.append(pkg)

    return packages


def _detect_packages(repo_path: Path, max_depth: int = 2) -> list[Package]:
    """Detect packages in non-workspace repos."""
    packages: list[Package] = []
    seen_paths: set[Path] = set()

    def scan_dir(path: Path, depth: int = 0) -> None:
        if depth > max_depth:
            return

        rel_path = path.relative_to(repo_path) if path != repo_path else Path(".")

        if rel_path in seen_paths:
            return

        # Check for package manifest (excluding root for workspace detection)
        has_manifest = False
        for manifest in PACKAGE_MANIFESTS:
            if (path / manifest).exists():
                has_manifest = True
                # Don't add root if it's a workspace root
                if depth > 0 or not _is_workspace_root(path):
                    pkg = _create_package_fast(repo_path, path)
                    if pkg:
                        packages.append(pkg)
                        seen_paths.add(rel_path)
                break

        # Continue scanning subdirs even if we found a manifest
        # (for nested packages)
        if depth < max_depth:
            try:
                for subdir in sorted(path.iterdir()):
                    if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                        if subdir.relative_to(repo_path) not in seen_paths:
                            scan_dir(subdir, depth + 1)
            except PermissionError:
                pass

    scan_dir(repo_path)

    # If no packages found, treat root as single package
    if not packages:
        pkg = _create_package_fast(repo_path, repo_path)
        if pkg:
            packages.append(pkg)

    return packages


def _is_workspace_root(path: Path) -> bool:
    """Check if path is a workspace root (has workspaces config)."""
    pkg_json = path / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json) as f:
                data = json.load(f)
                if "workspaces" in data:
                    return True
        except (json.JSONDecodeError, IOError):
            pass

    if (path / "pnpm-workspace.yaml").exists():
        return True
    if (path / "lerna.json").exists():
        return True

    cargo_toml = path / "Cargo.toml"
    if cargo_toml.exists():
        try:
            if "[workspace]" in cargo_toml.read_text():
                return True
        except IOError:
            pass

    return False


def _create_package_fast(repo_path: Path, pkg_path: Path) -> Package | None:
    """Create a Package object with fast detection (no recursive globs)."""
    rel_path = pkg_path.relative_to(repo_path) if pkg_path != repo_path else Path(".")
    name = rel_path.name if rel_path != Path(".") else repo_path.name

    # Detect package manager and languages from manifest
    package_manager = None
    langs: set[Language] = set()

    for manifest, (pm, manifest_langs) in PACKAGE_MANIFESTS.items():
        if (pkg_path / manifest).exists():
            package_manager = pm
            langs.update(manifest_langs)
            break

    # Enhance language detection by checking for specific files
    langs.update(_detect_languages_fast(pkg_path, max_depth=2))

    if not langs:
        return None

    # Check for tests (direct check, no glob)
    has_tests = _has_tests_fast(pkg_path)

    # Check for lockfile
    has_lockfile = any((pkg_path / lf).exists() for lf in LOCKFILES)
    if not has_lockfile and pkg_path != repo_path:
        # Check root for shared lockfile
        has_lockfile = any((repo_path / lf).exists() for lf in LOCKFILES)

    # Check for type configs based on detected languages
    has_types = _has_types_fast(pkg_path, langs, repo_path)

    return Package(
        path=rel_path,
        name=name,
        languages=langs,
        package_manager=package_manager,
        has_tests=has_tests,
        has_lockfile=has_lockfile,
        has_types=has_types,
    )


def _detect_languages_fast(path: Path, max_depth: int = 2) -> set[Language]:
    """Detect languages without recursive glob (fast)."""
    langs: set[Language] = set()

    # Check manifest files first
    if (path / "package.json").exists():
        langs.add(Language.JAVASCRIPT)
        if (path / "tsconfig.json").exists():
            langs.add(Language.TYPESCRIPT)
    if (path / "pyproject.toml").exists() or (path / "setup.py").exists():
        langs.add(Language.PYTHON)
    if (path / "go.mod").exists():
        langs.add(Language.GO)
    if (path / "Cargo.toml").exists():
        langs.add(Language.RUST)
    if (path / "Gemfile").exists():
        langs.add(Language.RUBY)
    if (path / "pom.xml").exists() or (path / "build.gradle").exists():
        langs.add(Language.JAVA)
    if (path / "Package.swift").exists():
        langs.add(Language.SWIFT)
    if (path / "composer.json").exists():
        langs.add(Language.PHP)
    if (path / "mix.exs").exists():
        langs.add(Language.ELIXIR)
    if (path / "pubspec.yaml").exists():
        langs.add(Language.DART)

    # Quick scan of immediate files and first-level subdirs
    lang_extensions = {
        ".py": Language.PYTHON,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,
        ".go": Language.GO,
        ".rs": Language.RUST,
        ".rb": Language.RUBY,
        ".java": Language.JAVA,
        ".kt": Language.KOTLIN,
        ".swift": Language.SWIFT,
        ".cs": Language.CSHARP,
        ".php": Language.PHP,
        ".ex": Language.ELIXIR,
        ".exs": Language.ELIXIR,
        ".dart": Language.DART,
        ".sol": Language.JAVASCRIPT,  # Solidity often paired with JS tooling
    }

    def scan_for_extensions(dir_path: Path, depth: int = 0) -> None:
        if depth > max_depth:
            return
        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()
                    if ext in lang_extensions:
                        langs.add(lang_extensions[ext])
                elif item.is_dir() and item.name not in SKIP_DIRS and depth < max_depth:
                    scan_for_extensions(item, depth + 1)
        except PermissionError:
            pass

    scan_for_extensions(path)
    return langs


def _has_tests_fast(pkg_path: Path) -> bool:
    """Check for tests without recursive glob."""
    # Check for test directories
    for test_dir in TEST_DIRS:
        if (pkg_path / test_dir).is_dir():
            return True

    # Check for common test file patterns in src/
    src_dir = pkg_path / "src"
    if src_dir.is_dir():
        try:
            for item in src_dir.iterdir():
                if item.is_file():
                    name = item.name.lower()
                    if name.startswith("test_") or name.endswith((".test.ts", ".test.js", ".spec.ts", ".spec.js", "_test.go", "_test.py")):
                        return True
        except PermissionError:
            pass

    # Check root for test files
    try:
        for item in pkg_path.iterdir():
            if item.is_file():
                name = item.name.lower()
                if name.startswith("test_") or "test" in name or "spec" in name:
                    if item.suffix in {".py", ".js", ".ts", ".go", ".rs"}:
                        return True
    except PermissionError:
        pass

    return False


def _has_types_fast(pkg_path: Path, langs: set[Language], repo_path: Path) -> bool:
    """Check for type configs based on detected languages."""
    # TypeScript - check for tsconfig
    if Language.TYPESCRIPT in langs or Language.JAVASCRIPT in langs:
        if (pkg_path / "tsconfig.json").exists():
            return True
        if pkg_path != repo_path and (repo_path / "tsconfig.json").exists():
            return True
        # Check for tsconfig in parent (monorepo pattern)
        if (pkg_path / "tsconfig.base.json").exists():
            return True

    # Python - check for type configs
    if Language.PYTHON in langs:
        for tc in ["mypy.ini", ".mypy.ini", "pyrightconfig.json", "py.typed"]:
            if (pkg_path / tc).exists():
                return True
            if pkg_path != repo_path and (repo_path / tc).exists():
                return True
        # Check pyproject.toml for mypy config
        pyproject = pkg_path / "pyproject.toml"
        if pyproject.exists():
            try:
                if "[tool.mypy]" in pyproject.read_text():
                    return True
            except IOError:
                pass

    # Go and Rust have built-in types
    if Language.GO in langs or Language.RUST in langs:
        return True

    return False


def _detect_root_configs(repo_path: Path) -> list[Path]:
    """Detect shared config files at repository root."""
    configs: list[Path] = []
    for config_pattern, _ in SHARED_CONFIGS:
        if config_pattern.endswith("/"):
            if (repo_path / config_pattern.rstrip("/")).is_dir():
                configs.append(Path(config_pattern.rstrip("/")))
        else:
            if (repo_path / config_pattern).exists():
                configs.append(Path(config_pattern))
    return configs


def get_shared_config_checks() -> list[tuple[str, str]]:
    """Get list of shared config checks for display."""
    return [(pattern, name) for pattern, name in SHARED_CONFIGS]
