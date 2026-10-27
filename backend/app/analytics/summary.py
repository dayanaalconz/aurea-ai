"""Deterministic financial summary calculations."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from app.schemas.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class FinancialSummary:
    """Aggregated financial metrics for a collection of transactions."""

    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal


def calculate_financial_summary(
    transactions: Iterable[Transaction],
) -> FinancialSummary:
    """Calculate financial summary metrics excluding transfers."""
    transaction_list = list(transactions)

    total_income = sum(
        (
            transaction.amount
            for transaction in transaction_list
            if transaction.transaction_type == TransactionType.INCOME
        ),
        start=Decimal("0.00"),
    )

    expense_balance = sum(
        (
            transaction.amount
            for transaction in transaction_list
            if transaction.transaction_type == TransactionType.EXPENSE
        ),
        start=Decimal("0.00"),
    )

    total_expenses = abs(expense_balance)
    net_cash_flow = total_income - total_expenses

    return FinancialSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_cash_flow=net_cash_flow,
    )