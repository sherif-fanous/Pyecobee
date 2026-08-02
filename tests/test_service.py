import datetime
import json
from datetime import datetime as DateTime
from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest

from pyecobee import EcobeeService, Selection, SelectionType, Utilities


class Response:
    status_code = 200
    request = type("Request", (), {"url": "https://example.test"})()

    def json(self):
        return {"reportList": [], "status": {"code": 0, "message": ""}}


def service():
    return EcobeeService("test", "a" * 32)


def selection():
    return Selection(
        selection_type=SelectionType.THERMOSTATS.value, selection_match="123"
    )


def test_service_constructor_and_argument_validation():
    with pytest.raises(TypeError):
        EcobeeService("test", 1)
    with pytest.raises(ValueError):
        EcobeeService("test", "short")
    with pytest.raises(TypeError):
        service().request_thermostats_summary("not a selection")
    with pytest.raises(ValueError):
        service().authorize(response_type="code")


def test_meter_report_validates_dates_before_request():
    start = DateTime(2020, 1, 2, tzinfo=datetime.UTC)

    with pytest.raises(ValueError, match="later than start_date_time"):
        service().request_meter_reports(selection(), start, start)
    with pytest.raises(ValueError, match="more than 31 days"):
        service().request_meter_reports(selection(), start, start + timedelta(days=32))


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("request_meter_reports", {}),
        ("request_runtime_reports", {"columns": "auxHeat1"}),
    ],
)
def test_report_requests_reject_naive_datetimes(method, kwargs):
    start = DateTime(2020, 1, 2)
    end = DateTime(2020, 1, 3)

    with pytest.raises(ValueError, match="start_date_time must be timezone-aware"):
        getattr(service(), method)(selection(), start, end, **kwargs)
    with pytest.raises(ValueError, match="end_date_time must be timezone-aware"):
        getattr(service(), method)(
            selection(), start.replace(tzinfo=datetime.UTC), end, **kwargs
        )


def test_meter_report_converts_aware_dates_to_utc(monkeypatch):
    captured = {}

    def request(*args, **kwargs):
        captured.update(kwargs)
        return Response()

    monkeypatch.setattr(Utilities, "make_http_request", request)
    eastern = ZoneInfo("America/New_York")
    start = DateTime(2020, 1, 2, 0, 0, tzinfo=eastern)
    end = DateTime(2020, 1, 2, 1, 0, tzinfo=eastern)

    response = service().request_meter_reports(selection(), start, end)
    body = json.loads(captured["params"]["body"])

    assert response.status.code == 0
    assert body["startDate"] == "2020-01-02"
    assert body["startInterval"] == 60
    assert body["endInterval"] == 72
