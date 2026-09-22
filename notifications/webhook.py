"""Generic Webhook notification provider.

Dispatches a standard JSON payload via HTTP POST to any webhook endpoint
(e.g., n8n, Make, Zapier, Discord/Slack incoming webhook adapters).
"""

from __future__ import annotations

import logging
from typing import Optional
import httpx

from notifications.base import BaseNotifier, NotificationPayload, NotificationResult

logger = logging.getLogger(__name__)


class WebhookNotifier(BaseNotifier):
    """Dispatches JSON payload to a specified webhook URL."""

    name: str = "webhook"
    display_name: str = "Generic Webhook"

    def __init__(self, webhook_url: Optional[str] = None, secret: Optional[str] = None, enabled: bool = True):
        self.webhook_url = webhook_url
        self.secret = secret
        self.enabled = enabled

    def is_configured(self) -> bool:
        return bool(self.enabled and self.webhook_url)

    async def send(self, payload: NotificationPayload) -> NotificationResult:
        if not self.is_configured():
            return NotificationResult(
                provider=self.name,
                success=False,
                message="Webhook notifier is disabled or missing URL.",
            )

        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["X-Webhook-Secret"] = self.secret

        data = {
            "event": "transcription_complete",
            "task_id": payload.task_id,
            "filename": payload.filename,
            "duration_seconds": payload.duration_seconds,
            "processing_time_seconds": payload.processing_time_seconds,
            "whisper_model": payload.whisper_model,
            "llm_provider": payload.llm_provider,
            "llm_model": payload.llm_model,
            "summary_type": payload.summary_type,
            "transcript_text": payload.transcript_text,
            "summary_text": payload.summary_text,
            "polished_text": payload.polished_text,
            "created_at": payload.created_at.isoformat(),
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(str(self.webhook_url), json=data, headers=headers)
                if 200 <= resp.status_code < 300:
                    return NotificationResult(
                        provider=self.name,
                        success=True,
                        message=f"Webhook delivered successfully (HTTP {resp.status_code})",
                    )
                else:
                    return NotificationResult(
                        provider=self.name,
                        success=False,
                        message=f"Webhook endpoint returned HTTP {resp.status_code}",
                        error_details=resp.text,
                    )
        except Exception as e:
            logger.exception("Webhook notification failed")
            return NotificationResult(
                provider=self.name,
                success=False,
                message="Failed to deliver webhook",
                error_details=str(e),
            )

    async def test_connection(self) -> NotificationResult:
        if not self.webhook_url:
            return NotificationResult(
                provider=self.name,
                success=False,
                message="Webhook URL is not configured.",
            )

        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["X-Webhook-Secret"] = self.secret

        test_data = {"event": "ping", "message": "Test connection from Audio Transcriber"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(str(self.webhook_url), json=test_data, headers=headers)
                if 200 <= resp.status_code < 300:
                    return NotificationResult(
                        provider=self.name,
                        success=True,
                        message=f"Webhook ping acknowledged (HTTP {resp.status_code})",
                    )
                else:
                    return NotificationResult(
                        provider=self.name,
                        success=False,
                        message=f"Webhook ping returned HTTP {resp.status_code}",
                        error_details=resp.text,
                    )
        except Exception as e:
            return NotificationResult(
                provider=self.name,
                success=False,
                message="Network error reaching webhook URL",
                error_details=str(e),
            )
