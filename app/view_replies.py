
from database import get_replies

# Alle gespeicherten Antwortentwürfe abrufen
replies = get_replies()

print("--- Saved Email Replies ---")

for reply in replies:
    print(f"\nReply ID: {reply['id']}")
    print(f"Email ID: {reply['email_id']}")
    print(f"Status: {reply['approval_status']}")
    print(f"Created At: {reply['created_at']}")
    print("\nReply Text:")
    print(reply["reply_text"])

# Nur Entwürfe für Kunden-E-Mail ID 1
print("\n--- Replies for Email ID 1 ---")

email_replies = get_replies(email_id=1)

print(f"Found: {len(email_replies)} replies")
