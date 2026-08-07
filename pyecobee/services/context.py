"""Shared state used by the domain service components."""

import datetime
import logging
from collections.abc import Callable
from datetime import datetime as DateTime
from datetime import timedelta

import requests

from pyecobee.responses import EcobeeTokensResponse
from pyecobee.tokens import Tokens
from pyecobee.transport import HttpTransport
from pyecobee.utilities import process_http_response

logger = logging.getLogger(__name__)

EXPIRED_ACCESS_TOKEN_STATUS_CODE = 14


def _reports_an_expired_access_token(response: requests.Response) -> bool:
    """Return whether *response* is the ecobee "refresh your tokens" error."""
    if response.status_code == requests.codes.ok:
        return False

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError:
        # A body that is empty or is not JSON at all, such as a proxy error page.
        return False

    if not isinstance(payload, dict) or not isinstance(payload.get("status"), dict):
        return False

    return payload["status"].get("code") == EXPIRED_ACCESS_TOKEN_STATUS_CODE


class ClientContext:
    """Transport and authentication state shared by domain components."""

    __slots__ = (
        "_application_key",
        "_on_tokens_changed",
        "_thermostat_name",
        "_tokens",
        "_transport",
    )

    AUTHORIZE_URL = "https://api.ecobee.com/authorize"
    TOKENS_URL = "https://api.ecobee.com/token"
    THERMOSTAT_SUMMARY_URL = "https://api.ecobee.com/1/thermostatSummary"
    THERMOSTAT_URL = "https://api.ecobee.com/1/thermostat"
    METER_REPORT_URL = "https://api.ecobee.com/1/meterReport"
    RUNTIME_REPORT_URL = "https://api.ecobee.com/1/runtimeReport"
    GROUP_URL = "https://api.ecobee.com/1/group"
    HIERARCHY_SET_URL = "https://api.ecobee.com/1/hierarchy/set"
    HIERARCHY_USER_URL = "https://api.ecobee.com/1/hierarchy/user"
    HIERARCHY_THERMOSTAT_URL = "https://api.ecobee.com/1/hierarchy/thermostat"
    DEMAND_RESPONSE_URL = "https://api.ecobee.com/1/demandResponse"
    DEMAND_MANAGEMENT_URL = "https://api.ecobee.com/1/demandManagement"
    RUNTIME_REPORT_JOB_URL = "https://api.ecobee.com/1/runtimeReportJob"

    BEFORE_TIME_BEGAN_DATE_TIME = DateTime(2008, 1, 2, 0, 0, tzinfo=datetime.UTC)
    END_OF_TIME_DATE_TIME = DateTime(2035, 1, 1, 0, 0, tzinfo=datetime.UTC)

    # The ecobee API does not return a refresh token expiry. Since 2020-12-01 a
    # refresh token is documented to expire 30 days after it is issued.
    # https://developer.ecobee.com/home/developer/api/documentation/v1/auth/token-refresh.shtml
    REFRESH_TOKEN_LIFETIME = timedelta(days=30)

    # An access token is renewed this long before it expires so that a request
    # is not sent with credentials that lapse while it is in flight.
    ACCESS_TOKEN_REFRESH_MARGIN = timedelta(seconds=120)

    MINIMUM_COOLING_TEMPERATURE = -10.0
    MAXIMUM_COOLING_TEMPERATURE = 120.0
    MINIMUM_HEATING_TEMPERATURE = 45.0
    MAXIMUM_HEATING_TEMPERATURE = 120.0

    def __init__(
        self,
        thermostat_name: str,
        application_key: str,
        tokens: Tokens,
        on_tokens_changed: Callable[[Tokens], object],
    ) -> None:
        self._thermostat_name = thermostat_name
        self._application_key = application_key
        self._tokens = tokens
        self._on_tokens_changed = on_tokens_changed
        self._transport = HttpTransport()

    @property
    def thermostat_name(self) -> str:
        return self._thermostat_name

    @property
    def application_key(self) -> str:
        return self._application_key

    @property
    def tokens(self) -> Tokens:
        """Return the credentials currently held."""
        return self._tokens

    @property
    def transport(self) -> HttpTransport:
        """Return the transport, for requests that carry no access token."""
        return self._transport

    def store_tokens(self, tokens: Tokens) -> None:
        """Replace the credentials and hand them to the registered callback.

        Exceptions raised by the callback are deliberately not suppressed: a
        caller that cannot store its credentials must find out immediately.
        """
        self._tokens = tokens

        self._on_tokens_changed(tokens)

    def issue_tokens(
        self, grant_type: str, code: str | None, timeout: float = 5
    ) -> EcobeeTokensResponse:
        """Exchange *code* for credentials, then store and announce them.

        :param grant_type: "ecobeePin" for an initial request, otherwise
        "refresh_token"
        :param code: The authorization token, or the refresh token
        :param timeout: Number of seconds requests will wait to establish a
        connection and to receive a response
        :return: A TokensResponse object
        :rtype: EcobeeTokensResponse
        """
        issued_on = DateTime.now(datetime.UTC)
        response = self._transport.request(
            "post",
            ClientContext.TOKENS_URL,
            params={
                "client_id": self._application_key,
                "code": code,
                "grant_type": grant_type,
            },
            timeout=timeout,
        )
        tokens_response = process_http_response(response, EcobeeTokensResponse)

        self.store_tokens(
            self._tokens.replace(
                access_token=tokens_response.access_token,
                access_token_expires_on=issued_on
                + timedelta(seconds=tokens_response.expires_in),
                refresh_token=tokens_response.refresh_token,
                refresh_token_expires_on=issued_on + self.REFRESH_TOKEN_LIFETIME,
            )
        )

        return tokens_response

    def access_token_is_due_for_renewal(self) -> bool:
        """Return whether the access token should be renewed before a request.

        Renewal requires a refresh token. It happens when no access token is
        held at all, or when the one held expires within
        :attr:`ACCESS_TOKEN_REFRESH_MARGIN`. An access token of unknown expiry
        is left alone; an expired one is recognised from the response instead.
        """
        if self._tokens.refresh_token is None:
            return False

        if self._tokens.access_token is None:
            return True

        if self._tokens.access_token_expires_on is None:
            return False

        return (
            DateTime.now(datetime.UTC)
            >= self._tokens.access_token_expires_on - self.ACCESS_TOKEN_REFRESH_MARGIN
        )

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, object] | None = None,
        json_: object | None = None,
        timeout: float = 5,
    ) -> requests.Response:
        """Send an authenticated request, renewing credentials when needed.

        The access token is renewed before the request when it is about to
        expire, and once afterwards if ecobee reports that it already had.

        :param method: The HTTP method to use
        :param url: The ecobee API URL to send the request to
        :param params: Query parameters to send
        :param json_: The JSON body to send
        :param timeout: Number of seconds requests will wait to establish a
        connection and to receive a response
        :return: The HTTP response
        """
        if self.access_token_is_due_for_renewal():
            logger.debug("Renewing access token before it expires")
            self.issue_tokens(
                "refresh_token", self._tokens.refresh_token, timeout=timeout
            )

        response = self._authenticated_request(method, url, params, json_, timeout)

        if self._tokens.refresh_token is not None and _reports_an_expired_access_token(
            response
        ):
            logger.debug("Renewing access token after ecobee rejected it as expired")
            self.issue_tokens(
                "refresh_token", self._tokens.refresh_token, timeout=timeout
            )

            response = self._authenticated_request(method, url, params, json_, timeout)

        return response

    def _authenticated_request(
        self,
        method: str,
        url: str,
        params: dict[str, object] | None,
        json_: object | None,
        timeout: float,
    ) -> requests.Response:
        return self._transport.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {self._tokens.access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params=params,
            json_=json_,
            timeout=timeout,
        )
