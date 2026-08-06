"""Token expiries must reflect what the ecobee API documents."""

from datetime import UTC, datetime, timedelta

import pytest

from pyecobee.services.context import ClientContext
from pyecobee.transport import HttpTransport
from tests.support import build_service

TOKENS_PAYLOAD = {
    "access_token": "new-access",
    "token_type": "Bearer",
    "expires_in": 3599,
    "refresh_token": "new-refresh",
    "scope": "smartWrite",
}


@pytest.fixture
def service(monkeypatch, mock_response):
    def request(_transport, method, url, **kwargs):
        return mock_response(payload=TOKENS_PAYLOAD)

    monkeypatch.setattr(HttpTransport, "request", request)

    return build_service(
        authorization_token="authorization", refresh_token="old-refresh"
    )


@pytest.mark.parametrize("method_name", ["request_tokens", "refresh_tokens"])
def test_token_expiries_follow_the_documented_lifetimes(service, method_name):
    before = datetime.now(UTC)
    getattr(service, method_name)()
    after = datetime.now(UTC)

    assert before + timedelta(seconds=3599) <= service.access_token_expires_on
    assert service.access_token_expires_on <= after + timedelta(seconds=3599)

    # A refresh token expires 30 days after it is issued, not a year.
    assert before + timedelta(days=30) <= service.refresh_token_expires_on
    assert service.refresh_token_expires_on <= after + timedelta(days=30)


def test_refresh_replaces_the_stored_refresh_token(service):
    service.refresh_tokens()

    assert service.access_token == "new-access"
    assert service.refresh_token == "new-refresh"


def test_documented_refresh_token_lifetime_is_thirty_days():
    assert ClientContext.REFRESH_TOKEN_LIFETIME == timedelta(days=30)
