"""Language detection for repository analysis."""

from collections import Counter
from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    JAVA = "java"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    PHP = "php"
    ELIXIR = "elixir"
    SCALA = "scala"
    HASKELL = "haskell"
    LUA = "lua"
    DART = "dart"
    ZIG = "zig"
    UNKNOWN = "unknown"


# File extension to language mapping
EXTENSION_MAP: dict[str, Language] = {
    # Python
    ".py": Language.PYTHON,
    ".pyi": Language.PYTHON,
    ".pyx": Language.PYTHON,
    # JavaScript
    ".js": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".cjs": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    # TypeScript
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
    ".mts": Language.TYPESCRIPT,
    ".cts": Language.TYPESCRIPT,
    # Go
    ".go": Language.GO,
    # Rust
    ".rs": Language.RUST,
    # Ruby
    ".rb": Language.RUBY,
    ".rake": Language.RUBY,
    ".gemspec": Language.RUBY,
    # Java
    ".java": Language.JAVA,
    # Kotlin
    ".kt": Language.KOTLIN,
    ".kts": Language.KOTLIN,
    # Swift
    ".swift": Language.SWIFT,
    # C#
    ".cs": Language.CSHARP,
    # C++
    ".cpp": Language.CPP,
    ".cc": Language.CPP,
    ".cxx": Language.CPP,
    ".hpp": Language.CPP,
    ".hxx": Language.CPP,
    # C
    ".c": Language.C,
    ".h": Language.C,
    # PHP
    ".php": Language.PHP,
    # Elixir
    ".ex": Language.ELIXIR,
    ".exs": Language.ELIXIR,
    # Scala
    ".scala": Language.SCALA,
    ".sc": Language.SCALA,
    # Haskell
    ".hs": Language.HASKELL,
    ".lhs": Language.HASKELL,
    # Lua
    ".lua": Language.LUA,
    # Dart
    ".dart": Language.DART,
    # Zig
    ".zig": Language.ZIG,
}

# Directories to skip during detection
SKIP_DIRS = {
    "__pycache__", ".git", ".svn", ".hg",
    "node_modules", ".venv", "venv", "env",
    "build", "dist", "target", "out", "bin", "obj",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "vendor", "deps", "_build", ".bundle",
    ".next", ".nuxt", ".output",
}

# Threshold for considering a language "significant" in the repo
SIGNIFICANT_LANGUAGE_THRESHOLD = 0.1  # 10% of files


@dataclass
class LanguageStats:
    """Statistics about detected languages."""

    primary: Language
    languages: dict[Language, int]  # Language -> file count
    total_files: int
    confidence: float  # 0-1, how dominant the primary language is

    @property
    def is_multi_language(self) -> bool:
        """True if multiple significant languages detected."""
        if self.total_files == 0:
            return False
        significant = sum(
            1 for count in self.languages.values()
            if count / self.total_files > SIGNIFICANT_LANGUAGE_THRESHOLD
        )
        return significant > 1

    def has_language(self, lang: Language) -> bool:
        """Check if a language is present in the repo."""
        return lang in self.languages and self.languages[lang] > 0

    def language_ratio(self, lang: Language) -> float:
        """Get the ratio of files for a language (0-1)."""
        if self.total_files == 0:
            return 0.0
        return self.languages.get(lang, 0) / self.total_files

    def primary_languages(self, threshold: float = SIGNIFICANT_LANGUAGE_THRESHOLD) -> list[Language]:
        """Get list of primary/significant languages in the repo.

        Args:
            threshold: Minimum ratio of files to be considered significant.

        Returns:
            List of languages sorted by file count (most files first).
        """
        if self.total_files == 0:
            return []

        significant = [
            (lang, count) for lang, count in self.languages.items()
            if count / self.total_files >= threshold
        ]
        # Sort by count descending
        significant.sort(key=lambda x: x[1], reverse=True)
        return [lang for lang, _ in significant]


def detect_languages(repo_path: Path, max_files: int = 1000) -> LanguageStats:
    """Detect programming languages used in a repository.

    Args:
        repo_path: Path to repository root
        max_files: Maximum files to scan (for performance)

    Returns:
        LanguageStats with primary language and breakdown
    """
    counter: Counter[Language] = Counter()
    files_scanned = 0

    for file_path in repo_path.rglob("*"):
        if files_scanned >= max_files:
            break

        # Skip directories in exclusion list
        if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
            continue

        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        if ext in EXTENSION_MAP:
            counter[EXTENSION_MAP[ext]] += 1
            files_scanned += 1

    total_files = sum(counter.values())

    if total_files == 0:
        return LanguageStats(
            primary=Language.UNKNOWN,
            languages={},
            total_files=0,
            confidence=0.0,
        )

    # Get primary language
    primary, primary_count = counter.most_common(1)[0]
    confidence = primary_count / total_files

    return LanguageStats(
        primary=primary,
        languages=dict(counter),
        total_files=total_files,
        confidence=confidence,
    )


def get_language_family(lang: Language) -> set[Language]:
    """Get related languages (e.g., JS and TS are related)."""
    families = {
        frozenset({Language.JAVASCRIPT, Language.TYPESCRIPT}),
        frozenset({Language.C, Language.CPP}),
        frozenset({Language.JAVA, Language.KOTLIN, Language.SCALA}),
    }

    for family in families:
        if lang in family:
            return set(family)

    return {lang}
