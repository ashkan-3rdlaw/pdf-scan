"""File validation utilities for PDF uploads."""

from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class FileValidator:
    """Validator for uploaded PDF files."""

    # Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_CONTENT_TYPES = ["application/pdf"]
    ALLOWED_EXTENSIONS = [".pdf"]

    @staticmethod
    def validate_file_provided(filename: Optional[str]) -> None:
        """
        Validate that a file with a filename is provided.
        
        Args:
            filename: The filename to validate
            
        Raises:
            ValidationError: If filename is None or empty
        """
        if not filename:
            raise ValidationError(
                "Filename is required",
                "MISSING_FILENAME",
            )

    @staticmethod
    def validate_extension(filename: str) -> None:
        """
        Validate that the file has an allowed extension.
        
        Args:
            filename: The filename to check
            
        Raises:
            ValidationError: If extension is not allowed
        """
        file_path = Path(filename)
        if file_path.suffix.lower() not in FileValidator.ALLOWED_EXTENSIONS:
            raise ValidationError(
                "Invalid file type. Only PDF files are allowed.",
                "INVALID_FILE_TYPE",
            )

    @staticmethod
    def validate_content_type(content_type: Optional[str]) -> None:
        """
        Validate that the content type is allowed.
        
        Args:
            content_type: The MIME content type to check
            
        Raises:
            ValidationError: If content type is provided but not allowed
        """
        if content_type and content_type not in FileValidator.ALLOWED_CONTENT_TYPES:
            expected = ", ".join(FileValidator.ALLOWED_CONTENT_TYPES)
            raise ValidationError(
                f"Invalid content type: {content_type}. Expected: {expected}",
                "INVALID_CONTENT_TYPE",
            )

    @staticmethod
    def validate_file_size(file_size: int) -> None:
        """
        Validate that the file size is within acceptable limits.
        
        Args:
            file_size: Size of the file in bytes
            
        Raises:
            ValidationError: If file is empty or exceeds max size
        """
        if file_size == 0:
            raise ValidationError(
                "File is empty",
                "EMPTY_FILE",
            )

        if file_size > FileValidator.MAX_FILE_SIZE:
            raise ValidationError(
                f"File size ({file_size} bytes) exceeds maximum allowed size of {FileValidator.MAX_FILE_SIZE} bytes (10MB).",
                "FILE_TOO_LARGE",
            )

    @staticmethod
    def validate_pdf_upload(
        filename: Optional[str],
        content_type: Optional[str],
        file_size: int,
    ) -> None:
        """
        Perform all validations for a PDF upload.
        
        This is a convenience method that runs all validation checks in order.
        
        Args:
            filename: The name of the uploaded file
            content_type: The MIME content type of the file
            file_size: Size of the file in bytes
            
        Raises:
            ValidationError: If any validation fails
        """
        FileValidator.validate_file_provided(filename)
        FileValidator.validate_extension(filename)
        FileValidator.validate_content_type(content_type)
        FileValidator.validate_file_size(file_size)

    @staticmethod
    async def validate_and_read_fastapi_upload(file: UploadFile) -> Tuple[bytes, int, str]:
        """
        Read and validate a FastAPI UploadFile.
        
        This method is specifically for FastAPI UploadFile objects.
        It reads the file content and validates it according to PDF upload rules.
        The caller is responsible for converting ValidationError to HTTPException.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Tuple of (file_content, file_size, filename)
            
        Raises:
            ValidationError: If validation fails
        """
        if not file:
            raise ValidationError("No file provided", "MISSING_FILE")
        
        # Read file content
        try:
            content = await file.read()
            file_size = len(content)
        except Exception as e:
            raise ValidationError(f"Failed to read file: {str(e)}", "FILE_READ_ERROR")
        
        # Validate the uploaded file
        FileValidator.validate_pdf_upload(
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size,
        )
        
        return content, file_size, file.filename

