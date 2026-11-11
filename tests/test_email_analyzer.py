from unittest.mock import MagicMock

import httpx
import pytest
from openai import APITimeoutError
from openai import APIConnectionError
from openai import APIStatusError

from app.email_analyzer import analyze_email


def test_analyze_email_timeout(monkeypatch):
    """Prüft die Fehlerbehandlung bei einem OpenAI-Timeout."""

    # 1. Eine simulierte HTTP-Anfrage erstellen
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    # 2. Einen Timeout-Fehler simulieren
    timeout_error = APITimeoutError(request=request)

    # 3. OpenAI-Client durch einen Mock ersetzen
    fake_client = MagicMock()

    fake_client.responses.parse.side_effect = timeout_error

    monkeypatch.setattr(
        "app.email_analyzer.OpenAI",
        lambda **kwargs: fake_client
    )

    # 4. Prüfen, ob unsere Funktion den Fehler behandelt
    with pytest.raises(
        RuntimeError,
        match="OpenAI hat nicht rechtzeitig geantwortet"
    ):
        analyze_email(
            "Guten Tag, meine Bestellung ist nicht angekommen."
        )

def test_analyze_email_connection_error(monkeypatch):
    """Prüft die Fehlerbehandlung bei Verbindungsproblemen."""

    # 1. Simulierte HTTP-Anfrage erstellen
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    # 2. Verbindungsfehler simulieren
    connection_error = APIConnectionError(
        request=request
    )

    # 3. OpenAI-Client durch einen Mock ersetzen
    fake_client = MagicMock()

    fake_client.responses.parse.side_effect = connection_error

    monkeypatch.setattr(
        "app.email_analyzer.OpenAI",
        lambda **kwargs: fake_client
    )

    # 4. Fehlerbehandlung überprüfen
    with pytest.raises(
        RuntimeError,
        match="Verbindung zur OpenAI API fehlgeschlagen"
    ):
        analyze_email(
            "Guten Tag, ich kann mich nicht anmelden."
        )        

def test_analyze_email_rate_limit(monkeypatch):
    """Prüft die Fehlerbehandlung bei HTTP 429."""

    # 1. Simulierte HTTP-Anfrage
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses"
    )

    # 2. Simulierte HTTP-Antwort
    response = httpx.Response(
        status_code=429,
        request=request
    )

    # 3. API-Fehler erstellen
    api_error = APIStatusError(
        message="Too Many Requests",
        response=response,
        body=None
    )

    # 4. OpenAI-Client simulieren
    fake_client = MagicMock()
    fake_client.responses.parse.side_effect = api_error

    monkeypatch.setattr(
        "app.email_analyzer.OpenAI",
        lambda **kwargs: fake_client
    )

    # 5. Fehlerbehandlung überprüfen
    with pytest.raises(
        RuntimeError,
        match="OpenAI API-Fehler: HTTP 429"
    ):
        analyze_email(
            "Guten Tag, wo bleibt meine Bestellung?"
        )        