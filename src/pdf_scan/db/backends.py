"""Backends class for managing database and scanner dependencies."""

from pdf_scan.scanner import PDFScannerInterface

from .analytics import MetricsRepository
from .core import DocumentRepository, FindingRepository


class Backends:
    """Container for all database and scanner backend dependencies."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        finding_repo: FindingRepository,
        metrics_repo: MetricsRepository,
        scanner: PDFScannerInterface,
    ):
        """
        Initialize backends with repository and scanner dependencies.

        Args:
            document_repo: Document repository implementation
            finding_repo: Finding repository implementation
            metrics_repo: Metrics repository implementation
            scanner: PDF scanner implementation
        """
        self.document = document_repo
        self.finding = finding_repo
        self.metrics = metrics_repo
        self.scanner = scanner

    def __repr__(self) -> str:
        """String representation of backends."""
        return (
            f"Backends("
            f"document={type(self.document).__name__}, "
            f"finding={type(self.finding).__name__}, "
            f"metrics={type(self.metrics).__name__}, "
            f"scanner={type(self.scanner).__name__}"
            f")"
        )

