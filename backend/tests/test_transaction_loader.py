"""Tests for the canonical transaction CSV loader."""

from pathlib import Path

from app.schemas.transaction import TransactionType
from app.services.transaction_loader import load_transactions_from_csv

import pytest
from pydantic import ValidationError

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_load_transactions_from_csv() -> None:
    """The ground-truth fixture should load into canonical transactions."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    assert len(transactions) == 12


def test_loaded_transactions_are_normalized() -> None:
    """CSV values should be converted into canonical domain values."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    first_transaction = transactions[0]

    assert first_transaction.transaction_id == "txn_001"
    assert first_transaction.currency == "EUR"
    assert first_transaction.transaction_type == TransactionType.INCOME

def test_invalid_transaction_in_csv_is_rejected(tmp_path: Path) -> None:
    """Invalid financial rows must not pass the ingestion boundary."""
    invalid_csv = tmp_path / "invalid_transactions.csv"

    invalid_csv.write_text(
        (
            "transaction_id,account_id,transaction_date,description,"
            "amount,currency,transaction_type,category,merchant\n"
            "txn_invalid,checking_001,2026-03-01,"
            "Invalid expense,50.00,EUR,expense,groceries,Test Merchant\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValidationError,
        match="expense transactions must have a negative amount",
    ):
        load_transactions_from_csv(invalid_csv)