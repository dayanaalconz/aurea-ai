"""Reusable transaction filters for financial analytics."""

from datetime import date
from typing import Iterable

from app.schemas.transaction import Transaction


def filter_transactions_by_period(
    transactions: Iterable[Transaction],
    start_date: date,
    end_date: date,
) -> list[Transaction]:
    """Return transactions whose dates fall within the inclusive period."""
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    return [
        transaction
        for transaction in transactions
        if start_date <= transaction.transaction_date <= end_date
    ]
