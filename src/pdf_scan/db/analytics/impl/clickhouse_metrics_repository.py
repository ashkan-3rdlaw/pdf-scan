"""ClickHouse implementation of metrics repository."""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from asynch.pool import Pool

from pdf_scan.models import Metric

from ..metrics_repository import MetricsRepository


class ClickHouseMetricsRepository(MetricsRepository):
    """ClickHouse metrics storage implementation."""

    def __init__(self, pool: Pool) -> None:
        """
        Initialize with ClickHouse connection pool.

        Args:
            pool: ClickHouse connection pool
        """
        self._pool = pool

    async def store_metric(self, metric: Metric) -> None:
        """
        Store a metric record.

        Args:
            metric: Metric entity to store
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                INSERT INTO metrics (id, operation, duration_ms, timestamp, document_id, metadata)
                VALUES
                """,
                [(
                    str(metric.id),
                    metric.operation,
                    metric.duration_ms,
                    metric.timestamp,
                    str(metric.document_id) if metric.document_id else None,
                    json.dumps(metric.metadata),
                )]
            )

    async def get_metrics(
        self,
        operation: Optional[str] = None,
        document_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Metric]:
        """
        Retrieve metrics with optional filtering and pagination.

        Args:
            operation: Optional filter by operation type
            document_id: Optional filter by document UUID
            start_time: Optional filter for metrics after this time
            end_time: Optional filter for metrics before this time
            limit: Maximum number of metrics to return
            offset: Number of metrics to skip

        Returns:
            List of metrics, sorted by timestamp descending
        """
        # Build query with conditional WHERE clauses
        where_clauses = []
        parameters = {"limit": limit, "offset": offset}
        
        if operation is not None:
            where_clauses.append("operation = %(op)s")
            parameters["op"] = operation
        
        if document_id is not None:
            where_clauses.append("document_id = %(doc_id)s")
            parameters["doc_id"] = str(document_id)
        
        if start_time is not None:
            where_clauses.append("timestamp >= %(start)s")
            parameters["start"] = start_time
        
        if end_time is not None:
            where_clauses.append("timestamp <= %(end)s")
            parameters["end"] = end_time
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f"""
        SELECT id, operation, duration_ms, timestamp, document_id, metadata
        FROM metrics
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT %(limit)s OFFSET %(offset)s
        """
        
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(query, parameters)
            rows = await cursor.fetchall()
            return [self._row_to_metric(row) for row in rows]

    async def get_average_duration(
        self,
        operation: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        """
        Calculate average duration for an operation.

        Args:
            operation: Operation type to calculate average for
            start_time: Optional filter for metrics after this time
            end_time: Optional filter for metrics before this time

        Returns:
            Average duration in milliseconds, 0.0 if no metrics found
        """
        # Build query with conditional WHERE clauses
        where_clauses = ["operation = %(op)s"]
        parameters = {"op": operation}
        
        if start_time is not None:
            where_clauses.append("timestamp >= %(start)s")
            parameters["start"] = start_time
        
        if end_time is not None:
            where_clauses.append("timestamp <= %(end)s")
            parameters["end"] = end_time
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT avg(duration_ms) as avg_duration
        FROM metrics
        WHERE {where_clause}
        """
        
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(query, parameters)
            row = await cursor.fetchone()
            
            if not row or row[0] is None:
                return 0.0
            
            return float(row[0])

    def _row_to_metric(self, row: tuple) -> Metric:
        """
        Convert a database row to a Metric entity.

        Args:
            row: Tuple containing metric data

        Returns:
            Metric entity
        """
        # Parse metadata JSON string back to dict
        metadata = json.loads(row[5]) if row[5] else {}
        
        return Metric(
            id=UUID(row[0]) if isinstance(row[0], str) else row[0],
            operation=row[1],
            duration_ms=row[2],
            timestamp=row[3],
            document_id=UUID(row[4]) if row[4] and isinstance(row[4], str) else row[4],
            metadata=metadata,
        )

