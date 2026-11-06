
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_email_reply(
    email_text: str,
    category: str,
    summary: str
) -> str:

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""
        Du bist ein professioneller Kundenservice-Assistent.

        Erstelle einen höflichen Antwortentwurf auf Deutsch.

        Regeln:
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
        Kunden-E-Mail:
        {email_text}

        Kategorie: {category}
        Zusammenfassung: {summary}
        """,
        max_output_tokens=350,
    )

    return response.output_text
