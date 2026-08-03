import json
from pathlib import Path

import pytest

from pyecobee import (
    EcobeeAuthorizeResponse,
    EcobeeCreateRuntimeReportJobResponse,
    EcobeeDeserializationException,
    EcobeeListDemandResponsesResponse,
    EcobeeListHierarchySetsResponse,
    EcobeeListHierarchyUsersResponse,
    EcobeeListRuntimeReportJobStatusResponse,
    EcobeeStatusResponse,
    EcobeeThermostatResponse,
    Utilities,
)


class Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.request = type("Request", (), {"url": "https://example.test"})()

    def json(self):
        return self._payload


def response_from_fixture(name):
    path = Path(__file__).parent / "fixtures" / name
    return Response(200, json.loads(path.read_text()))


@pytest.mark.parametrize(
    "fixture_name,response_class,attribute",
    [
        ("add_hierarchy_set_response.json", EcobeeStatusResponse, "status"),
        (
            "create_runtime_report_job_response.json",
            EcobeeCreateRuntimeReportJobResponse,
            "job_id",
        ),
        (
            "list_demand_responses_response.json",
            EcobeeListDemandResponsesResponse,
            "demand_response_list",
        ),
        ("list_hierarchy_sets_response.json", EcobeeListHierarchySetsResponse, "sets"),
        (
            "list_hierarchy_users_response.json",
            EcobeeListHierarchyUsersResponse,
            "users",
        ),
        (
            "list_runtime_report_job_response.json",
            EcobeeListRuntimeReportJobStatusResponse,
            "jobs",
        ),
    ],
)
def test_captured_response_fixtures_deserialize(
    fixture_name, response_class, attribute
):
    response = Utilities.process_http_response(
        response_from_fixture(fixture_name), response_class
    )

    assert getattr(response, attribute) is not None
    assert response.status.code == 0


def test_authorization_and_thermostat_responses_deserialize():
    authorization = Utilities.process_http_response(
        Response(
            200,
            {
                "ecobeePin": "ABCD",
                "code": "token",
                "scope": "smartWrite",
                "expires_in": 9,
                "interval": 30,
            },
        ),
        EcobeeAuthorizeResponse,
    )
    thermostat = Utilities.process_http_response(
        Response(
            200,
            {
                "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 0},
                "thermostatList": [],
                "status": {"code": 0, "message": ""},
            },
        ),
        EcobeeThermostatResponse,
    )

    assert authorization.ecobee_pin == "ABCD"
    assert thermostat.page.total_pages == 1
    assert thermostat.thermostat_list == []


def test_unsupported_nested_object_is_ignored():
    response = Utilities.process_http_response(
        Response(
            200, {"status": {"code": 0, "message": "", "futureObject": {"value": 1}}}
        ),
        EcobeeStatusResponse,
    )

    assert response.status.code == 0


def test_malformed_success_shape_raises():
    with pytest.raises(EcobeeDeserializationException, match="EcobeeStatusResponse"):
        Utilities.process_http_response(Response(200, []), EcobeeStatusResponse)


def test_unknown_fields_and_unsupported_objects_do_not_block_siblings(caplog):
    response = Utilities.process_http_response(
        Response(
            200,
            {
                "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 1},
                "thermostatList": [{"identifier": "abc", "oemCfg": {"new": True}}],
                "status": {"code": 0, "message": ""},
                "futureField": "ignored",
            },
        ),
        EcobeeThermostatResponse,
    )

    assert response.status.code == 0
    assert response.thermostat_list[0].identifier == "abc"
    assert any("Ignoring" in message for message in caplog.messages)


def test_empty_lists_and_malformed_known_fields_are_handled():
    response = Utilities.process_http_response(
        Response(
            200,
            {
                "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 0},
                "thermostatList": [],
                "status": {"code": 0, "message": ""},
            },
        ),
        EcobeeThermostatResponse,
    )

    assert response.thermostat_list == []
    with pytest.raises(EcobeeDeserializationException, match="status.code"):
        Utilities.process_http_response(
            Response(200, {"status": {"code": "not-a-number", "message": ""}}),
            EcobeeStatusResponse,
        )
