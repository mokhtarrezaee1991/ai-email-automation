
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    # Temporäre Datenbank statt echter Projektdatenbank
    db_path = tmp_path / "test_emails.db"

    monkeypatch.setattr(database, "DB_PATH", db_path)

    database.create_database()

    return db_path


def test_update_status_success(test_db):
    email_id = database.save_email(
        email_text="Wo ist meine Bestellung?",
        category="Versand",
        urgency="Mittel",
        summary="Kunde fragt nach seiner Bestellung.",
        priority="P2",
        department="Logistik"
    )

    success = database.update_email_status(
        email_id, "In Progress"
    )

    assert success is True

    emails = database.get_emails()
    assert emails[0]["status"] == "In Progress"


def test_invalid_status(test_db):
    with pytest.raises(ValueError):
        database.update_email_status(1, "Unknown")


def test_email_not_found(test_db):
    success = database.update_email_status(
        999, "Resolved"
    )

    assert success is False


# Hilfsfunktion: Test-E-Mail mit Antwortentwurf erstellen
def create_test_reply():
    email_id = database.save_email(
        email_text="Wo ist meine Bestellung?",
        category="Versand",
        urgency="Mittel",
        summary="Kunde fragt nach dem Versandstatus.",
        priority="P2",
        department="Logistik"
    )

    reply_id = database.save_reply(
        email_id=email_id,
        reply_text="Vielen Dank. Wir prüfen Ihre Anfrage."
    )

    return reply_id


def test_approve_reply(test_db):
    reply_id = create_test_reply()

    success = database.update_reply_status(
        reply_id, "Approved"
    )

    assert success is True

    replies = database.get_replies()
    assert replies[0]["approval_status"] == "Approved"


def test_reject_reply(test_db):
    reply_id = create_test_reply()

    success = database.update_reply_status(
        reply_id, "Rejected"
    )

    assert success is True

    replies = database.get_replies()
    assert replies[0]["approval_status"] == "Rejected"


def test_double_approval(test_db):
    reply_id = create_test_reply()

    first_approval = database.update_reply_status(
        reply_id, "Approved"
    )

    second_approval = database.update_reply_status(
        reply_id, "Approved"
    )

    assert first_approval is True
    assert second_approval is False


def test_invalid_approval_status(test_db):
    reply_id = create_test_reply()

    with pytest.raises(ValueError):
        database.update_reply_status(
            reply_id, "Unknown"
        )

