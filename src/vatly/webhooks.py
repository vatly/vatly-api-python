"""Raw-body HMAC verification and typed, forward-compatible webhook deliveries."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
import time
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .errors import VatlyInvalidSignatureError
from .models import WebhookDelivery

VATLY_SIGNATURE_HEADER = "Vatly-Signature"
VATLY_EVENT_ID_HEADER = "Vatly-Event-Id"
WEBHOOK_EVENT_NAMES: tuple[str, ...] = get_args(
    WebhookDelivery.model_fields["event_name"].annotation
)


class KnownWebhookEvent(WebhookDelivery):
    known: Literal[True] = True


class UnsupportedWebhookEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    known: Literal[False] = False
    id: str
    resource: Literal["webhook_event"]
    event_name: str = Field(alias="eventName")
    reason: str | None
    entity_type: str = Field(alias="entityType")
    entity_id: str = Field(alias="entityId")
    object: Any
    created_at: datetime = Field(alias="createdAt")
    testmode: bool


VatlyWebhookEvent = KnownWebhookEvent | UnsupportedWebhookEvent


def compute_signature_v1(raw_body: bytes | str, secret: str, timestamp: int) -> str:
    if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp < 0:
        raise ValueError("timestamp must be a non-negative integer")
    body = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
    return hmac.new(
        secret.encode("utf-8"), str(timestamp).encode() + b"." + body, hashlib.sha256
    ).hexdigest()


def verify_webhook_signature(
    raw_body: bytes | str,
    signature_header: str | None,
    secret: str | Sequence[str],
    *,
    tolerance: float = 300,
    now: float | None = None,
) -> None:
    """Verify exact bytes. Zero tolerance disables freshness, not deduplication."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    secrets = [secret] if isinstance(secret, str) else list(secret)
    if not secrets or any(not s for s in secrets):
        raise VatlyInvalidSignatureError("At least one non-empty webhook secret is required")
    if not signature_header:
        raise VatlyInvalidSignatureError("Missing webhook signature")
    parts = {}
    for piece in signature_header.split(","):
        key, sep, value = piece.strip().partition("=")
        if sep:
            parts[key.strip()] = value.strip()
    stamp = parts.get("t", "")
    signature = parts.get("v1", "")
    if not re.fullmatch(r"[0-9]{1,15}", stamp) or not re.fullmatch(r"[0-9a-fA-F]{64}", signature):
        raise VatlyInvalidSignatureError("Malformed timestamp or v1 signature")
    timestamp = int(stamp)
    current = time.time() if now is None else now
    if not math.isfinite(current):
        raise ValueError("now must be finite")
    if tolerance and abs(current - timestamp) > tolerance:
        raise VatlyInvalidSignatureError("Webhook timestamp outside tolerance")
    valid = False
    for candidate in secrets:
        valid |= hmac.compare_digest(
            compute_signature_v1(raw_body, candidate, timestamp), signature.lower()
        )
    if not valid:
        raise VatlyInvalidSignatureError("Invalid webhook signature")


def is_valid_webhook_signature(
    raw_body: bytes | str,
    signature_header: str | None,
    secret: str | Sequence[str],
    *,
    tolerance: float = 300,
    now: float | None = None,
) -> bool:
    try:
        verify_webhook_signature(raw_body, signature_header, secret, tolerance=tolerance, now=now)
        return True
    except VatlyInvalidSignatureError:
        return False


def construct_event(
    raw_body: bytes | str,
    signature_header: str | None,
    secret: str | Sequence[str],
    *,
    tolerance: float = 300,
    now: float | None = None,
) -> WebhookDelivery:
    verify_webhook_signature(raw_body, signature_header, secret, tolerance=tolerance, now=now)
    try:
        return WebhookDelivery.model_validate_json(raw_body)
    except ValidationError as exc:
        raise VatlyInvalidSignatureError("Invalid webhook JSON or envelope") from exc


def construct_webhook_event(
    raw_body: bytes | str,
    signature_header: str | None,
    secret: str | Sequence[str],
    *,
    tolerance: float = 300,
    now: float | None = None,
) -> VatlyWebhookEvent:
    verify_webhook_signature(raw_body, signature_header, secret, tolerance=tolerance, now=now)
    try:
        payload = json.loads(raw_body)
        if not isinstance(payload, dict):
            raise ValueError("Envelope must be an object")
        # `known` is SDK-owned; never trust a supplied discriminator.
        payload.pop("known", None)
        if payload.get("eventName") in WEBHOOK_EVENT_NAMES:
            return KnownWebhookEvent.model_validate(payload)
        return UnsupportedWebhookEvent.model_validate(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        raise VatlyInvalidSignatureError("Invalid webhook JSON or envelope") from exc
