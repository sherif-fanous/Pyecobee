import pytest
import requests

from pyecobee import (
    EcobeeApiException,
    EcobeeAuthorizationException,
    EcobeeHttpException,
    EcobeeRequestsException,
    EcobeeStatusResponse,
    Utilities,
)


class Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.request = type("Request", (), {"url": "https://example.test"})()

    def json(self):
        return self._payload


def test_authorization_error_response_raises_typed_exception():
    with pytest.raises(EcobeeAuthorizationException) as raised:
        Utilities.process_http_response(
            Response(
                400,
                {
                    "error": "invalid_client",
                    "error_description": "bad client",
                    "error_uri": "https://example.test/error",
                },
            ),
            EcobeeStatusResponse,
        )

    assert raised.value.error == "invalid_client"


def test_api_error_response_raises_typed_exception():
    with pytest.raises(EcobeeApiException) as raised:
        Utilities.process_http_response(
            Response(
                400,
                {"status": {"code": 14, "message": "Authentication token has expired"}},
            ),
            EcobeeStatusResponse,
        )

    assert raised.value.status_code == 14


def test_unstructured_http_error_raises_typed_exception():
    with pytest.raises(EcobeeHttpException):
        Utilities.process_http_response(Response(500, {}), EcobeeStatusResponse)


def test_requests_error_chains_underlying_exception():
    def fail(*args, **kwargs):
        raise requests.exceptions.ConnectionError("offline")

    with pytest.raises(EcobeeRequestsException) as raised:
        Utilities.make_http_request(fail, "https://example.test")

    assert isinstance(raised.value.__cause__, requests.exceptions.ConnectionError)
