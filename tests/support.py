"""Helpers shared by the offline tests."""

from pyecobee import EcobeeService, Tokens

APPLICATION_KEY = "a" * 32
THERMOSTAT_NAME = "test"


def discard_tokens(_tokens):
    """Ignore new credentials, as a caller with nothing to store would."""


def build_service(on_tokens_changed=discard_tokens, **token_fields):
    """Return a service holding *token_fields* as its credentials."""
    return EcobeeService(
        THERMOSTAT_NAME,
        APPLICATION_KEY,
        Tokens(**token_fields),
        on_tokens_changed,
    )
