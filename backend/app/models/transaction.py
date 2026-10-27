"""SQLAlchemy persistence model for financial transactions."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.data.database import Base


class TransactionModel(Base):
    """Database representation of a canonical financial transaction."""

    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    account_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    transaction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
    )

    merchant: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
    )