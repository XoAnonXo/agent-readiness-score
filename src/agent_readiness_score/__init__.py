"""Agent-Ready: Repository readiness scanner for AI agents."""

__version__ = "0.1.0"

# Re-export main components for convenience
from agent_readiness_score.core import (
    Category,
    CategoryScore,
    Finding,
    ScanReport,
    CATEGORY_WEIGHTS,
    calculate_grade,
    BaseScanner,
    ScannerRegistry,
    ScanEngine,
    Language,
    LanguageStats,
    detect_languages,
)
from agent_readiness_score.output import ConsoleFormatter, JSONFormatter

__all__ = [
    "__version__",
    # Core
    "Category",
    "CategoryScore",
    "Finding",
    "ScanReport",
    "CATEGORY_WEIGHTS",
    "calculate_grade",
    "BaseScanner",
    "ScannerRegistry",
    "ScanEngine",
    "Language",
    "LanguageStats",
    "detect_languages",
    # Output
    "ConsoleFormatter",
    "JSONFormatter",
]
