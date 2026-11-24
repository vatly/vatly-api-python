from typing import Any

from pydantic import BaseModel, RootModel, model_validator
from pydantic_core import to_jsonable_python


class VatlyModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def normalize_empty_metadata(cls, value: Any) -> Any:
        # PHP's empty associative arrays can serialize as [] instead of {}.
        if isinstance(value, dict) and value.get("metadata") == []:
            return {**value, "metadata": {}}
        return value

    @model_validator(mode="after")
    def check_request_metadata(self) -> "VatlyModel":
        for name, field in type(self).model_fields.items():
            extra = field.json_schema_extra
            if not isinstance(extra, dict) or not extra.get("x-vatly-request-metadata"):
                continue
            value = getattr(self, name)
            data = value.root if isinstance(value, RootModel) else value
            if data is None:
                continue
            if not isinstance(data, dict) or len(data) > 50:
                raise ValueError("metadata must be an object with at most 50 keys")
            for key, item in data.items():
                if not isinstance(key, str) or len(key) > 40:
                    raise ValueError("metadata keys must be strings of at most 40 characters")
                if not isinstance(item, str) or len(item) > 500:
                    raise ValueError("metadata values must be strings of at most 500 characters")
        return self


def to_wire(value: Any) -> Any:
    """Serialize a request for the API: spec-defined fields only, null only where allowed."""
    if isinstance(value, RootModel):
        return to_wire(value.root)
    if isinstance(value, BaseModel):
        result = {}
        for name, field in type(value).model_fields.items():
            if name not in value.model_fields_set:
                continue
            item = getattr(value, name)
            extra = field.json_schema_extra
            if item is None and not (isinstance(extra, dict) and extra.get("x-vatly-nullable")):
                continue
            result[field.alias or name] = to_wire(item)
        return result
    if isinstance(value, (list, tuple)):
        return [to_wire(item) for item in value]
    if isinstance(value, dict):
        return {key: to_wire(item) for key, item in value.items()}
    return to_jsonable_python(value)
