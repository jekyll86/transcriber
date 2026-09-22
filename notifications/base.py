"""Base notification models and abstract interface.

Follows the Strategy Pattern to decouple notification channels from the core pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field


class NotificationPayload(BaseModel):
    """Strongly typed DTO containing transcription and summary results for dispatch."""
    task_id: str
    filename: str
    duration_seconds: float = 0.0
    processing_time_seconds: float = 0.0
    whisper_model: str = "base"
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    summary_type: Optional[str] = None
    transcript_text: str = ""
    summary_text: Optional[str] = None
    polished_text: Optional[str] = None
    attachment_files: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationResult(BaseModel):
    """Result of a notification delivery attempt."""
    provider: str
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_details: Optional[str] = None


class BaseNotifier(ABC):
    """Abstract base class for all notification providers (Open/Closed Principle)."""

    name: str = "base"
    display_name: str = "Base Notifier"

    @abstractmethod
    def is_configured(self) -> bool:
        """Check whether the notifier has the required credentials and is enabled."""
        pass

    @abstractmethod
    async def send(self, payload: NotificationPayload) -> NotificationResult:
        """Dispatch notification payload to this channel."""
        pass

    @abstractmethod
    async def test_connection(self) -> NotificationResult:
        """Test authentication and connectivity with the notification service."""
        pass
