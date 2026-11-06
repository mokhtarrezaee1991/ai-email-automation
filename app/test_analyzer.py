
from email_analyzer import analyze_email

email = """
Guten Tag,

ich habe eine falsche Rechnung erhalten.
Der Betrag ist deutlich höher als vereinbart.

Bitte prüfen Sie meine Rechnung.

Mit freundlichen Grüßen
Max Müller
"""

analysis = analyze_email(email)

print("\n--- AI Analysis ---")
print(analysis.model_dump_json(indent=2))
