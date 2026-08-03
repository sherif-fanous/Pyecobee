import json
from pathlib import Path

import pytest
import requests


class MockResponse:
    def __init__(self, status_code=200, payload=None, url="https://example.test"):
        self.status_code = status_code
        self._payload = payload
        self.request = type("Request", (), {"url": url})()

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture
def fixture_payload():
    def load(name):
        return json.loads((Path(__file__).parent / "fixtures" / name).read_text())

    return load


@pytest.fixture
def mock_response():
    return MockResponse


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("network access is not allowed in offline tests")

    monkeypatch.setattr(requests.sessions.Session, "request", fail)
