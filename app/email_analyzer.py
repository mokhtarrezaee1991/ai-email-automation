
import os
from typing import Literal

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    APIStatusError
)
from pydantic import BaseModel

load_dotenv()


class EmailAnalysis(BaseModel):
    category: Literal[
        "Versand",
        "Rechnung",
        "Technischer Support",
        "Sonstiges"
    ]
    urgency: Literal["Niedrig", "Mittel", "Hoch"]
    summary: str


def analyze_email(email_text: str) -> EmailAnalysis:

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=15.0,
        max_retries=0
    )

    try:
        response = client.responses.parse(
            model="gpt-4.1-mini",
            instructions="""
            Du bist ein KI-Assistent für den Kundenservice.

            Analysiere die Kunden-E-Mail.

            Bestimme:
            - Kategorie
            - Dringlichkeit
            - Kurze Zusammenfassung

            Verwende ausschließlich die vorgegebenen Kategorien.
            Bewerte die Dringlichkeit anhand des Inhalts.

            Antworte auf Deutsch.
            """,
            input=email_text,
            text_format=EmailAnalysis,
            max_output_tokens=250,
        )

        analysis = response.output_parsed

        if analysis is None:
            raise ValueError(
                "Keine strukturierte Analyse erhalten."
            )

        return analysis

    except APITimeoutError as error:
        raise RuntimeError(
            "OpenAI hat nicht rechtzeitig geantwortet."
        ) from error

    except APIConnectionError as error:
        raise RuntimeError(
            "Verbindung zur OpenAI API fehlgeschlagen."
        ) from error

    except APIStatusError as error:
        raise RuntimeError(
            f"OpenAI API-Fehler: HTTP {error.status_code}"
        ) from error