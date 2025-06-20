"""
This module contains the implementation of
the LLM Provider class (e.g., OpenAI).
"""

from typing import Any

from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack_integrations.components.generators.google_ai import (
    GoogleAIGeminiChatGenerator,
)
from haystack_integrations.components.generators.ollama import OllamaChatGenerator

LLM = (
    OpenAIChatGenerator
    | AnthropicChatGenerator
    | OllamaChatGenerator
    | GoogleAIGeminiChatGenerator
)


class LLMProvider:
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.validate_provider()

    def validate_provider(self) -> None:
        if self.provider not in ["openai", "anthropic", "ollama", "gemini"]:
            raise ValueError(
                "provider should be either 'openai', 'anthropic', 'ollama', or 'gemini'"
            )

    def connect(self, **kwargs: dict[str, Any]) -> LLM:
        if self.provider == "openai":
            return OpenAIChatGenerator(**kwargs)
        elif self.provider == "anthropic":
            return AnthropicChatGenerator(**kwargs)
        elif self.provider == "gemini":
            return GoogleAIGeminiChatGenerator(**kwargs)
        else:
            return OllamaChatGenerator(**kwargs)
