import pytest
from pydantic import ValidationError

from pyecobee import (
    EcobeeCreateRuntimeReportJobResponse,
    EcobeeThermostatResponse,
    Selection,
    SelectionType,
)
from pyecobee.deserialization import deserialize
from pyecobee.models import Event, Status


def test_request_models_use_aliases_nested_values_and_enum_serialization():
    selection = Selection(
        selection_type=SelectionType.THERMOSTATS,
        selection_match="123",
        include_runtime=True,
    )

    assert selection.selection_type is SelectionType.THERMOSTATS
    assert selection.to_api_dict() == {
        "selectionType": "thermostats",
        "selectionMatch": "123",
        "includeRuntime": True,
    }

    event = Event(type="hold", fan="auto")

    assert event.type == "hold"
    assert event.fan == "auto"
    assert event.to_api_dict() == {"type": "hold", "fan": "auto"}


def test_request_models_reject_unknown_or_invalid_fields():
    with pytest.raises(ValidationError, match="selection_type"):
        Selection.model_validate(
            {"selection_type": "not-a-selection", "selection_match": "123"}
        )

    with pytest.raises(ValidationError, match="unsupported"):
        Selection.model_validate(
            {
                "selection_type": SelectionType.THERMOSTATS,
                "selection_match": "123",
                "unsupported": True,
            }
        )

    with pytest.raises(ValidationError, match="unsupported"):
        Event(type="hold", unsupported=True)


def test_response_models_reject_values_that_do_not_match_declared_types():
    with pytest.raises(ValidationError, match="job_id"):
        EcobeeCreateRuntimeReportJobResponse.model_validate(
            {
                "job_id": 123,
                "job_status": "queued",
                "status": Status(code=0, message="ok"),
            }
        )


def test_response_models_reject_unknown_fields_when_validated_directly():
    with pytest.raises(ValidationError, match="futureField"):
        EcobeeThermostatResponse.model_validate(
            {
                "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 1},
                "thermostatList": [{"identifier": "abc", "futureField": True}],
                "status": {"code": 0, "message": "ok"},
            }
        )


def test_deserialization_ignores_new_fields_in_optional_nested_lists():
    response = deserialize(
        {
            "page": {"page": 1, "totalPages": 1, "pageSize": 1, "total": 1},
            "thermostatList": [
                {
                    "identifier": "abc",
                    "devices": [{"deviceId": 1, "futureDeviceField": True}],
                    "futureThermostatField": True,
                }
            ],
            "status": {"code": 0, "message": "ok", "futureStatus": True},
            "futureResponse": True,
        },
        EcobeeThermostatResponse,
    )

    assert response.thermostat_list[0].devices[0].device_id == 1
    assert response.status.message == "ok"
