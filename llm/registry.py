"""LLM Provider Registry module."""

import logging
from typing import Any
from llm.base import BaseLLMProvider
from llm.ollama import OllamaLLMProvider
from llm.openai_compat import OpenAICompatibleLLMProvider

logger = logging.getLogger(__name__)


class LLMRegistry:
    """Registry managing available LLM providers."""

    def __init__(self):
        self._providers: dict[str, BaseLLMProvider] = {
            "ollama": OllamaLLMProvider(),
            "openai_compat": OpenAICompatibleLLMProvider(),
        }

    def register(self, provider: BaseLLMProvider) -> None:
        self._providers[provider.provider_id] = provider
        logger.info("Registered LLM Provider: %s", provider.provider_id)

    def get_provider(self, provider_id: str | None = None) -> BaseLLMProvider:
        pid = provider_id or "ollama"
        if pid not in self._providers:
            raise KeyError(f"LLM Provider '{pid}' not found. Available: {list(self._providers.keys())}")
        return self._providers[pid]

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {
                "id": p.provider_id,
                "display_name": p.display_name,
                "configured": p.is_configured(),
            }
            for p in self._providers.values()
        ]


# Global LLM Registry
llm_registry = LLMRegistry()
