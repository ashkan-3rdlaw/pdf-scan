"""Database interfaces and implementations."""

from .analytics import MetricsRepository
from .analytics.impl import InMemoryMetricsRepository
from .backends import Backends
from .core import DocumentRepository, FindingRepository
from .core.impl import InMemoryDocumentRepository, InMemoryFindingRepository
from .factory import BackendFactory

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
    "BackendFactory",
    # Backends container
    "Backends",
]

