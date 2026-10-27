"""Tests for the canonical AUREA transaction schema."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.transaction import Transaction, TransactionType


def test_valid_expense_transaction() -> None:
    """A valid expense should be normalized successfully."""
    transaction = Transaction(
        transaction_id="txn_001",
        account_id="checking_001",
        transaction_date="2026-01-15",
        description="Mercadona",
        amount="-54.37",
        currency="eur",
        transaction_type="expense",
        category="groceries",
        merchant="Mercadona",
    )

    assert transaction.transaction_date == date(2026, 1, 15)
    assert transaction.amount == Decimal("-54.37")
    assert transaction.currency == "EUR"
    assert transaction.transaction_type == TransactionType.EXPENSE


def test_positive_expense_is_rejected() -> None:
    """Expenses must represent cash outflows."""
    with pytest.raises(
        ValidationError,
        match="expense transactions must have a negative amount",
    ):
        Transaction(
            transaction_id="txn_002",
            account_id="checking_001",
            transaction_date="2026-01-15",
            description="Restaurant",
            amount="42.00",
            currency="EUR",
            transaction_type="expense",
        )


def test_negative_income_is_rejected() -> None:
    """Income must represent cash inflows."""
    with pytest.raises(
        ValidationError,
        match="income transactions must have a positive amount",
    ):
        Transaction(
            transaction_id="txn_003",
            account_id="checking_001",
            transaction_date="2026-01-31",
            description="Salary",
            amount="-2800.00",
            currency="EUR",
            transaction_type="income",
        )


def test_zero_amount_is_rejected() -> None:
    """Zero-value transactions are not part of the canonical model."""
    with pytest.raises(ValidationError, match="amount must not be zero"):
        Transaction(
            transaction_id="txn_004",
            account_id="checking_001",
            transaction_date="2026-01-31",
            description="Zero transaction",
            amount="0.00",
            currency="EUR",
            transaction_type="transfer",
        )

def test_transfer_accepts_positive_amount() -> None:
    """Transfers may represent cash entering an owned account."""
    transaction = Transaction(
        transaction_id="txn_005",
        account_id="savings_001",
        transaction_date="2026-02-01",
        description="Transfer from checking",
        amount="500.00",
        currency="EUR",
        transaction_type="transfer",
    )

    assert transaction.amount == Decimal("500.00")
    assert transaction.transaction_type == TransactionType.TRANSFER


def test_transfer_accepts_negative_amount() -> None:
    """Transfers may represent cash leaving an owned account."""
    transaction = Transaction(
        transaction_id="txn_006",
        account_id="checking_001",
        transaction_date="2026-02-01",
        description="Transfer to savings",
        amount="-500.00",
        currency="EUR",
        transaction_type="transfer",
    )

    assert transaction.amount == Decimal("-500.00")
    assert transaction.transaction_type == TransactionType.TRANSFER


def test_blank_description_is_rejected() -> None:
    """Descriptions containing only whitespace must be rejected."""
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="txn_007",
            account_id="checking_001",
            transaction_date="2026-02-01",
            description="   ",
            amount="-20.00",
            currency="EUR",
            transaction_type="expense",
        )


def test_unexpected_fields_are_rejected() -> None:
    """Unknown fields must not be silently accepted."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Transaction(
            transaction_id="txn_008",
            account_id="checking_001",
            transaction_date="2026-02-01",
            description="Groceries",
            amount="-20.00",
            currency="EUR",
            transaction_type="expense",
            ammount="-20.00",
        )