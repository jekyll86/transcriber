"""Modular Notification Subsystem."""

from notifications.base import BaseNotifier, NotificationPayload, NotificationResult
from notifications.telegram import TelegramNotifier
from notifications.webhook import WebhookNotifier
from notifications.dispatcher import NotificationDispatcher, dispatcher

__all__ = [
    "BaseNotifier",
    "NotificationPayload",
    "NotificationResult",
    "TelegramNotifier",
    "WebhookNotifier",
    "NotificationDispatcher",
    "dispatcher",
]
