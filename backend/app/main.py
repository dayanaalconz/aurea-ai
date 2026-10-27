"""AUREA AI backend application."""

from fastapi import FastAPI

app = FastAPI(
    title="AUREA AI API",
    description="Backend API for the AUREA financial intelligence platform.",
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Return the current health status of the API."""
    return {
        "status": "healthy",
        "service": "aurea-api",
    }