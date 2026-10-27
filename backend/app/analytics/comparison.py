"""Deterministic financial period comparison analytics."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from app.analytics.spending import (
    calculate_category_spending_change,
    calculate_spending_by_category,
)
from app.analytics.summary import calculate_financial_summary
from app.schemas.transaction import Transaction


@dataclass(frozen=True)
class PeriodComparison:
    """Structured comparison of spending between two periods."""

    previous_expenses: Decimal
    current_expenses: Decimal
    absolute_change: Decimal
    percentage_change: Decimal | None
    category_changes: dict[str, Decimal]


def compare_periods(
    previous_transactions: Iterable[Transaction],
    current_transactions: Iterable[Transaction],
) -> PeriodComparison:
    """Compare expenses between two transaction periods."""
    previous_list = list(previous_transactions)
    current_list = list(current_transactions)

    previous_summary = calculate_financial_summary(previous_list)
    current_summary = calculate_financial_summary(current_list)

    absolute_change = (
        current_summary.total_expenses
        - previous_summary.total_expenses
    )

    if previous_summary.total_expenses == Decimal("0.00"):
        percentage_change = None
    else:
        percentage_change = (
            absolute_change
            / previous_summary.total_expenses
            * Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    previous_spending = calculate_spending_by_category(previous_list)
    current_spending = calculate_spending_by_category(current_list)

    category_changes = calculate_category_spending_change(
        previous_spending=previous_spending,
        current_spending=current_spending,
    )

    return PeriodComparison(
        previous_expenses=previous_summary.total_expenses,
        current_expenses=current_summary.total_expenses,
        absolute_change=absolute_change,
        percentage_change=percentage_change,
        category_changes=category_changes,
    )