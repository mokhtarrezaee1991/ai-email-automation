
import requests
import streamlit as st

# ---------------------------------------
# 1. Streamlit-Konfiguration
# ---------------------------------------

st.set_page_config(
    page_title="AI Email Automation",
    page_icon="📧",
    layout="wide"
)

# FastAPI-Adresse
API_URL = "http://127.0.0.1:8000"


# ---------------------------------------
# 2. API-Funktionen
# ---------------------------------------

def update_reply_text(reply_id: int, new_text: str) -> bool:
    """Speichert eine bearbeitete KI-Antwort über FastAPI."""

    try:
        response = requests.patch(
            f"{API_URL}/replies/{reply_id}",
            json={"reply_text": new_text},
            timeout=10
        )

        response.raise_for_status()

        return True

    except requests.exceptions.RequestException as error:
        st.error(
            f"Antwort konnte nicht gespeichert werden: {error}"
        )
        return False
def update_approval_status(reply_id, status):
    """Sendet eine Freigabeentscheidung an n8n und prüft das Ergebnis."""

    webhook_url = "http://localhost:5678/webhook/email-approval"

    payload = {
        "reply_id": reply_id,
        "status": status
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=15
        )

        # Prüfen, ob n8n einen HTTP-Fehler zurückgegeben hat
        response.raise_for_status()

        # JSON-Antwort von n8n lesen
        result = response.json()

        # Prüfen, ob FastAPI die Änderung bestätigt hat
        if (
            result.get("reply_id") == reply_id
            and result.get("approval_status") == status
            and result.get("message") == "Reply status updated successfully"
        ):
            return True

        st.error(
            "Die Statusänderung wurde nicht von FastAPI bestätigt."
        )
        return False

    except requests.exceptions.RequestException as error:
        st.error(f"Fehler bei der Verbindung zu n8n: {error}")
        return False

    except ValueError:
        st.error("n8n hat keine gültige JSON-Antwort zurückgegeben.")
        return False




def get_email_details(email_id):
    """Lädt die ursprüngliche Kunden-E-Mail über FastAPI."""

    try:
        response = requests.get(
            f"{API_URL}/emails/{email_id}",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        # Unterstützt direkte E-Mail-Daten
        # und Antworten mit einem "email"-Objekt.
        if isinstance(data, dict):
            email = data.get("email", data)

            if isinstance(email, dict):
                return email

        st.warning("Unerwartetes Format der E-Mail-Daten.")
        return None

    except requests.exceptions.RequestException as error:
        st.error(
            f"E-Mail #{email_id} konnte nicht geladen werden: {error}"
        )
        return None


# ---------------------------------------
# 3. Dashboard-Titel
# ---------------------------------------

st.title("AI Email Automation Dashboard")

st.write(
    "Verwaltung und Freigabe von KI-generierten E-Mail-Antworten"
)

st.divider()



# ---------------------------------------
# 4. E-Mail-Übersicht
# ---------------------------------------

st.subheader("E-Mail-Übersicht")

# Zwei Filter nebeneinander anzeigen
col1, col2 = st.columns(2)

with col1:
    priority_filter = st.selectbox(
        "E-Mails nach Priorität filtern",
        options=["Alle", "P1", "P2", "P3"],
        index=0
    )

with col2:
    category_filter = st.selectbox(
        "E-Mails nach Kategorie filtern",
        options=[
            "Alle",
            "Rechnung",
            "Versand",
            "Technischer Support"
        ],
        index=0
    )

# ---------------------------------------
# API-Parameter vorbereiten
# ---------------------------------------

# Bei "Alle" wird der jeweilige Filter
# nicht an die API gesendet.
params = {}

if priority_filter != "Alle":
    params["priority"] = priority_filter

if category_filter != "Alle":
    params["category"] = category_filter

# ---------------------------------------
# E-Mails über FastAPI abrufen
# ---------------------------------------

try:
    response = requests.get(
        f"{API_URL}/emails",
        params=params,
        timeout=5
    )

    response.raise_for_status()

    emails = response.json()
    email_list = emails.get("emails", [])

    if email_list:

        st.write(
            f"Angezeigte E-Mails: {len(email_list)}"
        )

        # Relevante Tabellenspalten
        columns = [
            "id",
            "customer_name",
            "category",
            "urgency",
            "priority",
            "department",
            "status"
        ]

        # Tabellendaten vorbereiten
        table_data = [
            {
                column: email.get(column, "")
                for column in columns
            }
            for email in email_list
        ]

        # E-Mail-Tabelle anzeigen
        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Keine E-Mails für die ausgewählten Filter vorhanden."
        )

except requests.exceptions.RequestException as error:
    st.error(
        f"E-Mails konnten nicht geladen werden: {error}"
    )



# ---------------------------------------
# 5. Antwortfreigabe
# ---------------------------------------

st.divider()

st.subheader("Antwortfreigabe")

try:
    # Alle KI-Antworten über FastAPI abrufen
    response = requests.get(
        f"{API_URL}/replies",
        timeout=5
    )

    response.raise_for_status()

    replies = response.json().get("replies", [])

    # Nur Antworten mit offenem Freigabestatus
    pending_replies = [
        reply
        for reply in replies
        if reply.get("approval_status") == "Pending Approval"
    ]

    st.write(
        f"Offene Freigaben: {len(pending_replies)}"
    )

    if pending_replies:

        for reply in pending_replies:

            email_id = reply["email_id"]
            reply_id = reply["id"]
            reply_text = reply["reply_text"]
            approval_status = reply["approval_status"]

            with st.expander(
                f"E-Mail #{email_id} | Antwort #{reply_id}"
            ):

                # ---------------------------------------
                # Ursprüngliche Kunden-E-Mail
                # ---------------------------------------

                st.markdown("### Kundenanfrage")

                email_details = get_email_details(email_id)

                if email_details:

                    customer_name = (
                        email_details.get("customer_name")
                        or "Nicht angegeben"
                    )

                    email_text = (
                        email_details.get("email_text")
                        or email_details.get("text")
                        or "Kein E-Mail-Text vorhanden."
                    )

                    st.write(
                        f"**Kunde:** {customer_name}"
                    )

                    st.write("**Originalnachricht:**")
                    st.text(email_text)

                    st.write(
                        f"**Kategorie:** "
                        f"{email_details.get('category') or '-'}"
                    )

                    st.write(
                        f"**Dringlichkeit:** "
                        f"{email_details.get('urgency') or '-'}"
                    )

                    st.write(
                        f"**Priorität:** "
                        f"{email_details.get('priority') or '-'}"
                    )

                    st.write(
                        f"**Abteilung:** "
                        f"{email_details.get('department') or '-'}"
                    )

                else:
                    st.warning(
                        "Die ursprüngliche E-Mail ist nicht verfügbar."
                    )

                st.divider()

                # ---------------------------------------
                # KI-generierte Antwort
                # ---------------------------------------

                st.markdown("### KI-generierte Antwort")

                # Antwort in einem bearbeitbaren Textfeld anzeigen
                edited_reply = st.text_area(
                    "Antwort bearbeiten",
                    value=reply_text,
                    height=220,
                    key=f"reply_editor_{reply_id}"
                )

                # Prüfen, ob der Text verändert wurde
                text_changed = edited_reply != reply_text

                # Änderungen speichern
                if st.button(
                    "Änderungen speichern",
                    key=f"save_reply_{reply_id}",
                    disabled=not text_changed
                ):

                    if not edited_reply.strip():
                        st.warning("Die Antwort darf nicht leer sein.")

                    elif update_reply_text(
                        reply_id,
                        edited_reply.strip()
                    ):
                        st.success("Antwort erfolgreich gespeichert!")
                        st.rerun()

                st.write(
                    f"**Freigabestatus:** {approval_status}"
                )

                st.divider()

                # ---------------------------------------
                # Freigabe und Ablehnung
                # ---------------------------------------

                col1, col2 = st.columns(2)

                with col1:

                   
                    if st.button(
                        "Freigeben",
                        key=f"approve_{reply_id}",
                        type="primary",
                        disabled=text_changed
                    ):    

                        if update_approval_status(
                            reply_id,
                            "Approved"
                        ):
                            st.rerun()

                with col2:

                    if st.button(
                        "Ablehnen",
                        key=f"reject_{reply_id}",
                        disabled=text_changed
                    ):

                        if update_approval_status(
                            reply_id,
                            "Rejected"
                        ):
                            st.rerun()

    else:
        st.success(
            "Keine offenen Freigaben vorhanden."
        )

except requests.exceptions.RequestException as error:
    st.error(
        f"KI-Antworten konnten nicht geladen werden: {error}"
    )

# ---------------------------------------
# 6. Bearbeitete Antworten
# ---------------------------------------

st.divider()
st.subheader("Bearbeitete Antworten")

if "replies" in locals():

    processed_replies = [
        reply
        for reply in replies
        if reply.get("approval_status") in [
            "Approved",
            "Rejected"
        ]
    ]

    st.write(
        f"Bearbeitete Antworten: {len(processed_replies)}"
    )

    if processed_replies:

        table_data = [
            {
                "E-Mail-ID": reply["email_id"],
                "Antwort-ID": reply["id"],
                "Freigabestatus": reply["approval_status"]
            }
            for reply in processed_replies
        ]

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Noch keine bearbeiteten Antworten vorhanden.")

else:
    st.warning("Antwortdaten konnten nicht geladen werden.")

# ---------------------------------------
# 6. API-Verbindung
# ---------------------------------------

st.divider()

st.subheader("API-Verbindung")

try:
    # FastAPI-Verbindung überprüfen
    response = requests.get(
        f"{API_URL}/emails",
        timeout=5
    )

    response.raise_for_status()

    st.success(
        "Verbindung zur FastAPI erfolgreich!"
    )

except requests.exceptions.RequestException as error:
    st.error(
        f"Verbindung zur FastAPI fehlgeschlagen: {error}"
    )
