
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import database
from app.api import app
from app.email_analyzer import EmailAnalysis


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Temporäre Testdatenbank verwenden
    test_db = tmp_path / "test_api.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.create_database()

    return TestClient(app)


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Email Automation API is running"
    )


def test_get_emails(client):
    response = client.get("/emails")

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_email_not_found(client):
    response = client.get("/emails/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Email not found"


def test_double_approval(client):
    # Test-E-Mail erstellen
    email_id = database.save_email(
        email_text="Meine Bestellung ist nicht angekommen.",
        category="Versand",
        urgency="Hoch",
        summary="Kunde fragt nach seiner Bestellung.",
        priority="P1",
        department="Logistik"
    )

    # Test-Antwort speichern
    reply_id = database.save_reply(
        email_id=email_id,
        reply_text="Wir prüfen Ihre Anfrage."
    )

    # Erste Genehmigung
    response1 = client.patch(
        f"/replies/{reply_id}/approval",
        params={"status": "Approved"}
    )

    assert response1.status_code == 200
    assert response1.json()["approval_status"] == "Approved"

    # Zweite Genehmigung
    response2 = client.patch(
        f"/replies/{reply_id}/approval",
        params={"status": "Approved"}
    )

    assert response2.status_code == 409

def test_analyze_email_with_mock(client, monkeypatch):

    # Simuliertes KI-Ergebnis
    fake_analysis = EmailAnalysis(
        category="Technischer Support",
        urgency="Hoch",
        summary="Kunde meldet einen defekten Laptop."
    )

    # Echte OpenAI-Funktion durch Mock ersetzen
    def fake_analyze_email(email_text):
        return fake_analysis

    monkeypatch.setattr(
        "app.api.analyze_email",
        fake_analyze_email
    )

    # API-Anfrage simulieren
    response = client.post(
        "/emails/analyze",
        json={
            "email_text": "Mein Laptop startet nicht mehr."
        }
    )

    # HTTP-Antwort überprüfen
    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "Technischer Support"
    assert data["urgency"] == "Hoch"
    assert data["priority"] == "P1"
    assert data["department"] == "IT-Support"

    # Überprüfen, ob die E-Mail gespeichert wurde
    emails = database.get_emails()

    assert len(emails) == 1
    assert emails[0]["category"] == "Technischer Support"


def test_generate_reply_with_mock(client, monkeypatch):

    # 1. Test-E-Mail erstellen
    email_id = database.save_email(
        email_text="Mein Laptop startet nicht mehr.",
        category="Technischer Support",
        urgency="Hoch",
        summary="Kunde meldet einen defekten Laptop.",
        priority="P1",
        department="IT-Support"
    )

    # 2. KI-Antwort simulieren
    fake_reply = (
        "Guten Tag, vielen Dank für Ihre Nachricht. "
        "Wir prüfen Ihr Anliegen. "
        "Mit freundlichen Grüßen, Ihr Kundenservice-Team"
    )

    def fake_generate_reply(
        email_text,
        category,
        summary,
        customer_name=None
    ):
        return fake_reply

    monkeypatch.setattr(
        "app.api.generate_email_reply",
        fake_generate_reply
    )

    # 3. API-Endpunkt aufrufen
    response = client.post(
        f"/emails/{email_id}/generate-reply"
    )

    # 4. HTTP-Antwort überprüfen
    assert response.status_code == 201

    data = response.json()

    assert data["email_id"] == email_id
    assert data["reply_text"] == fake_reply
    assert data["approval_status"] == "Pending Approval"

    # 5. SQLite-Speicherung überprüfen
    replies = database.get_replies(email_id=email_id)

    assert len(replies) == 1
    assert replies[0]["reply_text"] == fake_reply
    assert replies[0]["approval_status"] == "Pending Approval"

def test_update_reply_text(client):

    # 1. Test-E-Mail erstellen
    email_id = database.save_email(
        email_text="Meine Rechnung ist falsch.",
        category="Rechnung",
        urgency="Mittel",
        summary="Kunde meldet eine falsche Rechnung.",
        priority="P2",
        department="Buchhaltung",
        customer_name="Max Müller"
    )

    # 2. Ursprünglichen Antwortentwurf speichern
    reply_id = database.save_reply(
        email_id=email_id,
        reply_text="Wir prüfen Ihre Anfrage."
    )

    # 3. Antwort über FastAPI bearbeiten
    new_text = "Sehr geehrter Herr Müller, wir prüfen Ihre Rechnung."

    response = client.patch(
        f"/replies/{reply_id}",
        json={"reply_text": new_text}
    )

    # 4. HTTP-Ergebnis überprüfen
    assert response.status_code == 200

    # 5. Gespeicherten Text in SQLite überprüfen
    replies = database.get_replies(email_id=email_id)

    assert len(replies) == 1
    assert replies[0]["reply_text"] == new_text

    # 6. Freigabestatus muss unverändert bleiben
    assert replies[0]["approval_status"] == "Pending Approval"

import pytest

@pytest.mark.parametrize("status", ["Approved", "Rejected"])
def test_cannot_edit_processed_reply(client, status):

    # 1. Test-E-Mail erstellen
    email_id = database.save_email(
        email_text="Meine Rechnung ist falsch.",
        category="Rechnung",
        urgency="Mittel",
        summary="Kunde meldet eine falsche Rechnung.",
        priority="P2",
        department="Buchhaltung",
        customer_name="Max Müller"
    )

    # 2. Antwortentwurf speichern
    original_text = "Wir prüfen Ihre Anfrage."

    reply_id = database.save_reply(
        email_id=email_id,
        reply_text=original_text
    )

    # 3. Antwort freigeben oder ablehnen
    database.update_reply_status(
        reply_id=reply_id,
        new_status=status
    )

    # 4. Versuchen, die Antwort nachträglich zu ändern
    response = client.patch(
        f"/replies/{reply_id}",
        json={
            "reply_text": "Dieser Text darf nicht gespeichert werden."
        }
    )

    # 5. API muss die Änderung ablehnen
    assert response.status_code == 409

    # 6. Ursprünglicher Text muss erhalten bleiben
    replies = database.get_replies(email_id=email_id)

    assert replies[0]["reply_text"] == original_text
    assert replies[0]["approval_status"] == status    


def test_update_nonexistent_reply(client):

    # Eine nicht vorhandene Antwort-ID verwenden
    reply_id = 999999

    # Versuchen, die Antwort zu bearbeiten
    response = client.patch(
        f"/replies/{reply_id}",
        json={
            "reply_text": "Neuer Antworttext"
        }
    )

    # Die API muss den Fehler korrekt behandeln
    assert response.status_code == 404

    assert response.json()["detail"] == "Reply not found" 

def test_cannot_save_empty_reply(client):
    """Prüft, ob leere Antworttexte abgelehnt werden."""

    # Eine Antwort nur mit Leerzeichen simulieren
    response = client.patch(
        "/replies/9",
        json={
            "reply_text": "   "
        }
    )

    # FastAPI muss die Eingabe ablehnen
    assert response.status_code == 422

def test_analyze_email_api_unavailable(client, monkeypatch):
    """Prüft HTTP 503 bei einem OpenAI-Ausfall."""

    # 1. OpenAI-Ausfall simulieren
    def fake_analyze_email(email_text):
        raise RuntimeError(
            "OpenAI hat nicht rechtzeitig geantwortet."
        )

    # 2. Echte KI-Funktion durch Mock ersetzen
    monkeypatch.setattr(
        "app.api.analyze_email",
        fake_analyze_email
    )

    # 3. Anfrage an FastAPI senden
    response = client.post(
        "/emails/analyze",
        json={
            "email_text": "Guten Tag, meine Bestellung ist nicht angekommen.",
            "customer_name": "Max Müller"
        }
    )

    # 4. HTTP-Status prüfen
    assert response.status_code == 503

    # 5. Fehlermeldung prüfen
    assert response.json() == {
        "detail": "OpenAI hat nicht rechtzeitig geantwortet."
    }    