
from email_generator import generate_email_reply

email = """
Guten Tag,

ich habe vor fünf Tagen einen Laptop bestellt.
Leider habe ich noch keine Versandbestätigung erhalten.

Können Sie mir bitte mitteilen, wann mein Laptop geliefert wird?

Mit freundlichen Grüßen
Max Müller
"""

reply = generate_email_reply(
    email_text=email,
    category="Versand",
    summary="Kunde fragt nach dem Lieferstatus seines Laptops."
)

print("\n--- AI Generated Reply ---")
print(reply)
