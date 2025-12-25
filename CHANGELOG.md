# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2024-12-25

### Fixed

- **Performance**: Glob patterns now exclude `node_modules/`, `.git/`, `vendor/`, and other heavy directories
- Fixes scanner hanging indefinitely on large monorepos with multiple `node_modules/` directories
- Added `_is_excluded()` and `_filtered_glob()` helpers for consistent exclusion logic

## [0.2.0] - 2024-12-25

### Added

- **Package Detection**: Automatic detection of polyrepo/monorepo structures
- **Per-Package Scoring**: Each package scored independently based on its languages
- **Shared Infrastructure**: Recognition of root-level configs that benefit all packages
- **New Output Tables**: Per-package breakdown and shared infrastructure status
- **Package Models**: `Package`, `RepoStructure`, `PackageScore`, `SharedInfraFinding`
- **Check Scopes**: Checks can now specify `root`, `package`, or `any` scope
- **Aggregation Formula**: Weighted average of package scores with shared config bonuses

### Changed

- Engine now detects repo structure before scanning
- Console output shows package breakdown for multi-package repos
- Scoring algorithm accounts for package-level language filtering

### Fixed

- Misleading low scores for polyrepo/monorepo structures
- Python checks no longer penalize JS-only packages and vice versa
- Configs in subdirectories now properly detected

## [0.1.1] - 2024-12-25

### Fixed

- **Polyrepo/monorepo support**: Scanner now searches subdirectories when configs aren't at root level
- Fixes misleading low scores for repos with nested project structures

## [0.1.0] - 2024-12-25

### Added

- Initial release of Agent Readiness Score CLI
- 8 scoring categories with weighted scoring:
  - Testing (20%)
  - Style & Validation (15%)
  - Dev Environments (15%)
  - Build Systems (10%)
  - Observability (10%)
  - Dependencies (10%)
  - Documentation (10%)
  - Static Typing (10%)
- Multi-language support for 15+ languages:
  - Python, JavaScript/TypeScript, Go, Rust
  - Ruby, Java/Kotlin, Swift, C#
  - C/C++, PHP, Elixir, Dart
  - Haskell, Scala, Zig
- Rich console output with progress bars and tables
- JSON output format for CI/CD integration
- Minimum score threshold (`--min-score`) for CI pipelines
- Verbose mode for detailed findings
- Plugin-based scanner architecture with auto-registration
- Comprehensive documentation

### Technical Details

- Pure Python implementation (no external scanning tools required)
- Uses Typer for CLI and Rich for console output
- Glob pattern matching for file detection
- Weighted scoring algorithm with per-category normalization
- Grading scale: A (90-100), B (80-89), C (70-79), D (60-69), F (0-59)

[Unreleased]: https://github.com/yourusername/agent-readiness-score/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/agent-readiness-score/releases/tag/v0.1.0
