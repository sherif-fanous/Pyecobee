"""Credentials must round-trip as plain data and be announced when they change."""

from datetime import UTC, datetime, timedelta

import pytest

from pyecobee import EcobeeService, Scope, Tokens
from pyecobee.transport import HttpTransport
from tests.support import APPLICATION_KEY, build_service, discard_tokens

TOKENS_PAYLOAD = {
    "access_token": "new-access",
    "token_type": "Bearer",
    "expires_in": 3599,
    "refresh_token": "new-refresh",
    "scope": "smartWrite",
}
AUTHORIZE_PAYLOAD = {
    "ecobeePin": "ABCD",
    "code": "authorization-code",
    "scope": "smartWrite",
    "expires_in": 9,
    "interval": 30,
}


@pytest.fixture
def respond(monkeypatch, mock_response):
    def with_payload(payload):
        def request(_transport, method, url, **kwargs):
            return mock_response(payload=payload)

        monkeypatch.setattr(HttpTransport, "request", request)

    return with_payload


def test_tokens_round_trip_through_a_json_compatible_mapping():
    tokens = Tokens(
        authorization_token="authorization",
        access_token="access",
        refresh_token="refresh",
        access_token_expires_on=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        refresh_token_expires_on=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
        scope=Scope.EMS,
    )

    data = tokens.to_dict()

    assert data == {
        "authorization_token": "authorization",
        "access_token": "access",
        "refresh_token": "refresh",
        "access_token_expires_on": "2026-08-05T12:00:00+00:00",
        "refresh_token_expires_on": "2026-09-04T12:00:00+00:00",
        "scope": "ems",
    }
    assert Tokens.from_dict(data) == tokens


def test_tokens_default_to_utc_and_ignore_unknown_stored_fields():
    tokens = Tokens.from_dict(
        {
            "access_token": "access",
            "access_token_expires_on": "2026-08-05T12:00:00",
            "from_a_later_release": True,
        }
    )

    assert tokens.access_token_expires_on == datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
    assert tokens.refresh_token is None
    assert tokens.scope is Scope.SMART_WRITE


def test_tokens_representation_withholds_the_credentials():
    representation = repr(Tokens(access_token="s3cret", refresh_token="al5oSecret"))

    assert "s3cret" not in representation
    assert "al5oSecret" not in representation
    assert "held=access_token, refresh_token" in representation


def test_service_restores_and_exposes_stored_credentials():
    stored = Tokens(
        access_token="access",
        refresh_token="refresh",
        access_token_expires_on=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        scope=Scope.SMART_READ,
    )

    service = EcobeeService("test", APPLICATION_KEY, stored, discard_tokens)

    assert service.access_token == "access"
    assert service.refresh_token == "refresh"
    assert service.scope is Scope.SMART_READ
    assert service.tokens == stored


def test_service_accepts_a_stored_mapping():
    service = EcobeeService(
        "test",
        APPLICATION_KEY,
        {"access_token": "access", "scope": "ems"},
        discard_tokens,
    )

    assert service.tokens.access_token == "access"
    assert service.scope is Scope.EMS


def test_service_rejects_credentials_that_are_not_tokens():
    with pytest.raises(TypeError, match="tokens must be an instance of"):
        EcobeeService("test", APPLICATION_KEY, "access", discard_tokens)


def test_service_requires_somewhere_to_store_new_credentials():
    with pytest.raises(TypeError, match="on_tokens_changed must be callable"):
        EcobeeService("test", APPLICATION_KEY, Tokens(), None)


@pytest.mark.parametrize(
    ("method_name", "payload"),
    [
        ("authorize", AUTHORIZE_PAYLOAD),
        ("request_tokens", TOKENS_PAYLOAD),
        ("refresh_tokens", TOKENS_PAYLOAD),
    ],
)
def test_new_credentials_are_announced_to_the_callback(respond, method_name, payload):
    respond(payload)

    announced = []
    service = build_service(
        announced.append,
        authorization_token="authorization",
        refresh_token="old-refresh",
    )

    getattr(service, method_name)()

    assert len(announced) == 1
    assert announced[-1] == service.tokens


def test_announced_credentials_are_ready_to_store(respond):
    respond(TOKENS_PAYLOAD)

    announced = []
    service = build_service(announced.append, refresh_token="old-refresh")

    before = datetime.now(UTC)

    service.refresh_tokens()

    tokens = announced[-1]

    assert tokens.access_token == "new-access"
    assert tokens.refresh_token == "new-refresh"
    assert tokens.access_token_expires_on >= before
    assert tokens.refresh_token_expires_on >= before + timedelta(days=29)
    assert Tokens.from_dict(tokens.to_dict()) == tokens


def test_a_failing_callback_is_not_suppressed(respond):
    respond(TOKENS_PAYLOAD)

    def fail(_tokens):
        raise OSError("read-only file system")

    service = build_service(fail, refresh_token="old-refresh")

    with pytest.raises(OSError, match="read-only file system"):
        service.refresh_tokens()
