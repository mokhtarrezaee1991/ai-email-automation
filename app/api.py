
from fastapi import FastAPI

from app.database import create_database, get_emails
from fastapi import FastAPI, HTTPException
from app.database import (
    create_database,
    get_emails,
    get_email_by_id
)

from pydantic import BaseModel
from typing import Literal
from app.database import save_email
from app.rules import assign_priority, assign_department
from app.email_analyzer import analyze_email

from app.email_generator import generate_email_reply
from app.database import save_reply
from app.database import update_reply_status


# FastAPI-Anwendung erstellen
app = FastAPI(
    title="AI Email Automation API",
    description="REST API for AI-powered email automation",
    version="1.0.0"
)


# Datenbank vorbereiten
create_database()


class EmailCreate(BaseModel):
    email_text: str
    category: Literal[
        "Versand",
        "Rechnung",
        "Technischer Support",
        "Sonstiges"
    ]
    urgency: Literal["Niedrig", "Mittel", "Hoch"]
    summary: str

class EmailAnalyzeRequest(BaseModel):
    email_text: str


# Startseite
@app.get("/")
def home():
    return {
        "message": "AI Email Automation API is running"
    }


# Gespeicherte E-Mails abrufen

@app.get("/emails")
def read_emails(priority: str | None = None):
    emails = get_emails(priority=priority)

    return {
        "total": len(emails),
        "emails": emails
    }


@app.get("/emails/{email_id}")
def read_email_by_id(email_id: int):
    email = get_email_by_id(email_id)

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    return email


@app.post("/emails", status_code=201)
def create_email(email: EmailCreate):

    # Business Rules anwenden
    priority = assign_priority(email.urgency)
    department = assign_department(email.category)

    # E-Mail in SQLite speichern
    email_id = save_email(
        email_text=email.email_text,
        category=email.category,
        urgency=email.urgency,
        summary=email.summary,
        priority=priority,
        department=department
    )

    return {
        "message": "Email created successfully",
        "email_id": email_id,
        "priority": priority,
        "department": department,
        "status": "New"
    }



@app.post("/emails/analyze", status_code=201)
def analyze_and_save_email(request: EmailAnalyzeRequest):

    # 1. E-Mail mit KI analysieren
    analysis = analyze_email(request.email_text)

    # 2. Business Rules anwenden
    priority = assign_priority(analysis.urgency)
    department = assign_department(analysis.category)

    # 3. Ergebnis in SQLite speichern
    email_id = save_email(
        email_text=request.email_text,
        category=analysis.category,
        urgency=analysis.urgency,
        summary=analysis.summary,
        priority=priority,
        department=department
    )

    # 4. Ergebnis zurückgeben
    return {
        "message": "Email analyzed and saved successfully",
        "email_id": email_id,
        "category": analysis.category,
        "urgency": analysis.urgency,
        "summary": analysis.summary,
        "priority": priority,
        "department": department,
        "status": "New"
    }


@app.post("/emails/{email_id}/generate-reply", status_code=201)
def generate_reply(email_id: int):

    # 1. Gespeicherte Kunden-E-Mail abrufen
    email = get_email_by_id(email_id)

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    # 2. KI-Antwortentwurf erstellen
    reply_text = generate_email_reply(
        email_text=email["email_text"],
        category=email["category"],
        summary=email["summary"]
    )

    # 3. Antwortentwurf in SQLite speichern
    reply_id = save_reply(
        email_id=email_id,
        reply_text=reply_text
    )

    # 4. Ergebnis zurückgeben
    return {
        "message": "Reply generated successfully",
        "reply_id": reply_id,
        "email_id": email_id,
        "reply_text": reply_text,
        "approval_status": "Pending Approval"
    }


@app.patch("/replies/{reply_id}/approval")
def approve_or_reject_reply(
    reply_id: int,
    status: Literal["Approved", "Rejected"]
):
    success = update_reply_status(
        reply_id=reply_id,
        new_status=status
    )

    if not success:
        raise HTTPException(
            status_code=409,
            detail="Reply not found or already processed"
        )

    return {
        "message": "Reply status updated successfully",
        "reply_id": reply_id,
        "approval_status": status
    }
