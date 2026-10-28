"""Read-only financial tools exposed to the AUREA AI layer."""

from app.ai.schemas import (
    ExpenseToolItem,
    FinancialSummaryToolResult,
    LargestExpensesToolInput,
    LargestExpensesToolResult,
    MerchantToolItem,
    TopMerchantsToolInput,
    TopMerchantsToolResult,
)
from app.services.financial_analytics import FinancialAnalyticsService


class FinancialTools:
    """Expose controlled read-only financial capabilities to the AI layer."""

    def __init__(
        self,
        analytics_service: FinancialAnalyticsService,
    ) -> None:
        self.analytics_service = analytics_service

    def get_financial_summary(self) -> FinancialSummaryToolResult:
        """Return deterministic financial summary evidence."""
        summary = self.analytics_service.get_summary()

        return FinancialSummaryToolResult(
            currency="EUR",
            total_income=summary.total_income,
            total_expenses=summary.total_expenses,
            net_cash_flow=summary.net_cash_flow,
        )

    def get_top_merchants(
        self,
        tool_input: TopMerchantsToolInput,
    ) -> TopMerchantsToolResult:
        """Return deterministic merchant spending evidence."""
        merchants = self.analytics_service.get_top_merchants(
            limit=tool_input.limit
        )

        return TopMerchantsToolResult(
            currency="EUR",
            merchants=[
                MerchantToolItem(
                    merchant=merchant.merchant,
                    amount=merchant.amount,
                    transaction_count=merchant.transaction_count,
                )
                for merchant in merchants
            ],
        )

    def get_largest_expenses(
        self,
        tool_input: LargestExpensesToolInput,
    ) -> LargestExpensesToolResult:
        """Return deterministic largest-expense evidence."""
        expenses = self.analytics_service.get_largest_expenses(
            limit=tool_input.limit
        )

        return LargestExpensesToolResult(
            currency="EUR",
            expenses=[
                ExpenseToolItem(
                    transaction_id=expense.transaction_id,
                    description=expense.description,
                    amount=abs(expense.amount),
                    category=expense.category,
                    merchant=expense.merchant,
                )
                for expense in expenses
            ],
        )