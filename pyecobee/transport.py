"""Internal HTTP transport and safe diagnostic helpers."""

import json
import logging
from typing import Any

import requests

from pyecobee.exceptions import EcobeeRequestsException

logger = logging.getLogger(__name__)

_SECRET_FIELDS = {
    "access_token",
    "application_key",
    "authorization",
    "authorization_code",
    "client_id",
    "client_secret",
    "code",
    "password",
    "refresh_token",
    "token",
}


def redact(value: Any) -> Any:
    """Return a copy of headers or JSON-compatible data without credentials."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in _SECRET_FIELDS else redact(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact(item) for item in value]

    return value


class HttpTransport:
    """Small session-backed boundary for all Ecobee HTTP requests."""

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: Any = None,
        json_: Any = None,
        timeout: float = 5,
    ) -> requests.Response:
        headers = headers or {}

        logger.debug(
            "Request\n[Method]\n========\n%s\n\n[URL]\n=====\n%s\n%s%s%s".strip(),
            method.upper(),
            url,
            f"\n[Query Parameters]\n==================\n{json.dumps(redact(params), sort_keys=True, indent=2)}\n"
            if params is not None
            else "",
            f"\n[Headers]\n=========\n{json.dumps(redact(headers), sort_keys=True, indent=2)}\n",
            f"\n[JSON]\n======\n{json.dumps(redact(json_), sort_keys=True, indent=2)}\n"
            if json_ is not None
            else "",
        )

        try:
            return self._session.request(
                method, url, headers=headers, params=params, json=json_, timeout=timeout
            )
        except requests.exceptions.RequestException as exc:
            logger.exception("HTTP request failed")

            raise EcobeeRequestsException(str(exc)) from exc
