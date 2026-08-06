"""Every thermostat function call must build a valid ecobee function payload."""

import json
import re
from datetime import UTC
from datetime import datetime as DateTime
from pathlib import Path

import pytest

from pyecobee import (
    AckType,
    FanMode,
    HoldType,
    PlugState,
    Selection,
    SelectionType,
)
from pyecobee.transport import HttpTransport
from tests.support import build_service

UPDATE_RESPONSE = {"status": {"code": 0, "message": ""}}
START = DateTime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
END = DateTime(2024, 1, 3, 6, 7, 8, tzinfo=UTC)


def service():
    return build_service(authorization_token="authorization", access_token="access")


def selection():
    return Selection(selection_type=SelectionType.THERMOSTATS, selection_match="123")


@pytest.fixture
def sent_functions(monkeypatch, mock_response):
    captured = []

    def request(_transport, method, url, **kwargs):
        captured.append(kwargs["json_"])
        return mock_response(payload=UPDATE_RESPONSE)

    monkeypatch.setattr(HttpTransport, "request", request)

    def call(method_name, *args, **kwargs):
        del captured[:]
        getattr(service(), method_name)(*args, selection=selection(), **kwargs)
        assert len(captured) == 1
        payload = captured[0]
        # The payload is passed to requests as json_, so it must be serializable.
        json.dumps(payload)
        return payload["functions"]

    return call


FUNCTION_CALLS = [
    (
        "acknowledge",
        ("thermostat-1", "ack-1", AckType.ACCEPT),
        {"remind_me_later": True},
        {
            "type": "acknowledge",
            "params": {
                "thermostatIdentifier": "thermostat-1",
                "ackRef": "ack-1",
                "ackType": "accept",
                "remindMeLater": True,
            },
        },
    ),
    (
        "control_plug",
        ("plug-1", PlugState.ON),
        {
            "start_date_time": START,
            "end_date_time": END,
            "hold_type": HoldType.HOLD_HOURS,
            "hold_hours": 2,
        },
        {
            "type": "controlPlug",
            "params": {
                "plugName": "plug-1",
                "plugState": "on",
                "holdType": "holdHours",
                "startDate": "2024-01-02",
                "startTime": "03:04:05",
                "endDate": "2024-01-03",
                "endTime": "06:07:08",
                "holdHours": 2,
            },
        },
    ),
    (
        "create_vacation",
        ("vacation-1", 78.5, 62.5),
        {
            "start_date_time": START,
            "end_date_time": END,
            "fan_mode": FanMode.ON,
            "fan_min_on_time": 15,
        },
        {
            "type": "createVacation",
            "params": {
                "name": "vacation-1",
                "coolHoldTemp": 785,
                "heatHoldTemp": 625,
                "fan": "on",
                "fanMinOnTime": "15",
                "startDate": "2024-01-02",
                "startTime": "03:04:05",
                "endDate": "2024-01-03",
                "endTime": "06:07:08",
            },
        },
    ),
    (
        "delete_vacation",
        ("vacation-1",),
        {},
        {"type": "deleteVacation", "params": {"name": "vacation-1"}},
    ),
    ("reset_preferences", (), {}, {"type": "resetPreferences"}),
    (
        "resume_program",
        (),
        {"resume_all": True},
        {"type": "resumeProgram", "params": {"resumeAll": True}},
    ),
    (
        "send_message",
        ("hello",),
        {},
        {"type": "sendMessage", "params": {"text": "hello"}},
    ),
    (
        "set_hold",
        (),
        {
            "cool_hold_temp": 78.5,
            "heat_hold_temp": 62.5,
            "fan_mode": FanMode.ON,
            "hold_climate_ref": "home",
            "start_date_time": START,
            "end_date_time": END,
            "hold_type": HoldType.HOLD_HOURS,
            "hold_hours": 3,
        },
        {
            "type": "setHold",
            "params": {
                "holdType": "holdHours",
                "coolHoldTemp": 785,
                "heatHoldTemp": 625,
                "fan": "on",
                "holdClimateRef": "home",
                "startDate": "2024-01-02",
                "startTime": "03:04:05",
                "endDate": "2024-01-03",
                "endTime": "06:07:08",
                "holdHours": 3,
            },
        },
    ),
    (
        "set_occupied",
        (True,),
        {
            "start_date_time": START,
            "end_date_time": END,
            "hold_type": HoldType.HOLD_HOURS,
            "hold_hours": 4,
        },
        {
            "type": "setOccupied",
            "params": {
                "occupied": True,
                "holdType": "holdHours",
                "startDate": "2024-01-02",
                "startTime": "03:04:05",
                "endDate": "2024-01-03",
                "endTime": "06:07:08",
                "holdHours": 4,
            },
        },
    ),
    (
        "unlink_voice_engine",
        ("alexa",),
        {},
        {"type": "unlinkVoiceEngine", "params": {"engineName": "alexa"}},
    ),
    (
        "update_sensor",
        ("sensor name", "device-1", "sensor-1"),
        {},
        {
            "type": "updateSensor",
            "params": {
                "name": "sensor name",
                "deviceId": "device-1",
                "sensorId": "sensor-1",
            },
        },
    ),
]


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "expected_function"),
    FUNCTION_CALLS,
    ids=[call[0] for call in FUNCTION_CALLS],
)
def test_thermostat_function_payload(
    sent_functions, method_name, args, kwargs, expected_function
):
    assert sent_functions(method_name, *args, **kwargs) == [expected_function]


def test_every_thermostat_function_method_is_covered():
    source = Path("pyecobee/services/thermostats.py").read_text()

    assert set(re.findall(r'Function\(\s*type="(\w+)"', source)) == {
        call[3]["type"] for call in FUNCTION_CALLS
    }
