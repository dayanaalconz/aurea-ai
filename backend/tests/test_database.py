"""Tests for AUREA database infrastructure."""

from sqlalchemy import create_engine, inspect

from app.data.database import Base
from app.models.transaction import TransactionModel


def test_transactions_table_can_be_created() -> None:
    """The transaction model should create its expected database table."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert "transactions" in inspector.get_table_names()

    column_names = {
        column["name"]
        for column in inspector.get_columns("transactions")
    }

    assert column_names == {
        "transaction_id",
        "account_id",
        "transaction_date",
        "description",
        "amount",
        "currency",
        "transaction_type",
        "category",
        "merchant",
    }