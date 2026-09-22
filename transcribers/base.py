"""Base transcription interfaces and data models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any
try:
    import numpy as np
except ImportError:
    np = None
from pydantic import BaseModel, Field


class Segment(BaseModel):
    """A timestamped segment of transcription."""
    id: int
    start: float
    end: float
    text: str
    confidence: float | None = None


class TranscriptionResult(BaseModel):
    """Complete structured transcription result."""
    text: str
    segments: list[Segment] = Field(default_factory=list)
    language: str = "auto"
    duration: float = 0.0

    @staticmethod
    def _format_timestamp(seconds: float, srt_format: bool = True) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        delimiter = "," if srt_format else "."
        return f"{hrs:02d}:{mins:02d}:{secs:02d}{delimiter}{millis:03d}"

    def to_txt(self) -> str:
        return self.text.strip()

    def to_srt(self) -> str:
        lines = []
        for i, seg in enumerate(self.segments, start=1):
            start_str = self._format_timestamp(seg.start, srt_format=True)
            end_str = self._format_timestamp(seg.end, srt_format=True)
            lines.append(f"{i}\n{start_str} --> {end_str}\n{seg.text.strip()}\n")
        return "\n".join(lines).strip()

    def to_vtt(self) -> str:
        lines = ["WEBVTT\n"]
        for seg in self.segments:
            start_str = self._format_timestamp(seg.start, srt_format=False)
            end_str = self._format_timestamp(seg.end, srt_format=False)
            lines.append(f"{start_str} --> {end_str}\n{seg.text.strip()}\n")
        return "\n".join(lines).strip()

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


class BaseTranscriber(ABC):
    """Abstract base class for all transcriber implementations."""

    name: str = "base"
    display_name: str = "Base Transcriber"

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def transcribe(
        self,
        audio: Path | Any,
        model_name: str = "base",
        language: str | None = None,
        vad_filter: bool = True,
        on_segment: Callable[[Segment], None] | None = None,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """Perform audio transcription on 16kHz mono audio file or float32 NumPy array."""
        pass
