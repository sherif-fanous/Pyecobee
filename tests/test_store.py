"""Credentials must survive storage, stay private, and survive an interrupted save."""

import json
import stat
from datetime import UTC, datetime

import pytest

from pyecobee import JsonFileTokenStore, Scope, Tokens

STORED = Tokens(
    access_token="access",
    refresh_token="refresh",
    access_token_expires_on=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
    refresh_token_expires_on=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
    scope=Scope.EMS,
)


@pytest.fixture
def store(tmp_path):
    return JsonFileTokenStore(tmp_path / "nested" / "tokens.json")


def test_loading_an_absent_file_yields_empty_credentials(store):
    assert store.load() == Tokens()


def test_credentials_round_trip_through_the_file(store):
    store.save(STORED)

    assert store.load() == STORED


def test_the_file_is_readable_only_by_its_owner(store, tmp_path):
    store.save(STORED)

    mode = (tmp_path / "nested" / "tokens.json").stat().st_mode

    assert stat.S_IMODE(mode) == 0o600


def test_an_interrupted_save_leaves_the_previous_credentials_intact(store, tmp_path):
    store.save(STORED)

    path = tmp_path / "nested" / "tokens.json"
    before = path.read_text()

    def fail(_self, _data):
        raise OSError("no space left on device")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("pathlib.Path.write_text", fail)

        with pytest.raises(OSError, match="no space left on device"):
            store.save(STORED.replace(access_token="later"))

    assert path.read_text() == before
    assert store.load() == STORED


def test_stored_credentials_are_json_a_person_can_read(store, tmp_path):
    store.save(STORED)

    data = json.loads((tmp_path / "nested" / "tokens.json").read_text())

    assert data["access_token"] == "access"
    assert data["access_token_expires_on"] == "2026-08-05T12:00:00+00:00"
    assert data["scope"] == "ems"
