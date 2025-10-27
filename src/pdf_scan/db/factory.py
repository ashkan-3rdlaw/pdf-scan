"""Factory for creating backend implementations."""

from pdf_scan.db import (
    DocumentRepository,
    FindingRepository,
    InMemoryDocumentRepository,
    InMemoryFindingRepository,
    InMemoryMetricsRepository,
    MetricsRepository,
)
from pdf_scan.scanner import PDFScannerInterface, RegexPDFScanner


class BackendFactory:
    """Factory for creating backend implementations (repositories and scanner)."""

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
    def create_scanner() -> PDFScannerInterface:
        """Create a PDF scanner implementation."""
        return RegexPDFScanner()

    @staticmethod
    def create_all_repositories() -> tuple[DocumentRepository, FindingRepository, MetricsRepository]:
        """
        Create all repository implementations.
        
        Returns:
            Tuple of (document_repo, finding_repo, metrics_repo)
        """
        return (
            BackendFactory.create_document_repository(),
            BackendFactory.create_finding_repository(),
            BackendFactory.create_metrics_repository(),
        )

    @staticmethod
    def create_backends():
        """
        Create a complete Backends instance with all dependencies.
        
        Returns:
            Backends instance with in-memory repositories and regex scanner
        """
        from .backends import Backends
        
        return Backends(
            document_repo=BackendFactory.create_document_repository(),
            finding_repo=BackendFactory.create_finding_repository(),
            metrics_repo=BackendFactory.create_metrics_repository(),
            scanner=BackendFactory.create_scanner(),
        )

