"""ClickHouse implementation of finding repository."""

from typing import Optional
from uuid import UUID

from asynch.pool import Pool

from pdf_scan.models import Finding, FindingType

from ..finding_repository import FindingRepository


class ClickHouseFindingRepository(FindingRepository):
    """ClickHouse finding storage implementation."""

    def __init__(self, pool: Pool) -> None:
        """
        Initialize with ClickHouse connection pool.

        Args:
            pool: ClickHouse connection pool
        """
        self._pool = pool

    async def store_finding(self, finding: Finding) -> None:
        """
        Store a finding record.

        Args:
            finding: Finding entity to store
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                INSERT INTO findings (id, document_id, finding_type, location, confidence)
                VALUES
                """,
                [(
                    str(finding.id),
                    str(finding.document_id),
                    finding.finding_type.value,
                    finding.location,
                    finding.confidence,
                )]
            )

    async def get_findings(self, document_id: UUID) -> list[Finding]:
        """
        Retrieve all findings for a specific document.

        Args:
            document_id: UUID of the document

        Returns:
            List of findings for the document, sorted by confidence descending
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                SELECT id, document_id, finding_type, location, confidence, created_at
                FROM findings
                WHERE document_id = %(doc_id)s
                ORDER BY confidence DESC
                """,
                {"doc_id": str(document_id)}
            )
            rows = await cursor.fetchall()
            return [self._row_to_finding(row) for row in rows]

    async def get_all_findings(
        self, limit: int = 100, offset: int = 0, finding_type: Optional[FindingType] = None
    ) -> list[Finding]:
        """
        Retrieve findings with pagination and optional filtering.

        Args:
            limit: Maximum number of findings to return
            offset: Number of findings to skip
            finding_type: Optional filter by finding type

        Returns:
            List of findings, sorted by confidence descending
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            if finding_type is not None:
                await cursor.execute(
                    """
                    SELECT id, document_id, finding_type, location, confidence, created_at
                    FROM findings
                    WHERE finding_type = %(f_type)s
                    ORDER BY confidence DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                    """,
                    {
                        "f_type": finding_type.value,
                        "limit": limit,
                        "offset": offset
                    }
                )
            else:
                await cursor.execute(
                    """
                    SELECT id, document_id, finding_type, location, confidence, created_at
                    FROM findings
                    ORDER BY confidence DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                    """,
                    {"limit": limit, "offset": offset}
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_finding(row) for row in rows]

    async def count_findings(self, document_id: Optional[UUID] = None) -> int:
        """
        Count findings, optionally filtered by document.

        Args:
            document_id: Optional document UUID to filter by

        Returns:
            Number of findings
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            if document_id is not None:
                await cursor.execute(
                    """
                    SELECT count() as cnt
                    FROM findings
                    WHERE document_id = %(doc_id)s
                    """,
                    {"doc_id": str(document_id)}
                )
            else:
                await cursor.execute("SELECT count() as cnt FROM findings")
            
            row = await cursor.fetchone()
            return row[0] if row else 0

    def _row_to_finding(self, row: tuple) -> Finding:
        """
        Convert a database row to a Finding entity.

        Args:
            row: Tuple containing finding data

        Returns:
            Finding entity
        """
        return Finding(
            id=UUID(row[0]) if isinstance(row[0], str) else row[0],
            document_id=UUID(row[1]) if isinstance(row[1], str) else row[1],
            finding_type=FindingType(row[2]),
            location=row[3],
            confidence=row[4],
        )

