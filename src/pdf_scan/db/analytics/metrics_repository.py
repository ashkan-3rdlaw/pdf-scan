"""Abstract interface for metrics repository."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from pdf_scan.models import Metric


class MetricsRepository(ABC):
    """Abstract interface for metrics storage and retrieval."""

    @abstractmethod
    def store_metric(self, metric: Metric) -> None:
        """
        Store a metric record.

        Args:
            metric: Metric entity to store
        """
        pass

    @abstractmethod
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
            List of metrics
        """
        pass

    @abstractmethod
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
        pass

