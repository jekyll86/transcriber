"""Modular LLM Subsystem."""

from llm.base import BaseLLMProvider
from llm.prompts import get_polish_prompt, get_summary_prompt
from llm.ollama import OllamaLLMProvider
from llm.openai_compat import OpenAICompatibleLLMProvider
from llm.registry import LLMRegistry, llm_registry
from llm.summarizer import ChunkedSummarizer

__all__ = [
    "BaseLLMProvider",
    "get_polish_prompt",
    "get_summary_prompt",
    "OllamaLLMProvider",
    "OpenAICompatibleLLMProvider",
    "LLMRegistry",
    "llm_registry",
    "ChunkedSummarizer",
]
