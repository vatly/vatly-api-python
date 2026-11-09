from typing import Any

from pydantic import BaseModel, model_validator


class VatlyModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def normalize_empty_metadata(cls, value: Any) -> Any:
        # PHP's empty associative arrays can serialize as [] instead of {}.
        if isinstance(value, dict) and value.get("metadata") == []:
            return {**value, "metadata": {}}
        return value
