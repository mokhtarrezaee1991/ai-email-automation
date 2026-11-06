
import sqlite3
from pathlib import Path

# Pfad zum Projektordner
BASE_DIR = Path(__file__).resolve().parent.parent

# Speicherort der Datenbank
DB_PATH = BASE_DIR / "data" / "emails.db"


def create_database():
    # Datenordner erstellen, falls er nicht existiert
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Verbindung zur SQLite-Datenbank
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_text TEXT NOT NULL,
                category TEXT NOT NULL,
                urgency TEXT NOT NULL,
                summary TEXT NOT NULL,
                priority TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    print(f"Database created successfully: {DB_PATH}")



def save_email(
    email_text: str,
    category: str,
    urgency: str,
    summary: str,
    priority: str,
    department: str
) -> int:

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO emails (
                email_text,
                category,
                urgency,
                summary,
                priority,
                department
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            email_text,
            category,
            urgency,
            summary,
            priority,
            department
        ))

        conn.commit()

        return cursor.lastrowid

if __name__ == "__main__":
    create_database()
