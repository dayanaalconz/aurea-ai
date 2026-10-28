"""Tests for controlled AUREA AI financial tools."""

from decimal import Decimal
from pathlib import Path
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.ai.schemas import (
    LargestExpensesToolInput,
    TopMerchantsToolInput,
)
from app.ai.tools.financial import FinancialTools
from app.data.database import Base
from app.data.repositories.transaction import TransactionRepository
from app.services.financial_analytics import FinancialAnalyticsService
from app.services.transaction_loader import load_transactions_from_csv

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def create_financial_tools(session: Session) -> FinancialTools:
    """Create financial AI tools backed by the provided database session."""
    repository = TransactionRepository(session)
    analytics_service = FinancialAnalyticsService(repository)

    return FinancialTools(analytics_service)


def test_financial_summary_tool_returns_verified_metrics() -> None:
    """The summary tool must return deterministic analytics evidence."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        tools = create_financial_tools(session)
        result = tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")


def test_top_merchants_tool_returns_verified_evidence() -> None:
    """The top-merchants tool must return deterministic ranked evidence."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        tools = create_financial_tools(session)

        result = tools.get_top_merchants(
            TopMerchantsToolInput(limit=2)
        )

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")


def test_largest_expenses_tool_returns_verified_evidence() -> None:
    """The largest-expenses tool must return ranked transaction evidence."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        tools = create_financial_tools(session)

        result = tools.get_largest_expenses(
            LargestExpensesToolInput(limit=2)
        )

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].amount == Decimal("1000.00")
    assert result.expenses[1].amount == Decimal("1000.00")


def test_tool_input_default_limit_is_safe() -> None:
    """Tool inputs should use a bounded default result count."""
    assert TopMerchantsToolInput().limit == 5
    assert LargestExpensesToolInput().limit == 5


@pytest.mark.parametrize("limit", [0, -1, 101])
def test_top_merchants_tool_input_rejects_invalid_limit(limit: int) -> None:
    """Invalid model-generated tool arguments must be rejected."""
    with pytest.raises(ValidationError):
        TopMerchantsToolInput(limit=limit)


@pytest.mark.parametrize("limit", [0, -1, 101])
def test_largest_expenses_tool_input_rejects_invalid_limit(limit: int) -> None:
    """Invalid model-generated tool arguments must be rejected."""
    with pytest.raises(ValidationError):
        LargestExpensesToolInput(limit=limit)

def test_financial_summary_tool_returns_grounded_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Summary tool should return deterministic financial evidence."""
    result = financial_tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_ranked_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Merchant tool should return deterministic ranked evidence."""
    tool_input = TopMerchantsToolInput(limit=2)

    result = financial_tools.get_top_merchants(tool_input)

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")
    assert result.merchants[0].transaction_count == 2

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")

def test_largest_expenses_tool_returns_transaction_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Largest-expense tool should return traceable transaction evidence."""
    tool_input = LargestExpensesToolInput(limit=2)

    result = financial_tools.get_largest_expenses(tool_input)

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].transaction_id == "txn_002"
    assert result.expenses[0].amount == Decimal("1000.00")

    assert result.expenses[1].transaction_id == "txn_008"
    assert result.expenses[1].amount == Decimal("1000.00")

def test_financial_summary_tool_returns_grounded_results(
    financial_tools: FinancialTools,
) -> None:
    """Financial summary tool should return deterministic financial evidence."""
    result = financial_tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_ranked_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Top merchants tool should return deterministic ranked evidence."""
    result = financial_tools.get_top_merchants(
        TopMerchantsToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")
    assert result.merchants[0].transaction_count == 2

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")

def test_largest_expenses_tool_returns_transaction_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Largest-expenses tool should expose source transaction evidence."""
    result = financial_tools.get_largest_expenses(
        LargestExpensesToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    first_expense = result.expenses[0]

    assert first_expense.transaction_id == "txn_002"
    assert first_expense.description == "Rent"
    assert first_expense.amount == Decimal("1000.00")
    assert first_expense.category == "housing"
    assert first_expense.merchant == "Landlord"

def test_financial_summary_tool_returns_grounded_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Summary tool values must originate from deterministic analytics."""
    result = financial_tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_grounded_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Merchant tool must expose deterministic ranked evidence."""
    result = financial_tools.get_top_merchants(
        TopMerchantsToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")
    assert result.merchants[0].transaction_count == 2

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")
    assert result.merchants[1].transaction_count == 2

def test_largest_expenses_tool_returns_transaction_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Largest-expense tool must return source transaction evidence."""
    result = financial_tools.get_largest_expenses(
        LargestExpensesToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].transaction_id == "txn_002"
    assert result.expenses[0].amount == Decimal("1000.00")

    assert result.expenses[1].transaction_id == "txn_008"
    assert result.expenses[1].amount == Decimal("1000.00")

def test_financial_summary_tool_returns_grounded_evidence(
    populated_session,
) -> None:
    """Financial summary tool must return deterministic financial evidence."""
    repository = TransactionRepository(populated_session)
    service = FinancialAnalyticsService(repository)
    tools = FinancialTools(service)

    result = tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_grounded_evidence(
    populated_session,
) -> None:
    """Top merchants tool must expose deterministic ranked evidence."""
    repository = TransactionRepository(populated_session)
    service = FinancialAnalyticsService(repository)
    tools = FinancialTools(service)

    result = tools.get_top_merchants(
        TopMerchantsToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")

def test_largest_expenses_tool_returns_grounded_evidence(
    populated_session,
) -> None:
    """Largest expenses tool must return persisted transaction evidence."""
    repository = TransactionRepository(populated_session)
    service = FinancialAnalyticsService(repository)
    tools = FinancialTools(service)

    result = tools.get_largest_expenses(
        LargestExpensesToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].transaction_id == "txn_002"
    assert result.expenses[0].amount == Decimal("1000.00")

    assert result.expenses[1].transaction_id == "txn_008"
    assert result.expenses[1].amount == Decimal("1000.00")

def test_financial_summary_tool_returns_grounded_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Summary tool must return deterministic financial evidence."""
    result = financial_tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_ranked_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Top-merchants tool should preserve deterministic ranking."""
    tool_input = TopMerchantsToolInput(limit=2)

    result = financial_tools.get_top_merchants(tool_input)

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")
    assert result.merchants[0].transaction_count == 2

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")
    assert result.merchants[1].transaction_count == 2

def test_largest_expenses_tool_returns_transaction_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Largest-expenses tool should expose grounded transaction evidence."""
    tool_input = LargestExpensesToolInput(limit=2)

    result = financial_tools.get_largest_expenses(tool_input)

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].transaction_id == "txn_002"
    assert result.expenses[0].amount == Decimal("1000.00")
    assert result.expenses[0].category == "housing"

    assert result.expenses[1].transaction_id == "txn_008"
    assert result.expenses[1].amount == Decimal("1000.00")
    assert result.expenses[1].category == "housing"

def test_financial_summary_tool_returns_grounded_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Summary tool values must originate from deterministic analytics."""
    result = financial_tools.get_financial_summary()

    assert result.currency == "EUR"
    assert result.total_income == Decimal("6000.00")
    assert result.total_expenses == Decimal("2750.00")
    assert result.net_cash_flow == Decimal("3250.00")

def test_top_merchants_tool_returns_ranked_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Merchant tool should expose deterministic ranked spending."""
    result = financial_tools.get_top_merchants(
        TopMerchantsToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.merchants) == 2

    assert result.merchants[0].merchant == "Landlord"
    assert result.merchants[0].amount == Decimal("2000.00")
    assert result.merchants[0].transaction_count == 2

    assert result.merchants[1].merchant == "Mercadona"
    assert result.merchants[1].amount == Decimal("450.00")

def test_largest_expenses_tool_returns_transaction_evidence(
    financial_tools: FinancialTools,
) -> None:
    """Largest-expense tool should expose traceable transaction evidence."""
    result = financial_tools.get_largest_expenses(
        LargestExpensesToolInput(limit=2)
    )

    assert result.currency == "EUR"
    assert len(result.expenses) == 2

    assert result.expenses[0].transaction_id == "txn_002"
    assert result.expenses[0].amount == Decimal("1000.00")
    assert result.expenses[0].category == "housing"

    assert result.expenses[1].transaction_id == "txn_008"
    assert result.expenses[1].amount == Decimal("1000.00")