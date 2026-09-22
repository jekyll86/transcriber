"""Tests for Transcriber outputs, timestamps, and formatting."""

import json
from transcribers.base import Segment, TranscriptionResult
from transcribers.factory import TranscriberFactory


def test_transcription_result_formatters():
    segments = [
        Segment(id=1, start=1.234, end=4.567, text="Hello world!"),
        Segment(id=2, start=5.000, end=7.890, text="This is a test transcription."),
    ]
    res = TranscriptionResult(
        text="Hello world! This is a test transcription.",
        segments=segments,
        language="en",
        duration=7.89,
    )

    # Plain text
    assert res.to_txt() == "Hello world! This is a test transcription."

    # SRT formatting
    srt = res.to_srt()
    assert "00:00:01,234 --> 00:00:04,567" in srt
    assert "Hello world!" in srt
    assert "00:00:05,000 --> 00:00:07,890" in srt

    # VTT formatting
    vtt = res.to_vtt()
    assert vtt.startswith("WEBVTT")
    assert "00:00:01.234 --> 00:00:04.567" in vtt

    # JSON formatting
    data = json.loads(res.to_json())
    assert data["language"] == "en"
    assert len(data["segments"]) == 2
    assert data["segments"][0]["text"] == "Hello world!"


def test_transcriber_factory():
    factory = TranscriberFactory()
    engines = factory.list_engines()
    engine_ids = [e["id"] for e in engines]
    assert "whisper.cpp" in engine_ids
    assert "faster-whisper" in engine_ids

    # Should safely retrieve the available engine (faster-whisper in this env)
    active = factory.get_transcriber()
    assert active.is_available()
