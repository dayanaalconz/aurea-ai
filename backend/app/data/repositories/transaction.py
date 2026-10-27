"""Repository for transaction persistence."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import TransactionModel
from app.schemas.transaction import Transaction


class TransactionRepository:
    """Provide persistence operations for financial transactions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _to_model(transaction: Transaction) -> TransactionModel:
        """Map a validated transaction to its persistence model."""
        return TransactionModel(
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            transaction_date=transaction.transaction_date,
            description=transaction.description,
            amount=transaction.amount,
            currency=transaction.currency,
            transaction_type=transaction.transaction_type.value,
            category=transaction.category,
            merchant=transaction.merchant,
        )

    def add(self, transaction: Transaction) -> TransactionModel:
        """Persist one validated transaction."""
        model = self._to_model(transaction)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return model

    def add_many(
        self,
        transactions: Sequence[Transaction],
    ) -> list[TransactionModel]:
        """Persist validated transactions as one database transaction."""
        models = [self._to_model(transaction) for transaction in transactions]

        try:
            self.session.add_all(models)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return models

    def list_all(self) -> list[TransactionModel]:
        """Return all persisted transactions in deterministic order."""
        statement = select(TransactionModel).order_by(
            TransactionModel.transaction_date,
            TransactionModel.transaction_id,
        )

        return list(self.session.scalars(statement).all())