"""Tests for file validation."""

import pytest

from pdf_scan.validation import FileValidator
from pdf_scan.validation.file_validator import ValidationError


class TestFileValidator:
    """Tests for FileValidator class."""

    def test_validate_file_provided_with_valid_filename(self):
        """Test validation passes with a valid filename."""
        # Should not raise
        FileValidator.validate_file_provided("test.pdf")

    def test_validate_file_provided_with_none(self):
        """Test validation fails when filename is None."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_file_provided(None)
        
        assert exc_info.value.code == "MISSING_FILENAME"
        assert "required" in exc_info.value.message.lower()

    def test_validate_file_provided_with_empty_string(self):
        """Test validation fails when filename is empty."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_file_provided("")
        
        assert exc_info.value.code == "MISSING_FILENAME"

    def test_validate_extension_with_pdf(self):
        """Test validation passes with .pdf extension."""
        # Should not raise
        FileValidator.validate_extension("document.pdf")
        FileValidator.validate_extension("document.PDF")  # Case insensitive

    def test_validate_extension_with_invalid_extension(self):
        """Test validation fails with non-PDF extension."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_extension("document.txt")
        
        assert exc_info.value.code == "INVALID_FILE_TYPE"
        assert "PDF" in exc_info.value.message

    def test_validate_extension_with_no_extension(self):
        """Test validation fails when file has no extension."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_extension("document")
        
        assert exc_info.value.code == "INVALID_FILE_TYPE"

    def test_validate_content_type_with_valid_type(self):
        """Test validation passes with valid content type."""
        # Should not raise
        FileValidator.validate_content_type("application/pdf")

    def test_validate_content_type_with_none(self):
        """Test validation passes when content type is None."""
        # Should not raise - content type is optional
        FileValidator.validate_content_type(None)

    def test_validate_content_type_with_invalid_type(self):
        """Test validation fails with invalid content type."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_content_type("text/plain")
        
        assert exc_info.value.code == "INVALID_CONTENT_TYPE"
        assert "text/plain" in exc_info.value.message

    def test_validate_file_size_with_valid_size(self):
        """Test validation passes with valid file size."""
        # Should not raise
        FileValidator.validate_file_size(1024)  # 1KB
        FileValidator.validate_file_size(5 * 1024 * 1024)  # 5MB

    def test_validate_file_size_with_empty_file(self):
        """Test validation fails with empty file."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_file_size(0)
        
        assert exc_info.value.code == "EMPTY_FILE"
        assert "empty" in exc_info.value.message.lower()

    def test_validate_file_size_with_file_too_large(self):
        """Test validation fails when file exceeds max size."""
        too_large = 11 * 1024 * 1024  # 11MB
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_file_size(too_large)
        
        assert exc_info.value.code == "FILE_TOO_LARGE"
        assert "exceeds" in exc_info.value.message.lower()

    def test_validate_file_size_at_max_limit(self):
        """Test validation passes at exactly the max size."""
        max_size = 10 * 1024 * 1024  # Exactly 10MB
        # Should not raise
        FileValidator.validate_file_size(max_size)

    def test_validate_pdf_upload_with_valid_file(self):
        """Test complete validation with valid PDF."""
        # Should not raise
        FileValidator.validate_pdf_upload(
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024,
        )

    def test_validate_pdf_upload_with_none_content_type(self):
        """Test complete validation with None content type."""
        # Should not raise - content type is optional
        FileValidator.validate_pdf_upload(
            filename="test.pdf",
            content_type=None,
            file_size=1024,
        )

    def test_validate_pdf_upload_fails_on_invalid_extension(self):
        """Test complete validation fails on invalid extension."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_pdf_upload(
                filename="test.txt",
                content_type="application/pdf",
                file_size=1024,
            )
        
        assert exc_info.value.code == "INVALID_FILE_TYPE"

    def test_validate_pdf_upload_fails_on_empty_file(self):
        """Test complete validation fails on empty file."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_pdf_upload(
                filename="test.pdf",
                content_type="application/pdf",
                file_size=0,
            )
        
        assert exc_info.value.code == "EMPTY_FILE"

    def test_validate_pdf_upload_fails_on_large_file(self):
        """Test complete validation fails on large file."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_pdf_upload(
                filename="test.pdf",
                content_type="application/pdf",
                file_size=11 * 1024 * 1024,
            )
        
        assert exc_info.value.code == "FILE_TOO_LARGE"

    def test_validate_pdf_upload_fails_on_invalid_content_type(self):
        """Test complete validation fails on invalid content type."""
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_pdf_upload(
                filename="test.pdf",
                content_type="text/plain",
                file_size=1024,
            )
        
        assert exc_info.value.code == "INVALID_CONTENT_TYPE"

    def test_validation_error_attributes(self):
        """Test ValidationError has correct attributes."""
        error = ValidationError("Test message", "TEST_CODE")
        
        assert error.message == "Test message"
        assert error.code == "TEST_CODE"
        assert str(error) == "Test message"

