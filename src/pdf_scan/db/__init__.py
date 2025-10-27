"""Database interfaces and implementations."""

from .backends import Backends
from .core import DocumentRepository, FindingRepository
from .core.impl import InMemoryDocumentRepository, InMemoryFindingRepository
from .analytics import MetricsRepository
from .analytics.impl import InMemoryMetricsRepository
from .factory import DatabaseFactory

__all__ = [
    # Core interfaces
    "DocumentRepository",
    "FindingRepository",
    # Core implementations
    "InMemoryDocumentRepository",
    "InMemoryFindingRepository",
    # Analytics interfaces
    "MetricsRepository",
    # Analytics implementations
    "InMemoryMetricsRepository",
    # Factory
    "DatabaseFactory",
    # Backends container
    "Backends",
]

