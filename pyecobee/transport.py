"""Internal HTTP transport and safe diagnostic helpers."""

import logging
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

from pyecobee.exceptions import EcobeeRequestsException

logger = logging.getLogger(__name__)


def sanitize_url(url: str) -> str:
    """Remove query parameters and fragments from a URL before logging it."""
    parts = urlsplit(url)

    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


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
            "Sending %s request to %s (timeout: %ss)",
            method.upper(),
            sanitize_url(url),
            timeout,
        )

        try:
            return self._session.request(
                method, url, headers=headers, params=params, json=json_, timeout=timeout
            )
        except requests.exceptions.RequestException as exc:
            raise EcobeeRequestsException(
                f"{method.upper()} request to {sanitize_url(url)} failed"
            ) from exc
