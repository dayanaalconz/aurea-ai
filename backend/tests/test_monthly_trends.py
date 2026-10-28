"""Tests for deterministic monthly trend analytics."""

from decimal import Decimal
from pathlib import Path

from app.analytics.trends import calculate_monthly_trends
from app.services.transaction_loader import load_transactions_from_csv


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_monthly_trends_match_ground_truth() -> None:
    """Monthly financial trends should match the verified fixture."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    trends = calculate_monthly_trends(transactions)

    assert len(trends) == 2

    january = trends[0]

    assert january.month == "2026-01"
    assert january.total_income == Decimal("3000.00")
    assert january.total_expenses == Decimal("1300.00")
    assert january.net_cash_flow == Decimal("1700.00")
    assert january.transaction_count == 4

    february = trends[1]

    assert february.month == "2026-02"
    assert february.total_income == Decimal("3000.00")
    assert february.total_expenses == Decimal("1450.00")
    assert february.net_cash_flow == Decimal("1550.00")
    assert february.transaction_count == 4


def test_monthly_trends_are_chronologically_sorted() -> None:
    """Monthly trends must be returned in chronological order."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    trends = calculate_monthly_trends(reversed(transactions))

    assert [trend.month for trend in trends] == [
        "2026-01",
        "2026-02",
    ]


def test_monthly_trends_exclude_transfers() -> None:
    """Transfers must not affect monthly financial metrics or counts."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    trends = calculate_monthly_trends(transactions)

    assert sum(
        trend.transaction_count
        for trend in trends
    ) == 8


def test_monthly_trends_handle_empty_input() -> None:
    """Empty datasets should return no monthly trend records."""
    assert calculate_monthly_trends([]) == []