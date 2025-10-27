"""Factory for creating database implementations."""

from pdf_scan.db import (
    DocumentRepository,
    FindingRepository,
    InMemoryDocumentRepository,
    InMemoryFindingRepository,
    InMemoryMetricsRepository,
    MetricsRepository,
)


class DatabaseFactory:
    """Factory for creating database implementations."""

    @staticmethod
    def create_document_repository() -> DocumentRepository:
        """Create a document repository implementation."""
        return InMemoryDocumentRepository()

    @staticmethod
    def create_finding_repository() -> FindingRepository:
        """Create a finding repository implementation."""
        return InMemoryFindingRepository()

    @staticmethod
    def create_metrics_repository() -> MetricsRepository:
        """Create a metrics repository implementation."""
        return InMemoryMetricsRepository()

    @staticmethod
    def create_all_repositories() -> tuple[DocumentRepository, FindingRepository, MetricsRepository]:
        """
        Create all repository implementations.
        
        Returns:
            Tuple of (document_repo, finding_repo, metrics_repo)
        """
        return (
            DatabaseFactory.create_document_repository(),
            DatabaseFactory.create_finding_repository(),
            DatabaseFactory.create_metrics_repository(),
        )

