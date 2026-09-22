"""Tests for notification providers, payload models, and dispatcher."""

import pytest
from notifications.base import NotificationPayload, NotificationResult
from notifications.telegram import TelegramNotifier
from notifications.webhook import WebhookNotifier
from notifications.dispatcher import NotificationDispatcher


def test_notification_payload_creation():
    payload = NotificationPayload(
        task_id="abc12345",
        filename="meeting.mp3",
        duration_seconds=120.5,
        processing_time_seconds=3.2,
        whisper_model="base",
        summary_text="Discussed Q3 deliverables and timeline.",
        transcript_text="Okay everyone let's begin the Q3 meeting...",
    )
    assert payload.filename == "meeting.mp3"
    assert payload.duration_seconds == 120.5


def test_telegram_message_formatting():
    notifier = TelegramNotifier(bot_token="fake_token", chat_id="123456", enabled=True)
    assert notifier.is_configured()

    payload = NotificationPayload(
        task_id="test1",
        filename="interview.wav",
        duration_seconds=90.0,
        processing_time_seconds=2.5,
        whisper_model="base",
        summary_type="bullets",
        summary_text="- Key topic 1\n- Key topic 2",
    )
    msg = notifier._format_message(payload)
    assert "interview.wav" in msg
    assert "1.5 min" in msg
    assert "Key topic 1" in msg


def test_webhook_notifier_configuration():
    notifier = WebhookNotifier(webhook_url="https://example.com/webhook", secret="topsecret")
    assert notifier.is_configured()

    unconfigured = WebhookNotifier()
    assert not unconfigured.is_configured()


@pytest.mark.asyncio
async def test_notification_dispatcher():
    dispatcher = NotificationDispatcher(load_defaults=False)
    assert len(dispatcher.list_providers()) == 0

    dummy_payload = NotificationPayload(
        task_id="d1",
        filename="dummy.wav",
        transcript_text="Test",
    )

    # Dispatch with no providers should return empty list without error
    results = await dispatcher.dispatch_all(dummy_payload)
    assert results == []
