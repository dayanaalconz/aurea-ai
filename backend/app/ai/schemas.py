"""Structured schemas for AUREA AI financial tools."""

from decimal import Decimal

from pydantic import BaseModel, Field


class FinancialSummaryToolResult(BaseModel):
    """Structured result returned by the financial summary tool."""

    currency: str
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal


class TopMerchantsToolInput(BaseModel):
    """Validated input for the top merchants tool."""

    limit: int = Field(default=5, ge=1, le=100)


class MerchantToolItem(BaseModel):
    """Merchant spending evidence returned to the AI layer."""

    merchant: str
    amount: Decimal
    transaction_count: int


class TopMerchantsToolResult(BaseModel):
    """Structured result returned by the top merchants tool."""

    currency: str
    merchants: list[MerchantToolItem]


class LargestExpensesToolInput(BaseModel):
    """Validated input for the largest expenses tool."""

    limit: int = Field(default=5, ge=1, le=100)


class ExpenseToolItem(BaseModel):
    """Expense evidence returned to the AI layer."""

    transaction_id: str
    description: str
    amount: Decimal
    category: str | None
    merchant: str | None


class LargestExpensesToolResult(BaseModel):
    """Structured result returned by the largest expenses tool."""

    currency: str
    expenses: list[ExpenseToolItem]