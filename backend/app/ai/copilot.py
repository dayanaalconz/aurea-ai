"""Application orchestration for the AUREA financial copilot."""

from app.ai.llm import LLMClient
from app.ai.tool_registry import FinancialToolRegistry, ToolExecutionResult


class CopilotService:
    """Coordinate language understanding with controlled financial tools."""

    def __init__(
        self,
        llm_client: LLMClient,
        tool_registry: FinancialToolRegistry,
    ) -> None:
        self.llm_client = llm_client
        self.tool_registry = tool_registry

    def handle_message(
        self,
        user_message: str,
    ) -> ToolExecutionResult | str:
        """Interpret a user message and execute approved tools when requested."""
        decision = self.llm_client.decide(user_message)

        if decision.tool_call is not None:
            return self.tool_registry.execute(
                tool_name=decision.tool_call.tool_name,
                arguments=decision.tool_call.arguments,
            )

        if decision.response_text is not None:
            return decision.response_text

        raise ValueError(
            "The language model returned neither a response nor a tool call"
        )