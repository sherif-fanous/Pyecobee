import pytest
import requests


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("network access is not allowed in offline tests")

    monkeypatch.setattr(requests.sessions.Session, "request", fail)
