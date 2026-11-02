"""
Data Redundancy Removal System - Flask Web Application
======================================================
This file serves as the main web application controller.
It defines routes, validates incoming user input, leverages database.py
for storage and duplicate prevention, and renders the frontend interface.
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, insert_record, get_all_records

# Initialize Flask application
app = Flask(__name__)

# Secret key required for session management and flash messages.
# In production, set the SECRET_KEY environment variable.
app.secret_key = os.environ.get(
    "SECRET_KEY", "dev-insecure-key-for-local-testing-only"
)

# Regular expression pattern to validate standard email format
# Format: characters@domain.extension
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
)


def is_valid_email(email: str) -> bool:
    """
    Validates whether the provided email string matches a standard email format
    and does not exceed acceptable length limits.
    """
    if not email or len(email.strip()) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route of the web application.
    - GET: Retrieves and displays all saved unique records.
    - POST: Validates submitted Name & Email, calls database insertion,
            handles duplicate detection, and redirects using the
            Post/Redirect/Get pattern to prevent duplicate form submissions.
    """
    if request.method == "POST":
        raw_name = request.form.get("name", "")
        raw_email = request.form.get("email", "")

        name = raw_name.strip()
        email = raw_email.strip()

        # Step 1: Validate required fields presence
        if not name or not email:
            flash(
                "Validation Error: Both Name and Email fields are required.",
                "warning",
            )
            return redirect(url_for("index"))

        # Step 2: Validate server-side email format
        if not is_valid_email(email):
            flash(
                f"Validation Error: '{email}' is not a valid email address format (example: user@example.com).",
                "danger",
            )
            return redirect(url_for("index"))

        # Step 3: Insert record via database.py helper function
        # This safely executes parameterized SQL queries and handles SQLite UNIQUE constraints
        result = insert_record(name=name, email=email)

        # Step 4: Flash appropriate feedback message based on database result
        if result["status"] == "created":
            flash(result["message"], "success")
        elif result["status"] == "duplicate":
            flash(result["message"], "warning")
        else:
            flash(result["message"], "danger")

        # Redirect to GET / to prevent form re-submission on refresh (PRG pattern)
        return redirect(url_for("index"))

    # Fetch all records to display in the table
    records = get_all_records()
    return render_template("index.html", records=records)


# Ensure database table exists whenever app starts
with app.app_context():
    init_db()


if __name__ == "__main__":
    # Run development server locally
    print("=" * 60)
    print("CodeAlpha Data Redundancy Removal System is running!")
    print("Local access URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
