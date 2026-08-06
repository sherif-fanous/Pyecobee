"""Shared Pydantic v2 configuration for ecobee API models."""

from __future__ import annotations

from pprint import pformat
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class EcobeeObject(BaseModel):
    """Strict model used when constructing an ecobee request payload."""

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
    )
    _model_namespace: ClassVar[dict[str, type[EcobeeObject]]] = {}

    def to_api_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible ecobee payload without unset values."""
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")

    def pretty_format(self, indent: int = 2, sort_attributes: bool = True) -> str:
        """Return a readable representation using ecobee field aliases."""
        return f"{type(self).__name__}({pformat(self.to_api_dict(), indent=indent, sort_dicts=sort_attributes)})"


class EcobeeResponseObject(EcobeeObject):
    """Tolerant model used for API responses, including future API fields."""

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        extra="ignore",
    )
