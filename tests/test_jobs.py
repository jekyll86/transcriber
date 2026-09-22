"""Tests for Background Job Manager and streaming event queues."""

import pytest
from jobs import JobManager, Job


def test_job_lifecycle():
    manager = JobManager()
    job = manager.create_job("test_audio.mp3")

    assert job.job_id is not None
    assert job.filename == "test_audio.mp3"
    assert job.status == "queued"
    assert manager.get_job(job.job_id) is job

    # Status update
    manager.update_status(job.job_id, "converting", 25, "Decoding audio...")
    assert job.status == "converting"
    assert job.progress == 25
    assert job.message == "Decoding audio..."


@pytest.mark.asyncio
async def test_job_event_subscription():
    manager = JobManager()
    job = manager.create_job("test_stream.wav")

    queue = manager.subscribe(job.job_id)
    assert len(job.event_queues) == 1

    manager.emit(job.job_id, "segment", {"text": "Hello world", "start": 0.0, "end": 2.0})
    event = await queue.get()

    assert event["event"] == "segment"
    assert event["data"]["text"] == "Hello world"

    manager.unsubscribe(job.job_id, queue)
    assert len(job.event_queues) == 0
