"""Requests must renew credentials before and after ecobee rejects them."""

from datetime import UTC, datetime, timedelta

import pytest
import requests

from pyecobee import (
    EcobeeHttpException,
    EcobeeService,
    Selection,
    SelectionType,
    Tokens,
)
from pyecobee.services.context import ClientContext
from pyecobee.transport import HttpTransport
from tests.support import APPLICATION_KEY, build_service

TOKENS_PAYLOAD = {
    "access_token": "renewed-access",
    "token_type": "Bearer",
    "expires_in": 3599,
    "refresh_token": "renewed-refresh",
    "scope": "smartWrite",
}
THERMOSTAT_PAYLOAD = {
    "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 0},
    "thermostatList": [],
    "status": {"code": 0, "message": ""},
}
EXPIRED_TOKEN_PAYLOAD = {
    "status": {"code": 14, "message": "Authentication token has expired."}
}
PROCESSING_ERROR_PAYLOAD = {"status": {"code": 3, "message": "Processing error."}}


def is_error(payload):
    """Return whether the API would answer *payload* with a failing status."""

    return set(payload) == {"status"} and payload["status"]["code"] != 0


def selection():
    return Selection(selection_type=SelectionType.REGISTERED, selection_match="")


@pytest.fixture
def exchange(monkeypatch, mock_response):
    """Record every request and reply with queued payloads."""

    sent = []

    def with_payloads(*payloads):
        remaining = list(payloads)

        def request(_transport, method, url, **kwargs):
            sent.append({"method": method, "url": url, **kwargs})
            payload = remaining.pop(0) if len(remaining) > 1 else remaining[0]

            return mock_response(
                status_code=500 if is_error(payload) else 200, payload=payload
            )

        monkeypatch.setattr(HttpTransport, "request", request)

        return sent

    return with_payloads


def service(**tokens):
    return build_service(**tokens)


def bearer_tokens(sent):
    return [
        request["headers"]["Authorization"]
        for request in sent
        if "headers" in request and request["headers"] is not None
    ]


def test_an_access_token_about_to_expire_is_renewed_first(exchange):
    sent = exchange(TOKENS_PAYLOAD, THERMOSTAT_PAYLOAD)
    ecobee_service = service(
        access_token="stale-access",
        refresh_token="old-refresh",
        access_token_expires_on=datetime.now(UTC) + timedelta(seconds=30),
    )

    ecobee_service.request_thermostats(selection())

    assert [request["url"] for request in sent] == [
        EcobeeService.TOKENS_URL,
        EcobeeService.THERMOSTAT_URL,
    ]
    assert bearer_tokens(sent) == ["Bearer renewed-access"]
    assert ecobee_service.access_token == "renewed-access"


def test_an_access_token_with_time_to_spare_is_left_alone(exchange):
    sent = exchange(THERMOSTAT_PAYLOAD)
    ecobee_service = service(
        access_token="good-access",
        refresh_token="old-refresh",
        access_token_expires_on=datetime.now(UTC) + timedelta(minutes=30),
    )

    ecobee_service.request_thermostats(selection())

    assert [request["url"] for request in sent] == [EcobeeService.THERMOSTAT_URL]
    assert bearer_tokens(sent) == ["Bearer good-access"]


def test_an_access_token_of_unknown_expiry_is_left_alone(exchange):
    sent = exchange(THERMOSTAT_PAYLOAD)

    service(
        access_token="good-access", refresh_token="old-refresh"
    ).request_thermostats(selection())

    assert [request["url"] for request in sent] == [EcobeeService.THERMOSTAT_URL]


def test_a_missing_access_token_is_obtained_before_the_request(exchange):
    sent = exchange(TOKENS_PAYLOAD, THERMOSTAT_PAYLOAD)

    service(refresh_token="old-refresh").request_thermostats(selection())

    assert [request["url"] for request in sent] == [
        EcobeeService.TOKENS_URL,
        EcobeeService.THERMOSTAT_URL,
    ]


def test_nothing_is_renewed_without_a_refresh_token(exchange):
    sent = exchange(THERMOSTAT_PAYLOAD)

    service(access_token="only-access").request_thermostats(selection())

    assert [request["url"] for request in sent] == [EcobeeService.THERMOSTAT_URL]


def test_a_rejected_access_token_is_renewed_and_the_request_retried(exchange):
    sent = exchange(EXPIRED_TOKEN_PAYLOAD, TOKENS_PAYLOAD, THERMOSTAT_PAYLOAD)
    ecobee_service = service(
        access_token="expired-access",
        refresh_token="old-refresh",
        access_token_expires_on=datetime.now(UTC) + timedelta(minutes=30),
    )

    response = ecobee_service.request_thermostats(selection())

    assert response.status.code == 0
    assert [request["url"] for request in sent] == [
        EcobeeService.THERMOSTAT_URL,
        EcobeeService.TOKENS_URL,
        EcobeeService.THERMOSTAT_URL,
    ]
    assert bearer_tokens(sent) == ["Bearer expired-access", "Bearer renewed-access"]


def test_a_request_is_retried_only_once(exchange):
    sent = exchange(EXPIRED_TOKEN_PAYLOAD, TOKENS_PAYLOAD, EXPIRED_TOKEN_PAYLOAD)
    ecobee_service = service(
        access_token="expired-access",
        refresh_token="old-refresh",
        access_token_expires_on=datetime.now(UTC) + timedelta(minutes=30),
    )

    with pytest.raises(Exception, match="ecobee API error"):
        ecobee_service.request_thermostats(selection())

    assert len(sent) == 3


def test_renewed_credentials_are_announced_once_per_renewal(exchange):
    exchange(EXPIRED_TOKEN_PAYLOAD, TOKENS_PAYLOAD, THERMOSTAT_PAYLOAD)
    announced = []
    ecobee_service = build_service(
        announced.append,
        access_token="expired-access",
        refresh_token="old-refresh",
        access_token_expires_on=datetime.now(UTC) + timedelta(minutes=30),
    )

    ecobee_service.request_thermostats(selection())

    assert len(announced) == 1
    assert announced[-1].refresh_token == "renewed-refresh"


def test_other_api_errors_are_not_treated_as_expired_credentials(exchange):
    sent = exchange(PROCESSING_ERROR_PAYLOAD)
    ecobee_service = service(access_token="access", refresh_token="old-refresh")

    with pytest.raises(Exception, match="ecobee API error"):
        ecobee_service.request_thermostats(selection())

    assert len(sent) == 1


def test_a_body_that_is_not_json_is_not_treated_as_expired_credentials(
    monkeypatch, mock_response
):
    """A proxy may answer with an error page rather than the ecobee API."""

    not_json = requests.Response()
    not_json.status_code = 502
    not_json._content = b"<html>502 Bad Gateway</html>"
    not_json.request = requests.Request("get", EcobeeService.THERMOSTAT_URL).prepare()
    sent = []

    def request(_transport, method, url, **kwargs):
        sent.append(url)

        return not_json

    monkeypatch.setattr(HttpTransport, "request", request)
    ecobee_service = service(access_token="access", refresh_token="old-refresh")

    with pytest.raises(EcobeeHttpException):
        ecobee_service.request_thermostats(selection())

    assert sent == [EcobeeService.THERMOSTAT_URL]


def test_documented_renewal_margin_is_two_minutes():
    assert ClientContext.ACCESS_TOKEN_REFRESH_MARGIN == timedelta(seconds=120)


def test_an_automatic_renewal_cannot_go_unstored(exchange):
    """Credentials cannot be renewed without somewhere to store them."""

    exchange(TOKENS_PAYLOAD, THERMOSTAT_PAYLOAD)

    with pytest.raises(TypeError, match="on_tokens_changed must be callable"):
        EcobeeService("test", APPLICATION_KEY, Tokens(refresh_token="r"), None)
