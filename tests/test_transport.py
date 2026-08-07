import logging

import requests

from pyecobee import EcobeeTokensResponse, Utilities
from pyecobee.transport import HttpTransport


class Response(requests.Response):
    def __init__(self):
        super().__init__()

        self.status_code = 200
        self.request = requests.Request(
            "POST", "https://example.test?access_token=response-url-token"
        ).prepare()

    def json(self, **kwargs):
        return {
            "access_token": "response-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "response-refresh-token",
            "scope": "smartWrite",
        }


class Session(requests.Session):
    def request(self, *args, **kwargs):
        return Response()


def test_request_and_response_logs_omit_sensitive_data(caplog):
    caplog.set_level(logging.DEBUG)

    response = HttpTransport(Session()).request(
        "post",
        "https://example.test?client_id=url-application-key",
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
        "response-url-token",
        "url-application-key",
    ):
        assert secret not in logs
    assert "Sending POST request to https://example.test (timeout: 10s)" in logs
    assert "Received HTTP 200 from https://example.test" in logs
