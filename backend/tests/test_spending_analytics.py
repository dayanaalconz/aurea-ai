"""Tests for deterministic spending analytics."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.analytics.filters import filter_transactions_by_period
from app.analytics.spending import calculate_spending_by_category
from app.schemas.transaction import Transaction
from app.services.transaction_loader import load_transactions_from_csv

from app.analytics.spending import (
    calculate_category_spending_change,
    calculate_spending_by_category,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_january_spending_by_category_matches_ground_truth() -> None:
    """January category spending should match the verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    january = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    spending = calculate_spending_by_category(january)

    assert spending == {
        "housing": Decimal("1000.00"),
        "groceries": Decimal("200.00"),
        "restaurants": Decimal("100.00"),
    }


def test_february_spending_by_category_matches_ground_truth() -> None:
    """February category spending should match the verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    february = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
    )

    spending = calculate_spending_by_category(february)

    assert spending == {
        "housing": Decimal("1000.00"),
        "groceries": Decimal("250.00"),
        "restaurants": Decimal("200.00"),
    }


def test_transfers_and_income_are_excluded_from_spending() -> None:
    """Only expense transactions should contribute to spending."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    spending = calculate_spending_by_category(transactions)

    assert "transfer" not in spending
    assert "salary" not in spending


def test_missing_category_is_reported_as_uncategorized() -> None:
    """Expenses without a category should remain visible in analytics."""
    transaction = Transaction(
        transaction_id="txn_uncategorized",
        account_id="checking_001",
        transaction_date="2026-03-01",
        description="Unknown purchase",
        amount="-25.00",
        currency="EUR",
        transaction_type="expense",
        category=None,
        merchant=None,
    )

    spending = calculate_spending_by_category([transaction])

    assert spending == {
        "uncategorized": Decimal("25.00"),
    }

def test_category_spending_change_matches_ground_truth() -> None:
    """Category changes should explain the verified monthly spending increase."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    january = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    february = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
    )

    january_spending = calculate_spending_by_category(january)
    february_spending = calculate_spending_by_category(february)

    changes = calculate_category_spending_change(
        previous_spending=january_spending,
        current_spending=february_spending,
    )

    assert changes == {
        "housing": Decimal("0.00"),
        "groceries": Decimal("50.00"),
        "restaurants": Decimal("100.00"),
    }

    assert sum(changes.values(), Decimal("0.00")) == Decimal("150.00")

def test_category_change_handles_categories_missing_from_one_period() -> None:
    """Categories appearing in only one period must still be represented."""
    previous = {
        "groceries": Decimal("100.00"),
        "travel": Decimal("400.00"),
    }

    current = {
        "groceries": Decimal("150.00"),
        "restaurants": Decimal("80.00"),
    }

    changes = calculate_category_spending_change(
        previous_spending=previous,
        current_spending=current,
    )

    assert changes == {
        "groceries": Decimal("50.00"),
        "travel": Decimal("-400.00"),
        "restaurants": Decimal("80.00"),
    }