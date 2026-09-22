"""OpenAI-compatible LLM Provider implementation.

Supports OpenAI, Groq, DeepSeek, Mistral AI, OpenRouter, vLLM, and any
endpoint following the standard /v1/chat/completions schema.
"""

import json
import logging
from typing import AsyncGenerator, Any
import httpx

from config import settings
from llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    """Provider for standard OpenAI-compatible REST APIs."""

    provider_id: str = "openai_compat"
    display_name: str = "OpenAI-Compatible (Cloud / Proxy)"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None
    ):
        self.api_key = api_key or settings.openai_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.default_model = default_model or settings.openai_default_model

    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    async def list_models(self) -> list[str]:
        if not self.is_configured():
            return []
        url = f"{self.base_url}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return [m.get("id") for m in data.get("data", []) if m.get("id")]
                return [self.default_model]
        except Exception:
            return [self.default_model]

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        if not self.is_configured():
            raise RuntimeError("OpenAI-compatible provider requires an API Key.")

        url = f"{self.base_url}/chat/completions"
        model_name = model or self.default_model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "temperature": 0.3,
        }

        timeout = httpx.Timeout(120.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    raise RuntimeError(f"API error (HTTP {response.status_code}): {err_body.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue

    async def test_connection(self) -> dict[str, Any]:
        if not self.is_configured():
            return {
                "online": False,
                "base_url": self.base_url,
                "error": "API Key is missing",
            }

        url = f"{self.base_url}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, headers=headers)
                return {
                    "online": resp.status_code == 200,
                    "base_url": self.base_url,
                    "status_code": resp.status_code,
                }
        except Exception as e:
            return {
                "online": False,
                "base_url": self.base_url,
                "error": str(e),
            }
