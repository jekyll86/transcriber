"""Base LLM Provider interface using modern Python typing."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers (Strategy Pattern)."""

    provider_id: str = "base"
    display_name: str = "Base LLM Provider"

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if the provider is configured and reachable."""
        pass

    @abstractmethod
    async def list_models(self) -> list[str]:
        """Fetch list of available models for this provider."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream generated text tokens asynchronously."""
        pass

    @abstractmethod
    async def test_connection(self) -> dict[str, Any]:
        """Verify API connectivity and return status dictionary."""
        pass
