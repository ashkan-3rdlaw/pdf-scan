"""Factory for creating backend implementations."""

import os
from typing import Optional

from asynch import Pool
from dotenv import load_dotenv

from pdf_scan.db import (
    DocumentRepository,
    FindingRepository,
    InMemoryDocumentRepository,
    InMemoryFindingRepository,
    InMemoryMetricsRepository,
    MetricsRepository,
)
from pdf_scan.db.analytics.impl import ClickHouseMetricsRepository
from pdf_scan.db.core.impl import (
    ClickHouseDocumentRepository,
    ClickHouseFindingRepository,
)
from pdf_scan.scanner import PDFScannerInterface, RegexPDFScanner

# Load environment variables
load_dotenv()


class BackendFactory:
    """Factory for creating backend implementations (repositories and scanner)."""

    @staticmethod
    def get_backend_type() -> str:
        """Get the database backend type from environment variables."""
        return os.getenv("DATABASE_BACKEND", "memory").lower()

    @staticmethod
    async def create_clickhouse_pool(
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        minsize: Optional[int] = None,
        maxsize: Optional[int] = None,
    ) -> Pool:
        """
        Create a ClickHouse connection pool using environment variables.

        Args:
            host: ClickHouse server host (defaults to CLICKHOUSE_HOST env var)
            port: ClickHouse native TCP port (defaults to CLICKHOUSE_PORT env var)
            username: Database username (defaults to CLICKHOUSE_USERNAME env var)
            password: Database password (defaults to CLICKHOUSE_PASSWORD env var)
            database: Database name (defaults to CLICKHOUSE_DATABASE env var)
            minsize: Minimum number of connections in pool (defaults to CLICKHOUSE_POOL_MINSIZE env var)
            maxsize: Maximum number of connections in pool (defaults to CLICKHOUSE_POOL_MAXSIZE env var)

        Returns:
            ClickHouse connection pool
        """
        # Use environment variables as defaults
        config = {
            "host": host or os.getenv("CLICKHOUSE_HOST", "localhost"),
            "port": port or int(os.getenv("CLICKHOUSE_PORT", "9000")),
            "user": username or os.getenv("CLICKHOUSE_USERNAME", "pdf_user"),
            "password": password or os.getenv("CLICKHOUSE_PASSWORD", "pdf_password"),
            "database": database or os.getenv("CLICKHOUSE_DATABASE", "pdf_scan"),
            "minsize": minsize or int(os.getenv("CLICKHOUSE_POOL_MINSIZE", "5")),
            "maxsize": maxsize or int(os.getenv("CLICKHOUSE_POOL_MAXSIZE", "20")),
        }
        
        pool = Pool(**config)
        await pool.startup()
        return pool

    @staticmethod
    def create_document_repository(
        backend: str = "memory", pool: Optional[Pool] = None
    ) -> DocumentRepository:
        """
        Create a document repository implementation.

        Args:
            backend: Backend type ("memory" or "clickhouse")
            pool: Optional ClickHouse connection pool (required if backend="clickhouse")

        Returns:
            DocumentRepository implementation
        """
        if backend == "clickhouse":
            if pool is None:
                raise ValueError("ClickHouse pool is required for clickhouse backend")
            return ClickHouseDocumentRepository(pool)
        return InMemoryDocumentRepository()

    @staticmethod
    def create_finding_repository(
        backend: str = "memory", pool: Optional[Pool] = None
    ) -> FindingRepository:
        """
        Create a finding repository implementation.

        Args:
            backend: Backend type ("memory" or "clickhouse")
            pool: Optional ClickHouse connection pool (required if backend="clickhouse")

        Returns:
            FindingRepository implementation
        """
        if backend == "clickhouse":
            if pool is None:
                raise ValueError("ClickHouse pool is required for clickhouse backend")
            return ClickHouseFindingRepository(pool)
        return InMemoryFindingRepository()

    @staticmethod
    def create_metrics_repository(
        backend: str = "memory", pool: Optional[Pool] = None
    ) -> MetricsRepository:
        """
        Create a metrics repository implementation.

        Args:
            backend: Backend type ("memory" or "clickhouse")
            pool: Optional ClickHouse connection pool (required if backend="clickhouse")

        Returns:
            MetricsRepository implementation
        """
        if backend == "clickhouse":
            if pool is None:
                raise ValueError("ClickHouse pool is required for clickhouse backend")
            return ClickHouseMetricsRepository(pool)
        return InMemoryMetricsRepository()

    @staticmethod
    def create_scanner() -> PDFScannerInterface:
        """Create a PDF scanner implementation."""
        return RegexPDFScanner()

    @staticmethod
    def create_all_repositories(
        backend: str = "memory", pool: Optional[Pool] = None
    ) -> tuple[DocumentRepository, FindingRepository, MetricsRepository]:
        """
        Create all repository implementations.

        Args:
            backend: Backend type ("memory" or "clickhouse")
            pool: Optional ClickHouse connection pool (required if backend="clickhouse")

        Returns:
            Tuple of (document_repo, finding_repo, metrics_repo)
        """
        return (
            BackendFactory.create_document_repository(backend, pool),
            BackendFactory.create_finding_repository(backend, pool),
            BackendFactory.create_metrics_repository(backend, pool),
        )

    @staticmethod
    def create_backends(backend: Optional[str] = None, pool: Optional[Pool] = None):
        """
        Create a complete Backends instance with all dependencies.

        Args:
            backend: Backend type ("memory" or "clickhouse"). If None, uses DATABASE_BACKEND env var.
            pool: Optional ClickHouse connection pool (required if backend="clickhouse")

        Returns:
            Backends instance with repositories and scanner
        """
        from .backends import Backends

        # Use environment variable if backend not specified
        backend_type = backend or BackendFactory.get_backend_type()

        return Backends(
            document_repo=BackendFactory.create_document_repository(backend_type, pool),
            finding_repo=BackendFactory.create_finding_repository(backend_type, pool),
            metrics_repo=BackendFactory.create_metrics_repository(backend_type, pool),
            scanner=BackendFactory.create_scanner(),
        )

