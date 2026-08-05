"""Twilio auth-selection and send tests for SCLogger.send_sms() / sms_configured() (no real network)."""
from __future__ import annotations

import pytest

from sc_foundation import sc_logging
from sc_foundation.sc_logging import SCLogger

TWILIO_VARS = [
    "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
    "TWILIO_API_KEY_SID", "TWILIO_API_KEY_SECRET", "TWILIO_FROM_NUMBER",
    "TWILIO_SEND_SMS_TO",
]


class FakeMessages:
    def __init__(self, sink):
        self._sink = sink

    def create(self, to, from_, body):
        self._sink.append({"to": to, "from_": from_, "body": body})


class FakeClient:
    """Captures constructor args and message sends."""

    instances = []

    def __init__(self, *args):
        self.args = args
        self.sent = []
        self.messages = FakeMessages(self.sent)
        FakeClient.instances.append(self)


@pytest.fixture
def logger():
    return SCLogger({"logfile_name": None})


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in TWILIO_VARS:
        monkeypatch.delenv(var, raising=False)
    FakeClient.instances = []
    monkeypatch.setattr(sc_logging, "Client", FakeClient)


def test_api_key_auth_passes_account_sid(monkeypatch, logger):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_API_KEY_SID", "SK456")
    monkeypatch.setenv("TWILIO_API_KEY_SECRET", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "SpelloWater")

    assert logger.send_sms("hi", ["+393311194199"]) is True
    client = FakeClient.instances[-1]
    # API key sid + secret + account sid (AC...) in the URL path
    assert client.args == ("SK456", "secret", "AC123")
    assert client.sent[0]["from_"] == "SpelloWater"


def test_account_token_auth(monkeypatch, logger):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "tok")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+15005550006")

    assert logger.send_sms("hi", ["+393311194199"]) is True
    assert FakeClient.instances[-1].args == ("AC123", "tok")


def test_api_key_without_account_sid_is_rejected(monkeypatch, logger):
    monkeypatch.setenv("TWILIO_API_KEY_SID", "SK456")
    monkeypatch.setenv("TWILIO_API_KEY_SECRET", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "SpelloWater")

    assert logger.send_sms("hi", ["+39331"]) is False
    assert FakeClient.instances == []  # never constructed a client


def test_api_key_in_account_sid_slot_is_caught(monkeypatch, logger):
    # The exact original misconfiguration: SK... in TWILIO_ACCOUNT_SID + token.
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "SK0de4df")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "SpelloWater")

    assert logger.send_sms("hi", ["+39331"]) is False
    assert FakeClient.instances == []


def test_missing_from_number(monkeypatch, logger):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "tok")
    assert logger.send_sms("hi", ["+39331"]) is False


def test_no_credentials(monkeypatch, logger):
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "SpelloWater")
    assert logger.send_sms("hi", ["+39331"]) is False
    assert FakeClient.instances == []


def test_sms_configured(monkeypatch, logger):
    assert logger.sms_configured() is False
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "tok")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "SpelloWater")
    assert logger.sms_configured() is True
