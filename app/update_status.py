
from database import update_email_status, get_emails

# E-Mail mit ID 1 bearbeiten
email_id = 1
new_status = "In Progress"

success = update_email_status(email_id, new_status)

if success:
    print(f"Email {email_id} updated to '{new_status}'")
else:
    print(f"Email {email_id} not found")

# Aktuellen Datenbankinhalt anzeigen
print("\n--- Updated Emails ---")

for email in get_emails():
    print(email)
