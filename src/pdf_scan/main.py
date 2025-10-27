"""Main entry point for running the PDF scan service."""

import os
import uvicorn


def main() -> None:
    """Run the FastAPI server."""
    # Get port from environment variable (for Render.com) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "pdf_scan.app:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("APP_RELOAD", "true").lower() == "true",
    )


if __name__ == "__main__":
    main()

