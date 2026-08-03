import json

import requests

from pyecobee import EcobeeService, Selection, SelectionType, Utilities


def service():
    return EcobeeService(
        "test", "a" * 32, authorization_token="authorization", access_token="access"
    )


def selection():
    return Selection(
        selection_type=SelectionType.THERMOSTATS.value, selection_match="123"
    )


def capture_request(monkeypatch, mock_response, payload):
    captured = {}

    def request(method, url, **kwargs):
        captured.update(method=method, url=url, **kwargs)
        return mock_response(payload=payload)

    monkeypatch.setattr(Utilities, "make_http_request", request)
    return captured


def test_authorize_request_uses_expected_method_url_parameters_and_timeout(
    monkeypatch, mock_response
):
    captured = capture_request(
        monkeypatch,
        mock_response,
        {
            "ecobeePin": "ABCD",
            "code": "authorization-code",
            "scope": "smartWrite",
            "expires_in": 9,
            "interval": 30,
        },
    )

    response = service().authorize(timeout=17)

    assert response.code == "authorization-code"
    assert captured == {
        "method": requests.get,
        "url": EcobeeService.AUTHORIZE_URL,
        "params": {
            "client_id": "a" * 32,
            "response_type": "ecobeePin",
            "scope": "smartWrite",
        },
        "timeout": 17,
    }


def test_token_request_uses_post_and_updates_service_tokens(monkeypatch, mock_response):
    ecobee_service = service()
    captured = capture_request(
        monkeypatch,
        mock_response,
        {
            "access_token": "new-access",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "new-refresh",
            "scope": "smartWrite",
        },
    )

    response = ecobee_service.request_tokens(timeout=11)

    assert response.access_token == "new-access"
    assert ecobee_service.access_token == "new-access"
    assert captured["method"].__name__ == "post"
    assert captured["url"] == EcobeeService.TOKENS_URL
    assert captured["params"] == {
        "client_id": "a" * 32,
        "code": "authorization",
        "grant_type": "ecobeePin",
    }
    assert captured["timeout"] == 11


def test_thermostat_request_sends_headers_selection_payload_and_timeout(
    monkeypatch, mock_response
):
    captured = capture_request(
        monkeypatch,
        mock_response,
        {
            "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 0},
            "thermostatList": [],
            "status": {"code": 0, "message": ""},
        },
    )

    service().request_thermostats(selection(), timeout=13)

    assert captured["method"].__name__ == "get"
    assert captured["url"] == EcobeeService.THERMOSTAT_URL
    assert captured["headers"] == {
        "Authorization": "Bearer access",
        "Content-Type": "application/json;charset=UTF-8",
    }
    assert json.loads(captured["params"]["json"]) == {
        "selection": {"selectionType": "thermostats", "selectionMatch": "123"}
    }
    assert captured["timeout"] == 13
