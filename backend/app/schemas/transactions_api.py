"""API schemas for transaction ingestion."""

from pydantic import BaseModel


class TransactionUploadResponse(BaseModel):
    """Response returned after a successful transaction import."""

    status: str
    imported_transactions: int