"""Tests for reusable financial analytics filters."""

from datetime import date
from pathlib import Path

import pytest

from app.analytics.filters import filter_transactions_by_period
from app.analytics.summary import calculate_financial_summary
from app.services.transaction_loader import load_transactions_from_csv
from decimal import Decimal


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_january_financial_summary_matches_ground_truth() -> None:
    """January metrics should match the manually verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    january_transactions = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    summary = calculate_financial_summary(january_transactions)

    assert summary.total_income == Decimal("3000.00")
    assert summary.total_expenses == Decimal("1300.00")
    assert summary.net_cash_flow == Decimal("1700.00")


def test_february_financial_summary_matches_ground_truth() -> None:
    """February metrics should match the manually verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    february_transactions = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
    )

    summary = calculate_financial_summary(february_transactions)

    assert summary.total_income == Decimal("3000.00")
    assert summary.total_expenses == Decimal("1450.00")
    assert summary.net_cash_flow == Decimal("1550.00")


def test_period_boundaries_are_inclusive() -> None:
    """Transactions occurring on period boundaries must be included."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    selected = filter_transactions_by_period(
        transactions,
        start_date=date(2026, 1, 5),
        end_date=date(2026, 1, 5),
    )

    assert len(selected) == 1
    assert selected[0].transaction_id == "txn_001"


def test_invalid_period_is_rejected() -> None:
    """An inverted date interval must be rejected."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with pytest.raises(
        ValueError,
        match="start_date must be before or equal to end_date",
    ):
        filter_transactions_by_period(
            transactions,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
        )