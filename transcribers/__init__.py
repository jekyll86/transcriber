"""Modular Transcriber Subsystem."""

from transcribers.base import BaseTranscriber, Segment, TranscriptionResult
from transcribers.whisper_cpp import WhisperCppTranscriber
from transcribers.faster_whisper import FasterWhisperTranscriber
from transcribers.factory import TranscriberFactory, transcriber_factory

__all__ = [
    "BaseTranscriber",
    "Segment",
    "TranscriptionResult",
    "WhisperCppTranscriber",
    "FasterWhisperTranscriber",
    "TranscriberFactory",
    "transcriber_factory",
]
