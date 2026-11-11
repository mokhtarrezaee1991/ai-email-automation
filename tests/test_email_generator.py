
from unittest.mock import MagicMock

import httpx
import pytest

from openai import (
    APITimeoutError,
    APIConnectionError,
    APIStatusError
)

from app.email_generator import generate_email_reply


def create_mock_client(monkeypatch, side_effect=None, output_text=None):
    """Ersetzt den echten OpenAI-Aufruf durch eine Simulation."""

    fake_create = MagicMock()

    if side_effect is not None:
        fake_create.side_effect = side_effect
    else:
        fake_create.return_value.output_text = output_text

    monkeypatch.setattr(
        "app.email_generator.client.responses.create",
        fake_create
    )

    return fake_create


def generate_test_reply():
    """Ruft die Antwortgenerierung mit Testdaten auf."""

    return generate_email_reply(
        email_text="Guten Tag, meine Bestellung ist nicht angekommen.",
        category="Versand",
        summary="Kunde fragt nach seiner Bestellung.",
        customer_name="Max Müller"
    )


def test_generate_email_reply_timeout(monkeypatch):
    """Testet einen OpenAI-Timeout."""

    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    error = APITimeoutError(request=request)

    fake_create = create_mock_client(
        monkeypatch,
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match="nicht rechtzeitig geantwortet"
    ):
        generate_test_reply()

    fake_create.assert_called_once()


def test_generate_email_reply_connection_error(monkeypatch):
    """Testet einen Verbindungsfehler."""

    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    error = APIConnectionError(request=request)

    create_mock_client(
        monkeypatch,
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match="Verbindung zur OpenAI API"
    ):
        generate_test_reply()


@pytest.mark.parametrize("status_code", [429, 500])
def test_generate_email_reply_api_error(monkeypatch, status_code):
    """Testet HTTP 429 und HTTP 500."""

    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    response = httpx.Response(
        status_code=status_code,
        request=request
    )

    error = APIStatusError(
        message="Simulierter API-Fehler",
        response=response,
        body=None
    )

    create_mock_client(
        monkeypatch,
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match=f"HTTP {status_code}"
    ):
        generate_test_reply()


@pytest.mark.parametrize("output_text", ["", "   ", None])
def test_generate_email_reply_empty_response(monkeypatch, output_text):
    """Testet leere oder ungültige Antworttexte."""

    create_mock_client(
        monkeypatch,
        output_text=output_text
    )

    with pytest.raises(
        ValueError,
        match="keinen gültigen Antworttext"
    ):
        generate_test_reply()


def test_generate_email_reply_success(monkeypatch):
    """Testet eine erfolgreiche Antwortgenerierung."""

    expected_reply = "Sehr geehrter Herr Müller, vielen Dank."

    create_mock_client(
        monkeypatch,
        output_text=f"  {expected_reply}  "
    )

    result = generate_test_reply()

    assert result == expected_reply
