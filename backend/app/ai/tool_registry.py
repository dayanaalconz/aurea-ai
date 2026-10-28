"""Controlled registry and dispatcher for AUREA AI tools."""

from typing import Any

from pydantic import BaseModel

from app.ai.schemas import (
    LargestExpensesToolInput,
    TopMerchantsToolInput,
)
from app.ai.tools.financial import FinancialTools


class UnsupportedToolError(ValueError):
    """Raised when the AI requests an unsupported tool."""


class ToolExecutionResult(BaseModel):
    """Normalized result returned by the controlled tool dispatcher."""

    tool_name: str
    data: dict[str, Any]


class FinancialToolRegistry:
    """Whitelist and dispatch read-only financial tools."""

    def __init__(self, financial_tools: FinancialTools) -> None:
        self.financial_tools = financial_tools

    @property
    def allowed_tools(self) -> tuple[str, ...]:
        """Return the names of tools available to the AI layer."""
        return (
            "get_financial_summary",
            "get_top_merchants",
            "get_largest_expenses",
        )

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolExecutionResult:
        """Validate and execute an explicitly allowed financial tool."""
        arguments = arguments or {}

        if tool_name == "get_financial_summary":
            if arguments:
                raise ValueError(
                    "get_financial_summary does not accept arguments"
                )

            result = self.financial_tools.get_financial_summary()

        elif tool_name == "get_top_merchants":
            tool_input = TopMerchantsToolInput.model_validate(arguments)
            result = self.financial_tools.get_top_merchants(tool_input)

        elif tool_name == "get_largest_expenses":
            tool_input = LargestExpensesToolInput.model_validate(arguments)
            result = self.financial_tools.get_largest_expenses(tool_input)

        else:
            raise UnsupportedToolError(
                f"Unsupported tool: {tool_name}"
            )

        return ToolExecutionResult(
            tool_name=tool_name,
            data=result.model_dump(mode="json"),
        )