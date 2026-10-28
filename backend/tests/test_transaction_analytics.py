"""Tests for deterministic transaction-level analytics."""

from decimal import Decimal
from pathlib import Path

import pytest

from app.analytics.transaction import get_largest_expenses
from app.services.transaction_loader import load_transactions_from_csv


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_largest_expenses_are_ranked_correctly() -> None:
    """Largest individual expenses should appear first."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    expenses = get_largest_expenses(transactions, limit=3)

    assert len(expenses) == 3

    assert expenses[0].amount == Decimal("-1000.00")
    assert expenses[1].amount == Decimal("-1000.00")
    assert expenses[2].amount == Decimal("-250.00")


def test_largest_expenses_exclude_income_and_transfers() -> None:
    """Only expense transactions may appear in the ranking."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    expenses = get_largest_expenses(transactions, limit=20)

    assert all(
        transaction.transaction_type.value == "expense"
        for transaction in expenses
    )


def test_largest_expenses_limit_is_respected() -> None:
    """The requested result limit should be respected."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    expenses = get_largest_expenses(transactions, limit=2)

    assert len(expenses) == 2


def test_invalid_largest_expenses_limit_is_rejected() -> None:
    """Ranking limit must be greater than zero."""
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        get_largest_expenses([], limit=0)

def test_largest_expenses_have_deterministic_tie_breaking() -> None:
    """Equal expenses should be ordered deterministically."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    expenses = get_largest_expenses(transactions, limit=2)

    assert expenses[0].transaction_id == "txn_002"
    assert expenses[1].transaction_id == "txn_008"
