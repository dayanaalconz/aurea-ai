"""Tests for the controlled AUREA AI tool registry."""

import pytest
from pydantic import ValidationError

from app.ai.tool_registry import (
    FinancialToolRegistry,
    UnsupportedToolError,
)
from app.ai.tools.financial import FinancialTools


@pytest.fixture
def tool_registry(
    financial_tools: FinancialTools,
) -> FinancialToolRegistry:
    """Provide a registry backed by deterministic financial tools."""
    return FinancialToolRegistry(financial_tools)


def test_registry_exposes_only_allowed_tools(
    tool_registry: FinancialToolRegistry,
) -> None:
    """The AI layer should see only explicitly approved tools."""
    assert tool_registry.allowed_tools == (
        "get_financial_summary",
        "get_top_merchants",
        "get_largest_expenses",
    )


def test_registry_executes_financial_summary(
    tool_registry: FinancialToolRegistry,
) -> None:
    """Registry should execute an allowed parameterless tool."""
    result = tool_registry.execute("get_financial_summary")

    assert result.tool_name == "get_financial_summary"
    assert result.data == {
        "currency": "EUR",
        "total_income": "6000.00",
        "total_expenses": "2750.00",
        "net_cash_flow": "3250.00",
    }


def test_registry_validates_tool_arguments(
    tool_registry: FinancialToolRegistry,
) -> None:
    """LLM-generated arguments must pass tool input validation."""
    result = tool_registry.execute(
        "get_top_merchants",
        {"limit": 2},
    )

    assert result.tool_name == "get_top_merchants"
    assert len(result.data["merchants"]) == 2


def test_registry_rejects_invalid_arguments(
    tool_registry: FinancialToolRegistry,
) -> None:
    """Invalid generated arguments should fail before tool execution."""
    with pytest.raises(ValidationError):
        tool_registry.execute(
            "get_top_merchants",
            {"limit": -100},
        )


def test_registry_rejects_unsupported_tools(
    tool_registry: FinancialToolRegistry,
) -> None:
    """The AI must not execute tools outside the explicit whitelist."""
    with pytest.raises(
        UnsupportedToolError,
        match="Unsupported tool",
    ):
        tool_registry.execute(
            "execute_sql",
            {"query": "SELECT * FROM transactions"},
        )


def test_summary_rejects_unexpected_arguments(
    tool_registry: FinancialToolRegistry,
) -> None:
    """Parameterless tools should reject generated extra arguments."""
    with pytest.raises(
        ValueError,
        match="does not accept arguments",
    ):
        tool_registry.execute(
            "get_financial_summary",
            {"currency": "USD"},
        )