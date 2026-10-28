"""Provider-independent contracts for AUREA language models."""

from typing import Protocol

from pydantic import BaseModel


class ToolCall(BaseModel):
    """A tool invocation requested by a language model."""

    tool_name: str
    arguments: dict[str, object]


class LLMDecision(BaseModel):
    """Structured decision returned by the language model."""

    response_text: str | None = None
    tool_call: ToolCall | None = None


class LLMClient(Protocol):
    """Contract implemented by AUREA language-model providers."""

    def decide(
        self,
        user_message: str,
    ) -> LLMDecision:
        """Interpret a user message and optionally request a tool."""
        ...