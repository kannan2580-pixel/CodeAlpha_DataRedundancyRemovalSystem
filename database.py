"""
Database module for the Data Redundancy Removal System.
Handles SQLite database connection, table initialization, email normalization,
and safe record insertion with duplicate detection.
"""

import sqlite3
from typing import Dict, Any, List

# Name of the SQLite database file
DB_NAME = "redundancy.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Configures row_factory to sqlite3.Row so query results can be
    accessed like Python dictionaries (by column name).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_email(email: str) -> str:
    """
    Normalizes an email address by removing leading/trailing whitespace
    and converting all characters to lowercase.

    Example: '  John.Doe@EXAMPLE.com  ' -> 'john.doe@example.com'
    """
    if not email:
        return ""
    return email.strip().lower()


def init_db() -> None:
    """
    Initializes the SQLite database and creates the 'records' table
    if it does not already exist.

    Table Schema:
      - id: Auto-incrementing unique identifier
      - name: Stored user name
      - email: Original email entered by user
      - normalized_email: Lowercased, trimmed email with UNIQUE constraint
      - created_at: Timestamp of when the record was inserted
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            normalized_email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


def insert_record(name: str, email: str) -> Dict[str, Any]:
    """
    Safely inserts a record into the database using parameterized queries.
    Prevents duplicates using the UNIQUE constraint on normalized_email.

    Returns a dictionary indicating success or the reason for failure:
      - {"success": True, "status": "created", "message": "...", "id": ...}
      - {"success": False, "status": "duplicate", "message": "..."}
      - {"success": False, "status": "invalid", "message": "..."}
      - {"success": False, "status": "error", "message": "..."}
    """
    clean_name = name.strip() if name else ""
    clean_email = email.strip() if email else ""
    normalized = normalize_email(clean_email)

    if not clean_name or not clean_email:
        return {
            "success": False,
            "status": "invalid",
            "message": "Both name and email are required fields.",
        }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Parameterized query with '?' placeholders protects against SQL Injection
        cursor.execute(
            """
            INSERT INTO records (name, email, normalized_email)
            VALUES (?, ?, ?)
            """,
            (clean_name, clean_email, normalized),
        )
        conn.commit()
        new_id = cursor.lastrowid
        return {
            "success": True,
            "status": "created",
            "message": f"Record for '{clean_name}' was successfully saved.",
            "id": new_id,
        }

    except sqlite3.IntegrityError:
        # The UNIQUE constraint on 'normalized_email' was violated
        return {
            "success": False,
            "status": "duplicate",
            "message": f"Duplicate detected: The email address '{clean_email}' is already registered.",
        }

    except sqlite3.Error as e:
        # Catch unexpected database errors safely
        return {
            "success": False,
            "status": "error",
            "message": f"Database error occurred: {str(e)}",
        }

    finally:
        conn.close()


def get_all_records() -> List[Dict[str, Any]]:
    """
    Fetches all records from the database, ordered from newest to oldest.
    Returns a list of dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, normalized_email, created_at
        FROM records
        ORDER BY created_at DESC, id DESC
        """
    )
    rows = cursor.fetchall()
    records = [dict(row) for row in rows]
    conn.close()
    return records


if __name__ == "__main__":
    print("Testing database module standalone...")
    init_db()
    print("[SUCCESS] Database initialized and table 'records' ready.")

    # Quick test 1: Insert original record
    res1 = insert_record("Alice Smith", "alice@example.com")
    print(f"Test 1 (Insert Alice): {res1}")

    # Quick test 2: Insert case-insensitive duplicate with whitespace
    res2 = insert_record("Alice Duplicate", "  ALICE@EXAMPLE.COM  ")
    print(f"Test 2 (Duplicate check): {res2}")

    # Display records
    all_recs = get_all_records()
    print(f"Total stored unique records: {len(all_recs)}")
    for r in all_recs:
        print(f" - [{r['id']}] {r['name']} ({r['email']}) -> Normalized: {r['normalized_email']}")
