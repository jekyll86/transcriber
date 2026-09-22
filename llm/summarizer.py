"""Map-Reduce Chunked Summarizer for long transcripts.

Handles arbitrary audio lengths by splitting transcripts exceeding context window
limits into manageable chunks, summarizing each segment, and reducing to a final synthesis.
"""

from __future__ import annotations

import re
from typing import AsyncGenerator
from llm.base import BaseLLMProvider
from llm.prompts import get_summary_prompt

CHUNK_WORD_THRESHOLD = 2500
CHUNK_TARGET_SIZE = 1500


def split_into_chunks(text: str, target_words: int = CHUNK_TARGET_SIZE) -> list[str]:
    """Split text into chunks of target word length at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_word_count = 0

    for sentence in sentences:
        words = len(sentence.split())
        if current_word_count + words > target_words and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_word_count = words
        else:
            current_chunk.append(sentence)
            current_word_count += words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text]


class ChunkedSummarizer:
    """Orchestrates single-pass or map-reduce summarization based on transcript length."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def summarize_stream(
        self,
        transcript: str,
        level: str = "bullets",
        custom_instruction: str | None = None,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        words = len(transcript.split())

        # If transcript is short enough, perform direct single-pass generation
        if words <= CHUNK_WORD_THRESHOLD:
            sys_prompt, user_prompt = get_summary_prompt(
                transcript, level=level, custom_instruction=custom_instruction
            )
            async for token in self.provider.generate_stream(
                prompt=user_prompt, system_prompt=sys_prompt, model=model
            ):
                yield token
            return

        # Map-Reduce phase for long transcripts
        chunks = split_into_chunks(transcript, target_words=CHUNK_TARGET_SIZE)
        intermediate_summaries: list[str] = []

        yield f"*[Processing long transcript in {len(chunks)} sections...]*\n\n"

        for i, chunk in enumerate(chunks, start=1):
            map_sys = (
                "You are an expert analyst. Extract and summarize the key facts, decisions, and discussion "
                "topics from this transcript segment into concise, dense bullet points."
            )
            map_user = f"Transcript Section {i} of {len(chunks)}:\n\n{chunk}"

            chunk_summary_parts: list[str] = []
            async for token in self.provider.generate_stream(
                prompt=map_user, system_prompt=map_sys, model=model
            ):
                chunk_summary_parts.append(token)

            intermediate_summaries.append(f"### Section {i} Highlights:\n" + "".join(chunk_summary_parts))

        # Reduce phase: synthesize all intermediate summaries into requested level
        combined_notes = "\n\n".join(intermediate_summaries)
        reduce_sys, reduce_user = get_summary_prompt(
            combined_notes, level=level, custom_instruction=custom_instruction
        )
        reduce_prompt = (
            f"Below are the synthesized notes from all sections of a long meeting/recording:\n\n"
            f"{combined_notes}\n\n"
            f"Please produce the final {level} summary synthesizing all sections."
        )

        async for token in self.provider.generate_stream(
            prompt=reduce_prompt, system_prompt=reduce_sys, model=model
        ):
            yield token
