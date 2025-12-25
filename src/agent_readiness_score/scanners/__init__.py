"""Scanner implementations.

All scanners are auto-registered when this module is imported.
"""

# Import all scanners to trigger registration
from agent_readiness_score.scanners.style import StyleScanner
from agent_readiness_score.scanners.build import BuildScanner
from agent_readiness_score.scanners.devenv import DevEnvScanner
from agent_readiness_score.scanners.observability import ObservabilityScanner
from agent_readiness_score.scanners.testing import TestingScanner
from agent_readiness_score.scanners.dependencies import DependenciesScanner
from agent_readiness_score.scanners.documentation import DocumentationScanner
from agent_readiness_score.scanners.typing import TypingScanner

__all__ = [
    "StyleScanner",
    "BuildScanner",
    "DevEnvScanner",
    "ObservabilityScanner",
    "TestingScanner",
    "DependenciesScanner",
    "DocumentationScanner",
    "TypingScanner",
]
