"""Deterministic spending analytics."""

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from app.schemas.transaction import Transaction, TransactionType


def calculate_spending_by_category(
    transactions: Iterable[Transaction],
) -> dict[str, Decimal]:
    """Calculate positive expense totals grouped by category."""
    spending: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

    for transaction in transactions:
        if transaction.transaction_type != TransactionType.EXPENSE:
            continue

        category = transaction.category or "uncategorized"
        spending[category] += abs(transaction.amount)

    return dict(spending)

def calculate_category_spending_change(
    previous_spending: dict[str, Decimal],
    current_spending: dict[str, Decimal],
) -> dict[str, Decimal]:
    """Calculate spending changes by category between two periods."""
    categories = previous_spending.keys() | current_spending.keys()

    return {
        category: (
            current_spending.get(category, Decimal("0.00"))
            - previous_spending.get(category, Decimal("0.00"))
        )
        for category in categories
    }