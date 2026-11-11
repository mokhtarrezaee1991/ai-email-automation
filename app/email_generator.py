
import os

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    APIStatusError
)

# Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

# OpenAI-Client konfigurieren
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=15.0,
    max_retries=0
)


def generate_email_reply(
    email_text: str,
    category: str,
    summary: str,
    customer_name: str | None = None
) -> str:
    """Erstellt einen KI-generierten Antwortentwurf für eine Kunden-E-Mail."""

    try:
        # 1. Anfrage an die OpenAI API senden
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions="""
            Du bist ein professioneller Kundenservice-Assistent.

            Erstelle einen höflichen Antwortentwurf auf Deutsch.

            Regeln:
            - Verwende den Kundennamen für eine persönliche Anrede,
              wenn ein Name vorhanden ist.
            - Falls kein Name vorhanden ist, verwende
              "Guten Tag," als neutrale Anrede.
            - Verwende eine passende Anrede wie
              "Sehr geehrter Herr Müller" oder
              "Sehr geehrte Frau Schmidt".
            - Bedanke dich für die Nachricht.
            - Gehe konkret auf das Anliegen ein.
            - Schreibe klar und freundlich.
            - Erfinde keine Bestellnummern, Liefertermine
              oder Informationen zum Bestellstatus.
            - Versprich keine Lösung, die nicht bestätigt ist.
            - Falls Informationen fehlen, erkläre,
              dass der Sachverhalt geprüft werden muss.
            - Unterschreibe mit "Ihr Kundenservice-Team".

            Erstelle ausschließlich einen Antwortentwurf.
            """,
            input=f"""
            Kundenname: {customer_name or "Nicht angegeben"}

            Kunden-E-Mail:
            {email_text}

            Kategorie: {category}
            Zusammenfassung: {summary}
            """,
            max_output_tokens=350,
        )

        # 2. Generierten Antworttext auslesen
        reply_text = response.output_text

        # 3. Prüfen, ob ein gültiger Antworttext vorhanden ist
        if not reply_text or not reply_text.strip():
            raise ValueError(
                "OpenAI hat keinen gültigen Antworttext geliefert."
            )

        # 4. Antworttext ohne äußere Leerzeichen zurückgeben
        return reply_text.strip()

    except APITimeoutError as error:
        # OpenAI antwortet nicht innerhalb des Zeitlimits
        raise RuntimeError(
            "OpenAI hat bei der Antwortgenerierung "
            "nicht rechtzeitig geantwortet."
        ) from error

    except APIConnectionError as error:
        # Verbindung zur OpenAI API fehlgeschlagen
        raise RuntimeError(
            "Verbindung zur OpenAI API bei der "
            "Antwortgenerierung fehlgeschlagen."
        ) from error

    except APIStatusError as error:
        # OpenAI gibt einen HTTP-Fehler zurück
        raise RuntimeError(
            f"OpenAI API-Fehler bei der Antwortgenerierung: "
            f"HTTP {error.status_code}"
        ) from error
