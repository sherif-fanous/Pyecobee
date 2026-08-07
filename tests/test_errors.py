import pytest
import requests

from pyecobee import (
    EcobeeApiException,
    EcobeeAuthorizationException,
    EcobeeDeserializationException,
    EcobeeHttpException,
    EcobeeRequestsException,
    EcobeeStatusResponse,
    Utilities,
)
from pyecobee.transport import HttpTransport


class Response(requests.Response):
    def __init__(self, status_code, payload, url="https://example.test"):
        super().__init__()

        self.status_code = status_code
        self._payload = payload
        self.request = requests.Request("GET", url).prepare()

    def json(self, **kwargs):
        if isinstance(self._payload, Exception):
            raise self._payload

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
    with pytest.raises(EcobeeHttpException) as raised:
        Utilities.process_http_response(
            Response(500, {}, "https://example.test/path?access_token=secret"),
            EcobeeStatusResponse,
        )

    assert "secret" not in str(raised.value)


def test_requests_error_chains_underlying_exception():
    class FailingSession(requests.Session):
        def request(self, *args, **kwargs):
            raise requests.exceptions.ConnectionError("offline")

    with pytest.raises(EcobeeRequestsException) as raised:
        HttpTransport(FailingSession()).request(
            "get", "https://example.test/path?access_token=secret"
        )

    assert str(raised.value) == "GET request to https://example.test/path failed"
    assert isinstance(raised.value.__cause__, requests.exceptions.ConnectionError)


def test_malformed_json_is_propagated():
    with pytest.raises(ValueError, match="invalid JSON"):
        Utilities.process_http_response(
            Response(200, ValueError("invalid JSON")), EcobeeStatusResponse
        )


def not_json():
    """Return the failure requests raises for a body that is not JSON."""
    return requests.exceptions.JSONDecodeError("Expecting value", "<html>502</html>", 0)


def test_a_success_response_that_is_not_json_raises_a_typed_exception():
    with pytest.raises(EcobeeDeserializationException, match="not JSON"):
        Utilities.process_http_response(Response(200, not_json()), EcobeeStatusResponse)


def test_an_error_response_that_is_not_json_raises_a_typed_exception():
    with pytest.raises(EcobeeHttpException, match="HTTP error code => 502"):
        Utilities.process_http_response(Response(502, not_json()), EcobeeStatusResponse)
