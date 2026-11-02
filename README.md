# Data Redundancy Removal System

**CodeAlpha Cloud Computing Internship — Task 1**  
A reliable, lightweight data ingestion web application built with **Python**, **Flask**, and **SQLite** to capture, validate, and store unique user records while actively preventing duplicate data entries.

---

## 📌 Project Overview & Problem Statement

In distributed systems and cloud databases, **data redundancy** wastes storage, skews analytics, degrades query performance, and leads to inconsistencies across services. A fundamental challenge in data ingestion pipelines is ensuring that duplicate records are caught early—before they corrupt storage layers.

This project implements a **Data Redundancy Removal System** that:
1. Ingests user records consisting of `name` and `email`.
2. Validates input formatting on the server side.
3. Automatically **normalizes email addresses** (stripping whitespace and converting to lowercase).
4. Employs a database-level **`UNIQUE` constraint** on the normalized email to guarantee zero duplicates even under concurrent access.
5. Displays clear visual feedback (success notifications, duplicate warnings, and validation alerts).
6. Lists all saved unique records in an interactive, responsive dashboard.

> **Note on Deployment Status:**  
> This application currently runs **locally** for development, evaluation, and testing. It has **not** been deployed to cloud hosting environments or paid cloud providers.

---

## ✨ Implemented Features

- **Server-Side Validation**: Ensures required fields are populated and verifies email syntax using regular expressions prior to database operations.
- **Case-Insensitive Deduplication**: Detects duplicates regardless of capitalization or outer whitespace (e.g., `User@Example.com` is recognized as the same identity as `user@example.com`).
- **Database Integrity Enforcement**: Utilizes SQLite's `UNIQUE` constraint on the `normalized_email` column, ensuring data consistency at the persistence layer.
- **SQL Injection Prevention**: All SQL queries utilize **parameterized statements** (`?` placeholders) rather than raw string interpolation.
- **Post/Redirect/Get (PRG) Pattern**: Prevents duplicate form submissions on browser page refresh (`F5`).
- **User-Friendly Flash Notifications**: Distinct visual alerts for:
  - ✅ Record successfully created
  - ⚠️ Duplicate record detected and rejected
  - ❌ Input validation errors (missing fields or invalid email syntax)
- **Responsive Dashboard UI**: Dark-mode interface styled with modern CSS, displaying real-time record counts, original inputs, normalized keys, and timestamps.
- **Isolated Automated Test Suite**: 7 comprehensive unit/integration tests running against isolated temporary databases.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3 (3.13+) | Core application logic and execution runtime |
| **Web Controller** | Flask 3.x | Routing, request handling, flash messaging, template rendering |
| **Database Engine** | SQLite3 (Built-in) | Serverless relational database engine storing records in `redundancy.db` |
| **Templating** | Jinja2 / HTML5 | Semantic structure for inputs, alert dialogs, and records table |
| **Styling** | Vanilla CSS3 | Responsive dark-mode layout, glassmorphism effects, flexbox/grid |
| **Testing** | `unittest` & Flask Test Client | Automated test execution with isolated temporary database fixtures |

---

## 🔍 How Duplicate Detection Works

The system applies a multi-layered approach to redundancy elimination:

```text
[ User Input ]
  Name:  "Jane Doe"
  Email: "  JANE.DOE@Company.Com  "
        │
        ▼
[ Server-Side Validation (app.py) ]
  • Check non-empty: Pass
  • Regex Format Match: Pass
        │
        ▼
[ Normalization (database.py: normalize_email) ]
  • .strip() -> "JANE.DOE@Company.Com"
  • .lower() -> "jane.doe@company.com"
        │
        ▼
[ Parameterized SQL INSERT (database.py) ]
  INSERT INTO records (name, email, normalized_email)
  VALUES (?, ?, ?)
        │
   ┌────┴──────────────────────────┐
   ▼                               ▼
[ Case 1: First Insertion ]     [ Case 2: Duplicate Found ]
UNIQUE constraint passes.       SQLite raises sqlite3.IntegrityError.
Commit transaction.             Catch exception gracefully.
Return status: "created"        Return status: "duplicate"
Flash: Success message          Flash: Warning message
```

1. **Email Normalization**: When a user enters an email address, `normalize_email()` strips leading/trailing spaces and converts all characters to lowercase.
2. **Original vs. Normalized Storage**:
   - `email`: Preserves original casing as entered by the user for presentation purposes.
   - `normalized_email`: The canonical lowercase form marked with a database-level `UNIQUE` constraint.
3. **Graceful Exception Handling**: If an identical normalized email already exists, SQLite blocks the transaction and raises `sqlite3.IntegrityError`. The application catches this error and returns a clean warning instead of crashing or generating duplicate rows.

---

## 📁 Project Structure

```text
CodeAlpha_DataRedundancy/
│
├── .env.example           # Example template for environment configuration (secrets)
├── .gitignore             # Specifies intentionally untracked files (DB, caches, venv)
├── app.py                 # Flask web application controller (routes, validation, PRG flow)
├── database.py            # SQLite helper functions (init_db, normalize_email, insert_record, get_all_records)
├── redundancy.db          # Local SQLite database (ignored by Git)
├── requirements.txt       # Project Python dependencies (Flask)
├── test_app.py            # Automated test suite using unittest and isolated temporary databases
├── README.md              # Project documentation and setup guide
│
├── static/
│   └── css/
│       └── style.css      # Custom styling, dark mode theme, responsive grid, alert badges
│
└── templates/
    └── index.html         # Web interface template with input form, alerts, and records table
```

---

## 💻 Installation & Local Setup (Windows)

### Prerequisites
- **Python 3.10+** (tested with Python 3.13)
- **pip** package installer

### Step 1: Open Terminal in Project Directory
Open **PowerShell** or **Command Prompt** and navigate to the project directory:
```powershell
cd E:\CodeAlpha_DataRedundancy
```

### Step 2: (Optional) Create & Activate a Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1

# (Or on Windows Command Prompt: venv\Scripts\activate.bat)
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Running the Web Application

To start the Flask development server:

```powershell
python app.py
```

You will see output similar to:
```text
============================================================
CodeAlpha Data Redundancy Removal System is running!
Local access URL: http://127.0.0.1:5000
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Automated Testing

The project includes an automated test suite implemented in `test_app.py`. Each test dynamically spins up an isolated temporary SQLite database using `tempfile.mkstemp()`, leaving the production `redundancy.db` completely untouched.

### Run Tests Command
```powershell
python -m unittest test_app -v
```

### Test Suite Breakdown

| Test Name | Method | What It Verifies |
| :--- | :--- | :--- |
| **Test 1** | `test_01_home_page_loads_successfully` | Asserts that `GET /` returns status code `200` and displays the main form and interface. |
| **Test 2** | `test_02_insert_valid_unique_record` | Confirms valid submission stores the record, returns a success flash message, and displays the record in the table. |
| **Test 3** | `test_03_reject_exact_duplicate_email` | Verifies that inserting an already registered email is rejected with a duplicate warning and does not increment database record count. |
| **Test 4** | `test_04_reject_case_insensitive_and_whitespace_duplicate` | Confirms that `bob.builder@example.com` and `  BOB.BUILDER@EXAMPLE.COM  ` collide and the duplicate is safely blocked. |
| **Test 5** | `test_05_reject_invalid_email_format` | Tests invalid patterns (`plainaddress`, `@missinguser.com`, etc.) and asserts they are rejected by server-side regex validation. |
| **Test 6** | `test_06_reject_missing_fields` | Verifies that blank inputs or whitespace-only inputs trigger a required-fields validation warning. |
| **Test 7** | `test_07_multiple_unique_records_displayed_correctly` | Verifies that multiple distinct records are stored concurrently and retrieved in descending chronological order. |

#### Expected Output:
```text
test_01_home_page_loads_successfully (test_app.DataRedundancyTestCase.test_01_home_page_loads_successfully) ... ok
test_02_insert_valid_unique_record (test_app.DataRedundancyTestCase.test_02_insert_valid_unique_record) ... ok
test_03_reject_exact_duplicate_email (test_app.DataRedundancyTestCase.test_03_reject_exact_duplicate_email) ... ok
test_04_reject_case_insensitive_and_whitespace_duplicate (test_app.DataRedundancyTestCase.test_04_reject_case_insensitive_and_whitespace_duplicate) ... ok
test_05_reject_invalid_email_format (test_app.DataRedundancyTestCase.test_05_reject_invalid_email_format) ... ok
test_06_reject_missing_fields (test_app.DataRedundancyTestCase.test_06_reject_missing_fields) ... ok
test_07_multiple_unique_records_displayed_correctly (test_app.DataRedundancyTestCase.test_07_multiple_unique_records_displayed_correctly) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.254s

OK
```

---

## 📝 Example Usage

### Scenario 1: Adding a First Record
- **Name**: `Alice Smith`
- **Email**: `alice@example.com`
- **Result**: Record saved with ID `#1`. Appears in table. Green alert displayed.

### Scenario 2: Attempting an Exact Duplicate
- **Name**: `Alice Smith`
- **Email**: `alice@example.com`
- **Result**: Rejected. Amber alert: *"Duplicate detected: The email address 'alice@example.com' is already registered."*

### Scenario 3: Attempting a Case-Insensitive Duplicate with Spaces
- **Name**: `Alice Impostor`
- **Email**: `  ALICE@EXAMPLE.COM  `
- **Result**: Rejected. Normalization detects collision with `alice@example.com`. No duplicate record inserted.

### Scenario 4: Entering an Invalid Email
- **Name**: `Bob Jones`
- **Email**: `notanemail`
- **Result**: Rejected. Red alert: *"Validation Error: 'notanemail' is not a valid email address format..."*

---

## ⚖️ Current Limitations & Future Improvements

### Current Limitations
- **Local SQLite Engine**: SQLite is ideal for development and single-instance deployments, but not suitable for multi-server, high-concurrency cloud clusters.
- **In-Memory Web Server**: Uses Flask's built-in development server; not intended for high-volume production traffic without a WSGI server (e.g., Gunicorn/Waitress).
- **No Pagination**: All stored records are rendered on a single page, which is efficient for moderate datasets but requires pagination for tens of thousands of records.

### Planned Future Improvements
- **Cloud Database Integration**: Transitioning storage to managed cloud databases such as PostgreSQL on AWS RDS or Google Cloud SQL.
- **Containerization**: Packaging the application into a Docker container (`Dockerfile` & `docker-compose.yml`) for portable deployment.
- **RESTful API Endpoints**: Exposing `/api/v1/records` with JSON payloads for external service integrations.
- **Search & Pagination**: Implementing client-side search filtering and server-side page chunking for large datasets.
- **Audit Logging**: Tracking deduplication events and rejection counts for analytics.

---

## 📄 License & Attribution

Developed as part of the **CodeAlpha Cloud Computing Internship** program (Task 1: Data Redundancy Removal System).  
Licensed under the [MIT License](https://opensource.org/licenses/MIT).
