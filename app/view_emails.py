
from database import get_emails

print("--- All Emails ---")

emails = get_emails()

for email in emails:
    print(email)

print("\n--- High Priority Emails (P1) ---")

high_priority_emails = get_emails(priority="P1")

for email in high_priority_emails:
    print(email)
