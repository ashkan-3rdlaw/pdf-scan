"""Main entry point for running the PDF scan service."""

import uvicorn


def main() -> None:
    """Run the FastAPI server."""
    uvicorn.run(
        "pdf_scan.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()

