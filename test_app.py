"""
Automated Test Suite for Data Redundancy Removal System
======================================================
Uses Python's unittest framework and Flask's test client.
Each test runs against an isolated, temporary SQLite database
to ensure tests are 100% reproducible and will not modify or
delete any data in the real 'redundancy.db'.
"""

import os
import tempfile
import unittest
import database
from app import app


class DataRedundancyTestCase(unittest.TestCase):
    """
    Test case suite covering all core requirements:
      - Page rendering
      - Valid unique insertions
      - Exact duplicate detection
      - Case-insensitive & whitespace-trimmed duplicate detection
      - Server-side email format validation
      - Required field presence validation
      - Database isolation
    """

    def setUp(self):
        """
        Runs BEFORE every individual test method.
        Creates a fresh, temporary SQLite database file and points
        the database module to it.
        """
        # Create a unique temporary file for the test database
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)  # Close file descriptor so SQLite can open it on Windows

        # Redirect database.py to use this temporary test database
        self.original_db_name = database.DB_NAME
        database.DB_NAME = self.temp_db_path

        # Initialize the fresh schema in the test database
        database.init_db()

        # Configure Flask application for testing mode
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        """
        Runs AFTER every individual test method.
        Restores the original database configuration and cleans up
        the temporary test database file.
        """
        # Restore original database filename
        database.DB_NAME = self.original_db_name

        # Delete the temporary database file
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def test_01_home_page_loads_successfully(self):
        """
        Verify that the home route (GET /) responds with HTTP 200 OK
        and displays the main interface elements.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Data Redundancy Removal System", response.data)
        self.assertIn(b"Add New Record", response.data)
        self.assertIn(b"No Records Found", response.data)

    def test_02_insert_valid_unique_record(self):
        """
        Verify that a valid, unique record is inserted into the database,
        shows a green success flash message, and displays in the table.
        """
        response = self.client.post(
            "/",
            data={"name": "Alice Smith", "email": "alice@example.com"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"successfully saved", response.data)
        self.assertIn(b"Alice Smith", response.data)
        self.assertIn(b"alice@example.com", response.data)

        # Verify record directly in database
        records = database.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice Smith")
        self.assertEqual(records[0]["email"], "alice@example.com")
        self.assertEqual(records[0]["normalized_email"], "alice@example.com")

    def test_03_reject_exact_duplicate_email(self):
        """
        Verify that attempting to insert an email that already exists
        is rejected by the database UNIQUE constraint and shows a warning.
        """
        # First insertion: succeeds
        self.client.post(
            "/",
            data={"name": "Alice Smith", "email": "alice@example.com"},
            follow_redirects=True,
        )

        # Second insertion with the same email: must be rejected
        response = self.client.post(
            "/",
            data={"name": "Alice Copy", "email": "alice@example.com"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Duplicate detected", response.data)

        # Database must still contain only 1 record
        records = database.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice Smith")

    def test_04_reject_case_insensitive_and_whitespace_duplicate(self):
        """
        Verify that variations like uppercase letters and outer whitespace
        are normalized and properly caught as duplicates.
        e.g. 'alice@example.com' vs '  ALICE@EXAMPLE.COM  '
        """
        # Insert lowercase original
        self.client.post(
            "/",
            data={"name": "Original User", "email": "bob.builder@example.com"},
            follow_redirects=True,
        )

        # Attempt to insert uppercase with spaces
        response = self.client.post(
            "/",
            data={
                "name": "Impostor Bob",
                "email": "   BOB.BUILDER@EXAMPLE.COM   ",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Duplicate detected", response.data)

        # Verify only the original record exists
        records = database.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Original User")
        self.assertEqual(records[0]["normalized_email"], "bob.builder@example.com")

    def test_05_reject_invalid_email_format(self):
        """
        Verify that invalid email strings are caught by server-side regex validation
        and are rejected before reaching database insertion.
        """
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "missingdomain@.com",
            "spaces in email@domain.com",
        ]

        for invalid_email in invalid_emails:
            response = self.client.post(
                "/",
                data={"name": "Test User", "email": invalid_email},
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Validation Error", response.data)
            self.assertIn(b"not a valid email address format", response.data)

        # Database must remain empty
        records = database.get_all_records()
        self.assertEqual(len(records), 0)

    def test_06_reject_missing_fields(self):
        """
        Verify that empty or whitespace-only inputs are rejected with validation warnings.
        """
        test_payloads = [
            {"name": "", "email": ""},
            {"name": "   ", "email": "   "},
            {"name": "", "email": "user@example.com"},
            {"name": "Valid Name", "email": ""},
        ]

        for payload in test_payloads:
            response = self.client.post("/", data=payload, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Both Name and Email fields are required", response.data)

        # Database must remain empty
        records = database.get_all_records()
        self.assertEqual(len(records), 0)

    def test_07_multiple_unique_records_displayed_correctly(self):
        """
        Verify that multiple genuinely unique records can all be stored
        and are correctly retrieved in newest-first order.
        """
        users = [
            ("User One", "user1@example.com"),
            ("User Two", "user2@example.com"),
            ("User Three", "user3@example.com"),
        ]

        for name, email in users:
            self.client.post(
                "/", data={"name": name, "email": email}, follow_redirects=True
            )

        records = database.get_all_records()
        self.assertEqual(len(records), 3)

        # Verify all 3 unique normalized emails are stored
        saved_emails = {r["normalized_email"] for r in records}
        self.assertEqual(
            saved_emails,
            {"user1@example.com", "user2@example.com", "user3@example.com"},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
