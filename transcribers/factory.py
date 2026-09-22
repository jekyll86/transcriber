"""Transcriber factory for dynamic engine resolution."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from transcribers.base import BaseTranscriber
from transcribers.whisper_cpp import WhisperCppTranscriber
from transcribers.faster_whisper import FasterWhisperTranscriber

logger = logging.getLogger(__name__)


class TranscriberFactory:
    """Factory and registry for transcriber engines."""

    def __init__(self):
        self._engines: Dict[str, BaseTranscriber] = {
            "whisper.cpp": WhisperCppTranscriber(),
            "faster-whisper": FasterWhisperTranscriber(),
        }

    def list_engines(self) -> List[Dict[str, object]]:
        return [
            {
                "id": engine_id,
                "display_name": engine.display_name,
                "available": engine.is_available(),
            }
            for engine_id, engine in self._engines.items()
        ]

    def get_transcriber(self, preferred_engine: Optional[str] = None) -> BaseTranscriber:
        """Get preferred transcriber if available, otherwise fallback to available engine."""
        if preferred_engine and preferred_engine in self._engines:
            engine = self._engines[preferred_engine]
            if engine.is_available():
                return engine
            logger.warning("Preferred engine %s unavailable; selecting fallback.", preferred_engine)

        # Priority 1: whisper.cpp
        if self._engines["whisper.cpp"].is_available():
            return self._engines["whisper.cpp"]

        # Priority 2: faster-whisper
        if self._engines["faster-whisper"].is_available():
            return self._engines["faster-whisper"]

        raise RuntimeError("No Whisper transcriber engines are available on this system.")


# Global factory instance
transcriber_factory = TranscriberFactory()
