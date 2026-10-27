"""Tests for transaction persistence."""

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.data.database import Base
from app.data.repositories.transaction import TransactionRepository
from app.models.transaction import TransactionModel
from app.schemas.transaction import Transaction, TransactionType

from pathlib import Path

from app.services.transaction_loader import load_transactions_from_csv

import pytest
from sqlalchemy.exc import IntegrityError

def test_transaction_can_be_persisted_and_retrieved() -> None:
    """A validated transaction should survive a database round trip."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transaction = Transaction(
        transaction_id="txn_001",
        account_id="checking_001",
        transaction_date="2026-01-05",
        description="Monthly salary",
        amount="3000.00",
        currency="EUR",
        transaction_type="income",
        category="salary",
        merchant="Employer",
    )

    with Session(engine) as session:
        repository = TransactionRepository(session)

        repository.add(transaction)
        stored_transactions = repository.list_all()

    assert len(stored_transactions) == 1

    stored = stored_transactions[0]

    assert isinstance(stored, TransactionModel)
    assert stored.transaction_id == "txn_001"
    assert stored.amount == Decimal("3000.00")
    assert stored.currency == "EUR"
    assert stored.transaction_type == TransactionType.INCOME.value

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)

def test_transaction_batch_can_be_persisted() -> None:
    """The validated ground-truth fixture should persist as one batch."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)

        persisted = repository.add_many(transactions)
        stored = repository.list_all()

    assert len(persisted) == 12
    assert len(stored) == 12

    assert stored[0].transaction_id == "txn_001"
    assert stored[-1].transaction_id == "txn_012"

    assert sum(
        transaction.amount
        for transaction in stored
        if transaction.transaction_type == TransactionType.TRANSFER.value
    ) == Decimal("0.00")

def test_batch_is_rolled_back_when_transaction_id_is_duplicated() -> None:
    """A failed batch must not leave partially persisted transactions."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    first_transaction = Transaction(
        transaction_id="txn_duplicate",
        account_id="checking_001",
        transaction_date="2026-03-01",
        description="First transaction",
        amount="-25.00",
        currency="EUR",
        transaction_type="expense",
        category="groceries",
        merchant="Merchant A",
    )

    duplicate_transaction = Transaction(
        transaction_id="txn_duplicate",
        account_id="checking_001",
        transaction_date="2026-03-02",
        description="Duplicated transaction",
        amount="-40.00",
        currency="EUR",
        transaction_type="expense",
        category="restaurants",
        merchant="Merchant B",
    )

    with Session(engine) as session:
        repository = TransactionRepository(session)

        with pytest.raises(IntegrityError):
            repository.add_many(
                [first_transaction, duplicate_transaction]
            )

        stored_transactions = repository.list_all()

    assert stored_transactions == []