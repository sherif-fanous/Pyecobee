"""File backed storage for the credentials the ecobee API issues."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from pyecobee.tokens import Tokens

__all__ = ["JsonFileTokenStore"]

logger = logging.getLogger(__name__)


class JsonFileTokenStore:
    """Store credentials as JSON in a file only the owner can read.

    Pass :meth:`load` and :meth:`save` to
    :class:`~pyecobee.service.EcobeeService` as its credentials and its
    callback::

        store = JsonFileTokenStore("~/.config/pyecobee/tokens.json")
        service = EcobeeService("My Thermostat", key, store.load(), store.save)
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path).expanduser()

    def load(self) -> Tokens:
        """Return the stored credentials, or empty ones when none are stored."""

        try:
            return Tokens.from_dict(json.loads(self._path.read_text()))
        except FileNotFoundError:
            return Tokens()

    def save(self, tokens: Tokens) -> None:
        """Store *tokens*, replacing the file in a single step."""

        self._path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = self._path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(tokens.to_dict(), indent=2))
        temporary_path.chmod(0o600)
        os.replace(temporary_path, self._path)

        logger.debug(
            "Stored credentials expiring on %s", tokens.access_token_expires_on
        )
