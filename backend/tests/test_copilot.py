"""Tests for AUREA Copilot orchestration."""

from app.ai.copilot import CopilotService
from app.ai.llm import LLMDecision, ToolCall
from app.ai.tool_registry import FinancialToolRegistry
from app.ai.tools.financial import FinancialTools
import pytest
from app.ai.tool_registry import UnsupportedToolError

class FakeLLMClient:
    """Deterministic fake language model used by Copilot tests."""

    def __init__(self, decision: LLMDecision) -> None:
        self.decision = decision

    def decide(self, user_message: str) -> LLMDecision:
        return self.decision


def test_copilot_executes_requested_financial_tool(
    financial_tools: FinancialTools,
) -> None:
    """Copilot should route an approved tool call through the registry."""
    fake_llm = FakeLLMClient(
        LLMDecision(
            tool_call=ToolCall(
                tool_name="get_financial_summary",
                arguments={},
            )
        )
    )

    registry = FinancialToolRegistry(financial_tools)

    copilot = CopilotService(
        llm_client=fake_llm,
        tool_registry=registry,
    )

    result = copilot.handle_message(
        "How much did I spend?"
    )

    assert result.tool_name == "get_financial_summary"
    assert result.data["total_expenses"] == "2750.00"

def test_copilot_can_return_non_tool_response(
    financial_tools: FinancialTools,
) -> None:
    """Copilot may answer without tools when no financial calculation is needed."""
    fake_llm = FakeLLMClient(
        LLMDecision(
            response_text="I can help analyze your financial transactions."
        )
    )

    registry = FinancialToolRegistry(financial_tools)

    copilot = CopilotService(
        llm_client=fake_llm,
        tool_registry=registry,
    )

    result = copilot.handle_message("What can you do?")

    assert result == "I can help analyze your financial transactions."

def test_copilot_cannot_execute_unregistered_tool(
    financial_tools: FinancialTools,
) -> None:
    """LLM decisions must remain constrained by the tool registry."""
    fake_llm = FakeLLMClient(
        LLMDecision(
            tool_call=ToolCall(
                tool_name="execute_sql",
                arguments={"query": "DELETE FROM transactions"},
            )
        )
    )

    registry = FinancialToolRegistry(financial_tools)

    copilot = CopilotService(
        llm_client=fake_llm,
        tool_registry=registry,
    )

    with pytest.raises(UnsupportedToolError):
        copilot.handle_message("Delete my transactions")