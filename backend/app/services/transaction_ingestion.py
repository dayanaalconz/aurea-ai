"""Application service for transaction ingestion."""

from pathlib import Path

from app.data.repositories.transaction import TransactionRepository
from app.services.transaction_loader import load_transactions_from_csv


class TransactionIngestionService:
    """Coordinate transaction validation and persistence."""

    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    def ingest_csv(self, file_path: Path) -> int:
        """Validate and persist all transactions from a CSV file."""
        transactions = load_transactions_from_csv(file_path)

        self.repository.add_many(transactions)

        return len(transactions)