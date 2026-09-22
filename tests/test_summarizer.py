"""Tests for chunked text splitting and Map-Reduce summarization."""

import pytest
from llm.summarizer import split_into_chunks, ChunkedSummarizer
from llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    provider_id = "mock"
    display_name = "Mock Provider"

    def is_configured(self):
        return True

    async def list_models(self):
        return ["mock-model"]

    async def generate_stream(self, prompt, system_prompt=None, model=None, **kwargs):
        yield "Summary: " + prompt[:30]

    async def test_connection(self):
        return {"online": True}


def test_split_into_chunks():
    # Construct paragraph of 100 words
    sentences = [f"This is sentence number {i} with several words." for i in range(50)]
    long_text = " ".join(sentences)

    chunks = split_into_chunks(long_text, target_words=50)
    assert len(chunks) > 1
    # Check that sentences aren't cut mid-sentence
    for chunk in chunks:
        assert chunk.endswith(".")


@pytest.mark.asyncio
async def test_chunked_summarizer_short_text():
    mock_prov = MockLLMProvider()
    summarizer = ChunkedSummarizer(mock_prov)

    tokens = []
    async for token in summarizer.summarize_stream("A short meeting transcript about budget.", level="bullets"):
        tokens.append(token)

    assert len(tokens) > 0
    assert "Summary:" in "".join(tokens)


@pytest.mark.asyncio
async def test_chunked_summarizer_long_text():
    mock_prov = MockLLMProvider()
    summarizer = ChunkedSummarizer(mock_prov)

    # Long text exceeding 2500 words to trigger Map-Reduce
    long_text = ("This is a long sentence discussing project architecture in detail. " * 350)

    tokens = []
    async for token in summarizer.summarize_stream(long_text, level="bullets"):
        tokens.append(token)

    output = "".join(tokens)
    assert "Processing long transcript" in output
    assert "Summary:" in output
