# ArdenLeaf - Centralized Book Discovery Platform

ArdenLeaf connects multiple libraries and bookstores into a single platform. It allows users to search for books, check availability, borrow library books, and track their loans and overdue fines.

## Project Architecture

Backend: Python + Flask
Database: MySQL
Frontend: HTML5 + Modern Vanilla CSS (Jinja Templates)

## Setup & Run Instructions

### 1. Database Initialization
Ensure you have a local MySQL server running.
1. Open your MySQL client and run the queries inside `database/schema.sql` to create the database and tables.
2. Run the queries inside `database/seed_data.sql` to populate it with sample users, books, and loans.

### 2. Python Environment Setup
1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Database Configuration:
   You can either set environment variables or edit `config.py` to match your local MySQL credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`). By default, it expects a local server with `root` and an empty password.

### 3. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 4. Access the Application
Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Testing Core Features
- **Login**: You can log in using `alice@example.com` with password `hashed_pw_1` (Alice is a Member).
- **Search**: Try searching for "Fantasy" or "Harry Potter" in the search bar.
- **Borrowing**: Viewing a book detail will show its availability across libraries and bookstores. As a member, you can borrow available library copies.
- **Fines**: Go to "My Loans" to see active loans. The seed data includes an overdue loan for Alice which will display a calculated fine amount.
