import pytest

from pyecobee import (
    EcobeeAuthorizeResponse,
    EcobeeListDemandResponsesResponse,
    EcobeeListHierarchySetsResponse,
    EcobeeListHierarchyUsersResponse,
    EcobeeListRuntimeReportJobStatusResponse,
    EcobeeMeterReportsResponse,
    EcobeeRuntimeReportsResponse,
    EcobeeStatusResponse,
    EcobeeThermostatResponse,
    EcobeeTokensResponse,
    Utilities,
)
from pyecobee.enumerations import FanMode, Scope


def process(payload, response_class, mock_response):
    return Utilities.process_http_response(
        mock_response(payload=payload), response_class
    )


@pytest.mark.parametrize(
    ("response_class", "payload", "attribute", "expected"),
    [
        (
            EcobeeAuthorizeResponse,
            {
                "ecobeePin": "ABCD",
                "code": "authorization-code",
                "scope": Scope.SMART_WRITE.value,
                "expires_in": 9,
                "interval": 30,
            },
            "ecobee_pin",
            "ABCD",
        ),
        (
            EcobeeTokensResponse,
            {
                "access_token": "access",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "refresh",
                "scope": Scope.SMART_READ.value,
            },
            "refresh_token",
            "refresh",
        ),
        (
            EcobeeThermostatResponse,
            {
                "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 0},
                "thermostatList": [],
                "status": {"code": 0, "message": ""},
            },
            "thermostat_list",
            [],
        ),
    ],
)
def test_common_success_responses_deserialize(
    response_class, payload, attribute, expected, mock_response
):
    assert (
        getattr(process(payload, response_class, mock_response), attribute) == expected
    )


def test_fixture_response_families_preserve_nested_values(
    fixture_payload, mock_response
):
    demand_responses = process(
        fixture_payload("list_demand_responses_response.json"),
        EcobeeListDemandResponsesResponse,
        mock_response,
    )
    hierarchy_sets = process(
        fixture_payload("list_hierarchy_sets_response.json"),
        EcobeeListHierarchySetsResponse,
        mock_response,
    )
    runtime_jobs = process(
        fixture_payload("list_runtime_report_job_response.json"),
        EcobeeListRuntimeReportJobStatusResponse,
        mock_response,
    )

    assert demand_responses.demand_response_list[0].event.fan == FanMode.AUTO.value
    assert demand_responses.demand_response_list[0].thermostats == [
        "123456789012",
        "123456789013",
        "123456789014",
    ]
    assert (
        hierarchy_sets.sets[0].children[0].children[0].set_path == "/MainNode/SubNode1"
    )
    assert runtime_jobs.jobs[2].files == [
        "https://s3.amazonaws.com/ecobee-utl/example_dir/examplefile-1.tar.gz.gpg"
    ]


def test_runtime_and_meter_report_primitive_lists_deserialize(mock_response):
    meter_response = process(
        {"reportList": [], "status": {"code": 0, "message": ""}},
        EcobeeMeterReportsResponse,
        mock_response,
    )
    runtime_response = process(
        {
            "startDate": "2020-01-02",
            "startInterval": 0,
            "endDate": "2020-01-02",
            "endInterval": 12,
            "columns": "auxHeat1",
            "reportList": [
                {
                    "thermostatIdentifier": "123",
                    "rowCount": 1,
                    "rowList": ["2020-01-02,0"],
                }
            ],
            "sensorList": [],
            "status": {"code": 0, "message": ""},
        },
        EcobeeRuntimeReportsResponse,
        mock_response,
    )

    assert meter_response.report_list == []
    assert runtime_response.report_list[0].row_list == ["2020-01-02,0"]
    assert runtime_response.sensor_list == []


def test_optional_response_fields_default_to_none(mock_response):
    response = process(
        {"users": [], "status": {"code": 0, "message": ""}},
        EcobeeListHierarchyUsersResponse,
        mock_response,
    )

    assert response.privileges is None


def test_unknown_fields_and_nested_objects_are_ignored(mock_response):
    response = process(
        {
            "status": {
                "code": 0,
                "message": "",
                "futureObject": {"value": 1},
                "futureValue": "ignored",
            },
            "futureTopLevel": {"value": 2},
        },
        EcobeeStatusResponse,
        mock_response,
    )

    assert response.status.code == 0
