"""CSV transaction loading and validation services."""

import csv
from pathlib import Path

from app.schemas.transaction import Transaction


def load_transactions_from_csv(file_path: Path) -> list[Transaction]:
    """Load and validate canonical transactions from a CSV file."""
    transactions: list[Transaction] = []

    with file_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            transactions.append(Transaction(**row))

    return transactions