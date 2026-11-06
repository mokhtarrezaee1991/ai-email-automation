
from database import get_replies, update_reply_status

reply_id = 1

# Entwurf vor der Entscheidung anzeigen
replies = get_replies()

reply = next(
    (item for item in replies if item["id"] == reply_id),
    None
)

if reply is None:
    print("Antwortentwurf nicht gefunden.")

elif reply["approval_status"] != "Pending Approval":
    print("Dieser Entwurf wurde bereits bearbeitet.")

else:
    print("--- Reply for Approval ---")
    print(reply["reply_text"])

    print("\n1 - Approve")
    print("2 - Reject")
    print("3 - Cancel")

    choice = input("\nYour choice: ")

    if choice == "1":
        new_status = "Approved"
    elif choice == "2":
        new_status = "Rejected"
    else:
        new_status = None

    if new_status:
        success = update_reply_status(reply_id, new_status)

        if success:
            print(f"\nReply {reply_id}: {new_status}")
        else:
            print("\nStatus konnte nicht geändert werden.")
    else:
        print("\nKeine Änderung vorgenommen.")
