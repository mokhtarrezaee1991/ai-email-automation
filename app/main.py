
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from rules import assign_priority, assign_department
from database import create_database, save_email


# 1. API-Key laden
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY wurde nicht gefunden.")

client = OpenAI(api_key=api_key)


# 2. Struktur der KI-Analyse
class EmailAnalysis(BaseModel):
    category: Literal[
        "Versand",
        "Rechnung",
        "Technischer Support",
        "Sonstiges"
    ]
    urgency: Literal["Niedrig", "Mittel", "Hoch"]
    summary: str


# 3. Beispiel-Kunden-E-Mail
email = """
Guten Tag,

ich habe vor fünf Tagen einen Laptop bestellt und bereits bezahlt.
Leider habe ich bisher weder eine Versandbestätigung noch eine
Sendungsnummer erhalten.

Ich benötige den Laptop dringend für meine Arbeit.
Können Sie mir bitte helfen?

Mit freundlichen Grüßen
Max Müller
"""


# 4. E-Mail mit OpenAI analysieren
response = client.responses.parse(
    model="gpt-4.1-mini",
    instructions="""
    Du bist ein KI-Assistent für den Kundenservice.

    Analysiere die Kunden-E-Mail.

    Bestimme:
    - Kategorie
    - Dringlichkeit
    - Kurze Zusammenfassung des Anliegens

    Verwende ausschließlich die vorgegebenen Kategorien.

    Bewerte die Dringlichkeit anhand des Inhalts.
    Eine dringende Formulierung allein bedeutet nicht automatisch
    eine hohe Dringlichkeit.

    Antworte auf Deutsch.
    """,
    input=email,
    text_format=EmailAnalysis,
    max_output_tokens=250,
)


# 5. Strukturierte KI-Antwort prüfen
analysis = response.output_parsed

if analysis is None:
    raise ValueError("Keine strukturierte Analyse erhalten.")

print("--- AI Email Analysis ---")
print(analysis.model_dump_json(indent=2))


# 6. Business Rules anwenden
priority = assign_priority(analysis.urgency)
department = assign_department(analysis.category)


# 7. Workflow-Ergebnis ausgeben
print("\n--- Workflow Decision ---")
print(f"Category: {analysis.category}")
print(f"Urgency: {analysis.urgency}")
print(f"Priority: {priority}")
print(f"Department: {department}")

# Datenbank vorbereiten
create_database()

# Analyse und Workflow-Ergebnis speichern
email_id = save_email(
    email_text=email,
    category=analysis.category,
    urgency=analysis.urgency,
    summary=analysis.summary,
    priority=priority,
    department=department
)

print(f"\nEmail saved successfully! ID: {email_id}")