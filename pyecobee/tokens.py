"""Serializable authentication state for :class:`~pyecobee.service.EcobeeService`."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, replace
from datetime import datetime as DateTime
from typing import Any

from pyecobee.enumerations import Scope

__all__ = ["Tokens"]


def _to_text(value: DateTime | None) -> str | None:
    """Return an ISO 8601 representation of an expiry."""

    return None if value is None else value.isoformat()


def _to_date_time(value: str | DateTime | None) -> DateTime | None:
    """Return a timezone aware expiry, assuming UTC when none is given."""

    if value is None:
        return None

    date_time = value if isinstance(value, DateTime) else DateTime.fromisoformat(value)

    if date_time.tzinfo is None:
        return date_time.replace(tzinfo=datetime.UTC)

    return date_time


@dataclass(frozen=True, slots=True)
class Tokens:
    """The credentials the ecobee API requires an application to store.

    Instances are immutable snapshots. Use :meth:`to_dict` to persist them as
    JSON and :meth:`from_dict` to restore them.
    """

    authorization_token: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    access_token_expires_on: DateTime | None = None
    refresh_token_expires_on: DateTime | None = None
    scope: Scope = Scope.SMART_WRITE

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "access_token_expires_on", _to_date_time(self.access_token_expires_on)
        )
        object.__setattr__(
            self,
            "refresh_token_expires_on",
            _to_date_time(self.refresh_token_expires_on),
        )
        object.__setattr__(self, "scope", Scope(self.scope))

    def __repr__(self) -> str:
        """Return a representation that does not disclose the credentials."""

        present = ", ".join(
            name
            for name in ("authorization_token", "access_token", "refresh_token")
            if getattr(self, name) is not None
        )

        return (
            f"Tokens(held={present or 'none'}, "
            f"access_token_expires_on={self.access_token_expires_on!r}, "
            f"refresh_token_expires_on={self.refresh_token_expires_on!r}, "
            f"scope={self.scope!r})"
        )

    def replace(self, **changes: Any) -> Tokens:
        """Return a copy of these tokens with *changes* applied."""

        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping of the credentials."""

        return {
            "authorization_token": self.authorization_token,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_token_expires_on": _to_text(self.access_token_expires_on),
            "refresh_token_expires_on": _to_text(self.refresh_token_expires_on),
            "scope": self.scope.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tokens:
        """Construct credentials from a mapping produced by :meth:`to_dict`."""

        recognized = {
            name: data[name] for name in cls.__dataclass_fields__ if name in data
        }

        return cls(**recognized)
