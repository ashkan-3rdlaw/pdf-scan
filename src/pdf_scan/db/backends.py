"""Backends class for managing database dependencies."""

from .core import DocumentRepository, FindingRepository
from .analytics import MetricsRepository


class Backends:
    """Container for all database backend dependencies."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        finding_repo: FindingRepository,
        metrics_repo: MetricsRepository,
    ):
        """
        Initialize backends with repository dependencies.

        Args:
            document_repo: Document repository implementation
            finding_repo: Finding repository implementation
            metrics_repo: Metrics repository implementation
        """
        self.document = document_repo
        self.finding = finding_repo
        self.metrics = metrics_repo

    @classmethod
    def create_in_memory(cls) -> "Backends":
        """
        Create backends with in-memory implementations.

        Returns:
            Backends instance with in-memory repositories
        """
        from .factory import DatabaseFactory

        return cls(
            document_repo=DatabaseFactory.create_document_repository(),
            finding_repo=DatabaseFactory.create_finding_repository(),
            metrics_repo=DatabaseFactory.create_metrics_repository(),
        )

    @classmethod
    def create_from_factory(cls) -> "Backends":
        """
        Create backends using the database factory.

        This is an alias for create_in_memory() for backward compatibility.
        In the future, this could be extended to support different backend types.

        Returns:
            Backends instance with factory-created repositories
        """
        return cls.create_in_memory()

    def __repr__(self) -> str:
        """String representation of backends."""
        return (
            f"Backends("
            f"document={type(self.document).__name__}, "
            f"finding={type(self.finding).__name__}, "
            f"metrics={type(self.metrics).__name__}"
            f")"
        )

