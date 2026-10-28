"""Deterministic monthly financial trend analytics."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from app.schemas.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class MonthlyTrend:
    """Financial metrics for one calendar month."""

    month: str
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal
    transaction_count: int


def calculate_monthly_trends(
    transactions: Iterable[Transaction],
) -> list[MonthlyTrend]:
    """Aggregate financial metrics by calendar month."""
    monthly_income: dict[str, Decimal] = defaultdict(
        lambda: Decimal("0.00")
    )
    monthly_expenses: dict[str, Decimal] = defaultdict(
        lambda: Decimal("0.00")
    )
    monthly_counts: dict[str, int] = defaultdict(int)

    for transaction in transactions:
        month = transaction.transaction_date.strftime("%Y-%m")

        if transaction.transaction_type == TransactionType.INCOME:
            monthly_income[month] += transaction.amount
            monthly_counts[month] += 1

        elif transaction.transaction_type == TransactionType.EXPENSE:
            monthly_expenses[month] += abs(transaction.amount)
            monthly_counts[month] += 1

    months = sorted(
        monthly_income.keys() | monthly_expenses.keys()
    )

    return [
        MonthlyTrend(
            month=month,
            total_income=monthly_income[month],
            total_expenses=monthly_expenses[month],
            net_cash_flow=(
                monthly_income[month]
                - monthly_expenses[month]
            ),
            transaction_count=monthly_counts[month],
        )
        for month in months
    ]