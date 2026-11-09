"""Typed Vatly API, transport, and webhook errors."""

from typing import Any


class VatlyError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status: int = 0,
        body: Any = None,
        url: str | None = None,
        method: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
        self.url = url
        self.method = method
        self.retry_after = retry_after
        self.details: dict[str, Any] = body.get("details", {}) if isinstance(body, dict) else {}
        self.errors: dict[str, list[str]] = body.get("errors", {}) if isinstance(body, dict) else {}


class VatlyAuthError(VatlyError):
    pass


class VatlyForbiddenError(VatlyError):
    pass


class VatlyNotFoundError(VatlyError):
    pass


class VatlyConflictError(VatlyError):
    pass


class VatlyValidationError(VatlyError):
    pass


class VatlyRateLimitError(VatlyError):
    pass


class VatlyApiError(VatlyError):
    pass


class VatlyConnectionError(VatlyError):
    pass


class VatlyTimeoutError(VatlyConnectionError):
    pass


class VatlyInvalidSignatureError(Exception):
    pass


def error_from_response(
    status: int, body: Any, url: str, method: str, retry_after: float | None
) -> VatlyError:
    cls = {
        401: VatlyAuthError,
        403: VatlyForbiddenError,
        404: VatlyNotFoundError,
        409: VatlyConflictError,
        422: VatlyValidationError,
        429: VatlyRateLimitError,
    }.get(status, VatlyApiError)
    message = body.get("message") if isinstance(body, dict) else None
    return cls(
        message if isinstance(message, str) else f"Vatly API error ({status}).",
        status=status,
        body=body,
        url=url,
        method=method,
        retry_after=retry_after,
    )
