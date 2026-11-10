
import sqlite3
from pathlib import Path

# Pfad zum Projektordner
BASE_DIR = Path(__file__).resolve().parent.parent

# Speicherort der Datenbank
DB_PATH = BASE_DIR / "data" / "emails.db"


def create_database():
    # Datenordner erstellen, falls er nicht existiert
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Verbindung zur SQLite-Datenbank herstellen
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Tabelle 1: Kunden-E-Mails
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_text TEXT NOT NULL,
                customer_name TEXT,
                category TEXT NOT NULL,
                urgency TEXT NOT NULL,
                summary TEXT NOT NULL,
                priority TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabelle 2: KI-generierte Antwortentwürfe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                reply_text TEXT NOT NULL,
                approval_status TEXT NOT NULL
                    DEFAULT 'Pending Approval'
                    CHECK (
                        approval_status IN (
                            'Pending Approval',
                            'Approved',
                            'Rejected'
                        )
                    ),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (email_id)
                    REFERENCES emails(id)
            )
        """)
                # Bestehende Datenbank um den Kundennamen erweitern
        cursor.execute("PRAGMA table_info(emails)")
        columns = [row[1] for row in cursor.fetchall()]

        if "customer_name" not in columns:
            cursor.execute("""
                ALTER TABLE emails
                ADD COLUMN customer_name TEXT
            """)

        conn.commit()

    print(f"Database created successfully: {DB_PATH}")


def save_email(
    email_text: str,
    category: str,
    urgency: str,
    summary: str,
    priority: str,
    department: str,
    customer_name: str | None = None
) -> int:
    """Speichert eine analysierte E-Mail in der SQLite-Datenbank."""

    # Kundennamen bereinigen
    # Entfernt Leerzeichen und Zeilenumbrüche am Anfang und Ende
    customer_name = customer_name.strip() if customer_name else None

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO emails (
                email_text,
                customer_name,
                category,
                urgency,
                summary,
                priority,
                department
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            email_text,
            customer_name,
            category,
            urgency,
            summary,
            priority,
            department
        ))

        conn.commit()

        return cursor.lastrowid






def get_emails(priority=None, category=None):
    """Liest gespeicherte E-Mails mit optionalen Filtern."""

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # SQL-Abfrage vorbereiten
        query = """
            SELECT
                id,
                customer_name,
                category,
                urgency,
                priority,
                department,
                status,
                created_at
            FROM emails
            WHERE 1=1
        """

        parameters = []

        # Optionaler Prioritätsfilter
        if priority:
            query += " AND priority = ?"
            parameters.append(priority)

        # Optionaler Kategoriefilter
        if category:
            query += " AND category = ?"
            parameters.append(category)

        # Neueste E-Mails zuerst anzeigen
        query += " ORDER BY created_at DESC, id DESC"

        cursor.execute(query, parameters)

        return [dict(row) for row in cursor.fetchall()]




def update_email_status(email_id: int, new_status: str) -> bool:
    allowed_statuses = ["New", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        raise ValueError(f"Ungültiger Status: {new_status}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE emails
            SET status = ?
            WHERE id = ?
        """, (new_status, email_id))

        conn.commit()

        return cursor.rowcount > 0


def save_reply(email_id: int, reply_text: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        # Fremdschlüsselprüfung aktivieren
        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO email_replies (
                email_id,
                reply_text
            )
            VALUES (?, ?)
        """, (email_id, reply_text))

        conn.commit()

        return cursor.lastrowid


def get_replies(email_id=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if email_id is not None:
            cursor.execute("""
                SELECT
                    id,
                    email_id,
                    reply_text,
                    approval_status,
                    created_at
                FROM email_replies
                WHERE email_id = ?
                ORDER BY id DESC
            """, (email_id,))
        else:
            cursor.execute("""
                SELECT
                    id,
                    email_id,
                    reply_text,
                    approval_status,
                    created_at
                FROM email_replies
                ORDER BY id DESC
            """)

        return [dict(row) for row in cursor.fetchall()]


def update_reply_status(reply_id: int, new_status: str) -> bool:
    allowed_statuses = ["Approved", "Rejected"]

    if new_status not in allowed_statuses:
        raise ValueError(f"Ungültiger Freigabestatus: {new_status}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE email_replies
            SET approval_status = ?
            WHERE id = ?
              AND approval_status = 'Pending Approval'
        """, (new_status, reply_id))

        conn.commit()

        return cursor.rowcount > 0


def get_email_by_id(email_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM emails
            WHERE id = ?
        """, (email_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)


if __name__ == "__main__":
    create_database()
