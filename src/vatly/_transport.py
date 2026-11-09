from __future__ import annotations

import asyncio
import math
import os
import platform
import random
import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, TypeVar, cast
from uuid import uuid4

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError
from typing_extensions import Self

from ._version import __version__
from .errors import (
    VatlyApiError,
    VatlyConnectionError,
    VatlyError,
    VatlyTimeoutError,
    error_from_response,
)

T = TypeVar("T")
VATLY_BASE_URL = "https://api.vatly.com/v1"


@dataclass(frozen=True)
class RequestOptions:
    """Per-request overrides. Timeouts are seconds; zero disables the timeout."""

    idempotency_key: str | None = None
    timeout: float | None = None
    headers: Mapping[str, str] | None = None


def _timeout(value: float) -> float | None:
    if not math.isfinite(value) or value < 0:
        raise ValueError("timeout must be finite and non-negative")
    return value or None


def _retry_after(value: str | None) -> float | None:
    if not value:
        return None
    if value.strip().isdigit():
        return float(value)
    try:
        date = parsedate_to_datetime(value)
        return max(0, (date - datetime.now(timezone.utc)).total_seconds())
    except (ValueError, TypeError, OverflowError):
        return None


class _Transport:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = VATLY_BASE_URL,
        timeout: float = 30,
        max_retries: int = 2,
        default_headers: Mapping[str, str] | None = None,
        idempotency_key_generator: Callable[[], str] | None = lambda: str(uuid4()),
        client_info: Mapping[str, str] | bool = True,
        transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None = None,
    ) -> None:
        key = api_key if api_key is not None else os.environ.get("VATLY_API_KEY", "")
        if not re.fullmatch(r"(live|test)_[\w|]{18,}", key, flags=re.ASCII):
            raise ValueError("Pass a valid live_ or test_ API key or set VATLY_API_KEY")
        _timeout(timeout)
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        self.mode = "test" if key.startswith("test_") else "live"
        self.base_url = base_url.rstrip("/")
        url = httpx.URL(self.base_url)
        if url.scheme not in {"http", "https"} or not url.host or url.query or url.fragment:
            raise ValueError("base_url must be an HTTP(S) URL without query or fragment")
        self.timeout = timeout
        self.max_retries = max_retries
        self._key_generator = idempotency_key_generator
        self._headers = httpx.Headers(
            {
                "Authorization": f"Bearer {key}",
                "Accept": "application/json",
                "User-Agent": f"vatly-sdk-python/{__version__}",
            }
        )
        self._headers.update(default_headers or {})
        if client_info is not False:
            info = f"sdk=vatly-sdk-python/{__version__}; runtime=python/{platform.python_version()}; os={platform.system()}; arch={platform.machine()}"
            if isinstance(client_info, Mapping):
                for name in ("app", "framework"):
                    value = re.sub(r"[\r\n;,]|\s+", " ", client_info.get(name, "")).strip()[:64]
                    if value:
                        info += f"; {name}={value}"
            self._headers["Vatly-Client-Info"] = info
        self._custom_transport = transport
        self._init_http()

    def _init_http(self) -> None:
        raise NotImplementedError

    @staticmethod
    def serialize(value: BaseModel | dict[str, Any] | None) -> dict[str, Any] | None:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json", by_alias=True, exclude_unset=True)
        return dict(value) if value is not None else None

    def _prepare(
        self,
        method: str,
        path: str,
        body: BaseModel | dict[str, Any] | None,
        params: BaseModel | dict[str, Any] | None,
        options: RequestOptions | None,
    ) -> tuple[dict[str, Any], bool]:
        opts = options or RequestOptions()
        headers = self._headers.copy()
        headers.update(opts.headers or {})
        key = opts.idempotency_key
        if key is None:
            key = headers.get("Idempotency-Key")
        if key is None and method in {"POST", "PATCH", "PUT", "DELETE"} and self._key_generator:
            key = self._key_generator()
        if key:
            headers["Idempotency-Key"] = key
        elif "Idempotency-Key" in headers:
            del headers["Idempotency-Key"]
        query = self.serialize(params) or {}
        if query.get("startingAfter") is not None and query.get("endingBefore") is not None:
            raise ValueError("startingAfter and endingBefore are mutually exclusive")
        query = {k: int(v) if isinstance(v, bool) else v for k, v in query.items() if v is not None}
        return {
            "method": method,
            "url": self.base_url + path,
            "headers": headers,
            "params": query,
            "json": self.serialize(body),
            "timeout": _timeout(self.timeout if opts.timeout is None else opts.timeout),
        }, method in {"GET", "HEAD", "OPTIONS"} or bool(key)

    @staticmethod
    def _parse(response: httpx.Response, response_type: type[T]) -> T:
        if not response.is_success:
            try:
                body = response.json()
            except ValueError:
                body = response.text
            raise error_from_response(
                response.status_code,
                body,
                str(response.request.url),
                response.request.method,
                _retry_after(response.headers.get("Retry-After")),
            )
        try:
            if response.status_code == 204 or not response.content:
                return cast(T, None)
            return TypeAdapter(response_type).validate_json(response.content)
        except (ValueError, ValidationError) as exc:
            raise VatlyApiError(
                "Invalid Vatly response",
                status=response.status_code,
                body=response.text,
                url=str(response.request.url),
                method=response.request.method,
            ) from exc

    @staticmethod
    def _delay(error: VatlyError, attempt: int, retryable: bool, max_retries: int) -> float:
        can_retry = (
            isinstance(error, VatlyConnectionError)
            or error.status == 429
            or error.status >= 500
            or (error.status == 409 and error.details.get("idempotency_outcome") == "in_progress")
        )
        if not retryable or attempt >= max_retries or not can_retry:
            raise error
        if error.retry_after is not None:
            return error.retry_after
        base = min(0.25 * 2.0 ** min(attempt, 6), 8.0)
        return base + random.random() * base * 0.25


class SyncTransport(_Transport):
    def _init_http(self) -> None:
        if self._custom_transport is not None and not isinstance(
            self._custom_transport, httpx.BaseTransport
        ):
            raise TypeError("Sync client requires an httpx.BaseTransport")
        self._http = httpx.Client(transport=self._custom_transport, follow_redirects=False)

    def request(
        self,
        method: str,
        path: str,
        response_type: type[T],
        *,
        body: BaseModel | dict[str, Any] | None = None,
        params: BaseModel | dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> T:
        kwargs, retryable = self._prepare(method, path, body, params, options)
        for attempt in range(self.max_retries + 1):
            try:
                response = self._http.request(**kwargs)
                return self._parse(response, response_type)
            except httpx.TimeoutException as exc:
                error: VatlyError = VatlyTimeoutError("Vatly request timed out")
                error.__cause__ = exc
            except httpx.TransportError as exc:
                error = VatlyConnectionError("Vatly connection failed")
                error.__cause__ = exc
            except VatlyError as exc:
                error = exc
            time.sleep(self._delay(error, attempt, retryable, self.max_retries))
        raise AssertionError("unreachable")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncTransport(_Transport):
    def _init_http(self) -> None:
        if self._custom_transport is not None and not isinstance(
            self._custom_transport, httpx.AsyncBaseTransport
        ):
            raise TypeError("Async client requires an httpx.AsyncBaseTransport")
        self._http = httpx.AsyncClient(transport=self._custom_transport, follow_redirects=False)

    async def request(
        self,
        method: str,
        path: str,
        response_type: type[T],
        *,
        body: BaseModel | dict[str, Any] | None = None,
        params: BaseModel | dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> T:
        kwargs, retryable = self._prepare(method, path, body, params, options)
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http.request(**kwargs)
                return self._parse(response, response_type)
            except httpx.TimeoutException as exc:
                error: VatlyError = VatlyTimeoutError("Vatly request timed out")
                error.__cause__ = exc
            except httpx.TransportError as exc:
                error = VatlyConnectionError("Vatly connection failed")
                error.__cause__ = exc
            except VatlyError as exc:
                error = exc
            await asyncio.sleep(self._delay(error, attempt, retryable, self.max_retries))
        raise AssertionError("unreachable")

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
