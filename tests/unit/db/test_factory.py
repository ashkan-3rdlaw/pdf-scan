"""Tests for DatabaseFactory."""

from pdf_scan.db import DatabaseFactory


class TestDatabaseFactory:
    """Test suite for DatabaseFactory."""

    def test_create_document_repository(self):
        """Test creating a document repository."""
        repo = DatabaseFactory.create_document_repository()
        assert repo is not None
        assert hasattr(repo, 'store_document')
        assert hasattr(repo, 'get_document')
        assert hasattr(repo, 'update_document_status')
        assert hasattr(repo, 'list_documents')

    def test_create_finding_repository(self):
        """Test creating a finding repository."""
        repo = DatabaseFactory.create_finding_repository()
        assert repo is not None
        assert hasattr(repo, 'store_finding')
        assert hasattr(repo, 'get_findings')
        assert hasattr(repo, 'get_all_findings')
        assert hasattr(repo, 'count_findings')

    def test_create_metrics_repository(self):
        """Test creating a metrics repository."""
        repo = DatabaseFactory.create_metrics_repository()
        assert repo is not None
        assert hasattr(repo, 'store_metric')
        assert hasattr(repo, 'get_metrics')
        assert hasattr(repo, 'get_average_duration')

    def test_create_all_repositories(self):
        """Test creating all repositories at once."""
        doc_repo, finding_repo, metrics_repo = DatabaseFactory.create_all_repositories()
        
        assert doc_repo is not None
        assert finding_repo is not None
        assert metrics_repo is not None
        
        # Verify they're different instances
        assert doc_repo is not finding_repo
        assert doc_repo is not metrics_repo
        assert finding_repo is not metrics_repo

    def test_factory_returns_different_instances(self):
        """Test that factory returns different instances each time."""
        repo1 = DatabaseFactory.create_document_repository()
        repo2 = DatabaseFactory.create_document_repository()
        
        assert repo1 is not repo2
        assert type(repo1) == type(repo2)

    def test_repositories_are_in_memory_implementations(self):
        """Test that factory returns in-memory implementations."""
        doc_repo = DatabaseFactory.create_document_repository()
        finding_repo = DatabaseFactory.create_finding_repository()
        metrics_repo = DatabaseFactory.create_metrics_repository()
        
        assert 'InMemory' in type(doc_repo).__name__
        assert 'InMemory' in type(finding_repo).__name__
        assert 'InMemory' in type(metrics_repo).__name__

