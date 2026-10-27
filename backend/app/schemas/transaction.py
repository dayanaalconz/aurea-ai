"""Canonical transaction schemas for AUREA AI."""

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TransactionType(str, Enum):
    """Supported canonical transaction types."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(BaseModel):
    """Canonical representation of a financial transaction."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    transaction_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    transaction_date: date
    description: str = Field(min_length=1)
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    transaction_type: TransactionType
    category: str | None = None
    merchant: str | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        """Normalize currency codes to uppercase."""
        return value.upper()

    @model_validator(mode="after")
    def validate_financial_semantics(self) -> "Transaction":
        """Validate relationships between amount and transaction type."""
        if self.amount == Decimal("0"):
            raise ValueError("amount must not be zero")

        if self.transaction_type == TransactionType.INCOME and self.amount < 0:
            raise ValueError("income transactions must have a positive amount")

        if self.transaction_type == TransactionType.EXPENSE and self.amount > 0:
            raise ValueError("expense transactions must have a negative amount")

        return self