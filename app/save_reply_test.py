
from database import create_database, save_reply

# Datenbank vorbereiten
create_database()

# Bereits gespeicherte Kunden-E-Mail
email_id = 1

# Beispiel-Antwortentwurf
reply_text = """
Sehr geehrter Herr Müller,

vielen Dank für Ihre Nachricht.

Wir haben Ihre Anfrage bezüglich der fehlenden
Versandbestätigung erhalten.

Der aktuelle Versandstatus muss zunächst geprüft werden.

Mit freundlichen Grüßen
Ihr Kundenservice-Team
"""

# Antwortentwurf speichern
reply_id = save_reply(
    email_id=email_id,
    reply_text=reply_text
)

print("\n--- Reply Saved ---")
print(f"Reply ID: {reply_id}")
print(f"Email ID: {email_id}")
print("Approval Status: Pending Approval")
