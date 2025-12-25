"""Scanner registry for auto-registration."""

from typing import Type

from agent_readiness_score.core.scanner import Scanner, BaseScanner
from agent_readiness_score.core.models import Category


class ScannerRegistry:
    """Registry for scanner implementations."""

    _scanners: dict[Category, Scanner] = {}

    @classmethod
    def register(cls, scanner_class: Type[BaseScanner]) -> Type[BaseScanner]:
        """Decorator to register a scanner class.

        Usage:
            @ScannerRegistry.register
            class MyScanner(BaseScanner):
                ...
        """
        instance = scanner_class()
        cls._scanners[instance.category] = instance
        return scanner_class

    @classmethod
    def get(cls, category: Category) -> Scanner | None:
        """Get scanner for a specific category."""
        return cls._scanners.get(category)

    @classmethod
    def get_all(cls) -> list[Scanner]:
        """Get all registered scanners."""
        return list(cls._scanners.values())

    @classmethod
    def categories(cls) -> list[Category]:
        """Get all categories with registered scanners."""
        return list(cls._scanners.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered scanners (useful for testing)."""
        cls._scanners.clear()
