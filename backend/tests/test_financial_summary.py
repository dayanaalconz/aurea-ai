"""Tests for deterministic financial summary calculations."""

from decimal import Decimal
from pathlib import Path

from app.analytics.summary import calculate_financial_summary
from app.services.transaction_loader import load_transactions_from_csv


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_financial_summary_matches_ground_truth() -> None:
    """Financial summary must match the manually verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    summary = calculate_financial_summary(transactions)

    assert summary.total_income == Decimal("6000.00")
    assert summary.total_expenses == Decimal("2750.00")
    assert summary.net_cash_flow == Decimal("3250.00")

def test_financial_summary_handles_empty_transactions() -> None:
    """An empty transaction collection should produce zero totals."""
    summary = calculate_financial_summary([])

    assert summary.total_income == Decimal("0.00")
    assert summary.total_expenses == Decimal("0.00")
    assert summary.net_cash_flow == Decimal("0.00")