from typing import Any, Generic, TypeVar
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, ConfigDict

from .models import PaginationLinks

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")
    data: list[T]
    count: int
    links: PaginationLinks


def next_params(page: Page[Any], params: dict[str, Any], seen: set[str]) -> dict[str, Any] | None:
    if page.links.next is None:
        return None
    cursor = parse_qs(urlparse(page.links.next.href).query).get("startingAfter", [None])[0]
    if not cursor or cursor in seen:
        raise VatlyPaginationError("Invalid or repeated pagination cursor")
    seen.add(cursor)
    return {k: v for k, v in {**params, "startingAfter": cursor}.items() if k != "endingBefore"}


class VatlyPaginationError(ValueError):
    pass
