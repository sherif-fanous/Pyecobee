import logging

from pyecobee import EcobeeTokensResponse, Utilities
from pyecobee.transport import HttpTransport


class Response:
    status_code = 200
    request = type("Request", (), {"url": "https://example.test"})()

    def json(self):
        return {
            "access_token": "response-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "response-refresh-token",
            "scope": "smartWrite",
        }


class Session:
    def request(self, *args, **kwargs):
        return Response()


def test_request_and_response_logs_redact_credentials(caplog):
    caplog.set_level(logging.DEBUG)
    response = HttpTransport(Session()).request(
        "post",
        "https://example.test",
        headers={"Authorization": "Bearer secret-token"},
        params={"client_id": "application-key", "code": "authorization-code"},
        json_={"refresh_token": "refresh-token", "password": "password-value"},
        timeout=10,
    )

    Utilities.process_http_response(response, EcobeeTokensResponse)

    logs = caplog.text
    for secret in (
        "secret-token",
        "application-key",
        "authorization-code",
        "refresh-token",
        "password-value",
        "response-token",
        "response-refresh-token",
    ):
        assert secret not in logs
    assert "[REDACTED]" in logs
