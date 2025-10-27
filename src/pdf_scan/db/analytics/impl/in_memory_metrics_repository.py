"""In-memory implementation of metrics repository."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pdf_scan.models import Metric

from ..metrics_repository import MetricsRepository


class InMemoryMetricsRepository(MetricsRepository):
    """In-memory metrics storage using Python dict."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._metrics: dict[UUID, Metric] = {}

    def store_metric(self, metric: Metric) -> None:
        """
        Store a metric record.

        Args:
            metric: Metric entity to store
        """
        self._metrics[metric.id] = metric

    def get_metrics(
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
        # Apply filters
        filtered_metrics = list(self._metrics.values())

        if operation is not None:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]

        if document_id is not None:
            filtered_metrics = [
                m for m in filtered_metrics if m.document_id == document_id
            ]

        if start_time is not None:
            filtered_metrics = [
                m for m in filtered_metrics if m.timestamp >= start_time
            ]

        if end_time is not None:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]

        # Sort by timestamp descending (most recent first)
        sorted_metrics = sorted(
            filtered_metrics, key=lambda m: m.timestamp, reverse=True
        )
        return sorted_metrics[offset : offset + limit]

    def get_average_duration(
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
        # Filter by operation and time range
        filtered_metrics = [m for m in self._metrics.values() if m.operation == operation]

        if start_time is not None:
            filtered_metrics = [
                m for m in filtered_metrics if m.timestamp >= start_time
            ]

        if end_time is not None:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]

        if not filtered_metrics:
            return 0.0

        total_duration = sum(m.duration_ms for m in filtered_metrics)
        return total_duration / len(filtered_metrics)

