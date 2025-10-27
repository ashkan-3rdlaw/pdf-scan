"""Tests for BackendFactory."""

from pdf_scan.db import BackendFactory


class TestBackendFactory:
    """Test suite for BackendFactory."""

    def test_create_document_repository(self):
        """Test creating a document repository."""
        repo = BackendFactory.create_document_repository(backend="memory")
        assert repo is not None
        assert hasattr(repo, 'store_document')
        assert hasattr(repo, 'get_document')
        assert hasattr(repo, 'update_document_status')
        assert hasattr(repo, 'list_documents')

    def test_create_finding_repository(self):
        """Test creating a finding repository."""
        repo = BackendFactory.create_finding_repository(backend="memory")
        assert repo is not None
        assert hasattr(repo, 'store_finding')
        assert hasattr(repo, 'get_findings')
        assert hasattr(repo, 'get_all_findings')
        assert hasattr(repo, 'count_findings')

    def test_create_metrics_repository(self):
        """Test creating a metrics repository."""
        repo = BackendFactory.create_metrics_repository(backend="memory")
        assert repo is not None
        assert hasattr(repo, 'store_metric')
        assert hasattr(repo, 'get_metrics')
        assert hasattr(repo, 'get_average_duration')

    def test_create_all_repositories(self):
        """Test creating all repositories at once."""
        doc_repo, finding_repo, metrics_repo = BackendFactory.create_all_repositories(backend="memory")
        
        assert doc_repo is not None
        assert finding_repo is not None
        assert metrics_repo is not None
        
        # Verify they're different instances
        assert doc_repo is not finding_repo
        assert doc_repo is not metrics_repo
        assert finding_repo is not metrics_repo

    def test_factory_returns_different_instances(self):
        """Test that factory returns different instances each time."""
        repo1 = BackendFactory.create_document_repository(backend="memory")
        repo2 = BackendFactory.create_document_repository(backend="memory")
        
        assert repo1 is not repo2
        assert type(repo1) == type(repo2)

    def test_repositories_are_in_memory_implementations(self):
        """Test that factory returns in-memory implementations."""
        doc_repo = BackendFactory.create_document_repository(backend="memory")
        finding_repo = BackendFactory.create_finding_repository(backend="memory")
        metrics_repo = BackendFactory.create_metrics_repository(backend="memory")
        
        assert 'InMemory' in type(doc_repo).__name__
        assert 'InMemory' in type(finding_repo).__name__
        assert 'InMemory' in type(metrics_repo).__name__

    def test_create_scanner(self):
        """Test creating a scanner."""
        scanner = BackendFactory.create_scanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan_pdf')
        assert hasattr(scanner, 'get_supported_patterns')
        assert 'Regex' in type(scanner).__name__

    def test_create_backends(self):
        """Test creating a complete backends instance."""
        backends = BackendFactory.create_backends(backend="memory")
        assert backends is not None
        assert backends.document is not None
        assert backends.finding is not None
        assert backends.metrics is not None
        assert backends.scanner is not None

