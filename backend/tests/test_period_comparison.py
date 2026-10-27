"""Tests for deterministic financial period comparisons."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.analytics.comparison import compare_periods
from app.analytics.filters import filter_transactions_by_period
from app.services.transaction_loader import load_transactions_from_csv


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_period_comparison_matches_ground_truth() -> None:
    """January-to-February comparison should match verified values."""
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

    comparison = compare_periods(january, february)

    assert comparison.previous_expenses == Decimal("1300.00")
    assert comparison.current_expenses == Decimal("1450.00")
    assert comparison.absolute_change == Decimal("150.00")
    assert comparison.percentage_change == Decimal("11.54")

    assert comparison.category_changes == {
        "housing": Decimal("0.00"),
        "groceries": Decimal("50.00"),
        "restaurants": Decimal("100.00"),
    }


def test_period_comparison_reconciles_category_changes() -> None:
    """Category contributions must reconcile with the total expense change."""
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

    comparison = compare_periods(january, february)

    category_change_total = sum(
        comparison.category_changes.values(),
        Decimal("0.00"),
    )

    assert category_change_total == comparison.absolute_change

def test_percentage_change_is_none_when_previous_expenses_are_zero() -> None:
    """Percentage change is undefined when the baseline is zero."""
    comparison = compare_periods([], [])

    assert comparison.previous_expenses == Decimal("0.00")
    assert comparison.current_expenses == Decimal("0.00")
    assert comparison.absolute_change == Decimal("0.00")
    assert comparison.percentage_change is None