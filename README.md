# ArdenLeaf — Book Discovery & Library Management Platform

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.2-000000?style=flat&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)
![Werkzeug](https://img.shields.io/badge/Security-Werkzeug%20scrypt-brightgreen?style=flat)

A full-stack web application that connects multiple libraries and bookstores into a single unified platform. Users can discover books, check live inventory, borrow copies, track their loans and fines, and save their favourite locations — all from one place. Built with a multi-role authentication system and a normalized relational database designed from scratch.

---

## What It Does

ArdenLeaf solves the problem of fragmented library and bookstore discovery. Instead of visiting each branch individually, users search a single platform and instantly see which location has a copy available, whether it can be borrowed or purchased, and what the price or overdue fine is.

The platform supports five distinct user roles — each with their own interface and access controls — backed by a fully normalized MySQL schema that demonstrates core database design principles end-to-end.

---

## Features

### Members (Library Users)
- Search the entire book catalogue by title, author, or genre
- See real-time availability across all partner libraries
- Borrow physical copies with a 14-day loan period, tracked per copy
- View active loans, full borrowing history, and live overdue fine calculations
- Bookmark books and filter them by genre on a dedicated page
- Save favourite library and bookstore locations to a personal shortlist

### Customers (Bookstore Users)
- Browse available book inventory at partner stores with live pricing and discounts
- Save locations and bookmark books of interest

### Library & Store Owners
- Personal `/owner` dashboard scoped exclusively to their assigned branch
- Library owners: track available/borrowed copy counts, view active and overdue loans
- Store owners: track available/sold inventory with pricing summaries
- Add new books to the global catalogue and register physical copies at their location

### System Administrator
- Global `/admin` dashboard with network-wide statistics
- Register new libraries and bookstores into the network
- Add and assign book copies across any location
- Monitor all active loans across every branch

---

## Technical Highlights

- **Multi-role session-based auth** — five user types with route-level guards; LibraryAdmin/StoreAdmin sessions are automatically enriched with their assigned branch on login
- **Secure password handling** — all passwords hashed with Werkzeug's `scrypt`-based `generate_password_hash`; verified on login with `check_password_hash`
- **Normalized relational schema** — 15 tables including supertype/subtype user model, junction tables, multivalued attributes, and a SQL view for derived fine calculations
- **Google Books API integration** — enriches every book with cover art, descriptions, ratings, and page count; falls back to title+author search when ISBN yields no results
- **Persistent disk cache** — thread-safe JSON cache (`utils/.book_cache.json`, up to 500 entries) for API responses that survives server restarts
- **Cache prewarming** — background thread on startup fetches API data for all books in the database so users see covers immediately
- **Blueprint architecture** — six Flask blueprints keep auth, book discovery, loans, profiles, owner portal, and admin panel cleanly separated
- **AJAX-friendly endpoints** — bookmark and location-save routes detect `Accept: application/json` and respond accordingly for live UI updates without full page reloads

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.0.2 |
| Database | MySQL 8.0 |
| Query Layer | Raw SQL via `mysql-connector-python` 8.3.0 |
| Auth / Security | Werkzeug 3.0.1 (scrypt hashing) |
| Templating | Jinja2 |
| Frontend | HTML5, Vanilla CSS |
| External API | Google Books API |
| Config | `python-dotenv` 1.0.1 |

---

## Database Design

The schema (`database/schema.sql`) was designed from scratch to demonstrate relational database concepts:

| Concept | Implementation |
|---|---|
| Supertype / Subtype | `User` table with `Member` and `Customer` specialization tables |
| Multivalued Attributes | `User_Phone` and `Book_Genre` as separate tables |
| Many-to-Many | `Book_Author` junction table between `Book` and `Author` |
| Weak / Dependent Entity | `BookCopy` depends on both `Book` and either `Library` or `Bookstore` |
| Derived Attribute | `LoanFines` SQL view — calculates overdue fee ($2.00/day) dynamically |
| Application-enforced Constraint | `BookCopy` must belong to exactly one of Library or Bookstore (XOR), enforced at the application layer |
| Role-to-Location Mapping | `LocationAdmin` table links owner accounts to exactly one branch |

---

## Project Structure

```
ArdenLeaf/
├── app.py                   # App factory, blueprint registration, cache prewarming
├── config.py                # Environment-based configuration
├── requirements.txt
│
├── database/
│   ├── db.py                # MySQL connection helper
│   ├── schema.sql           # Complete schema: tables, views, constraints
│   └── seed_expanded.sql    # Sample data: 9 users, 20 books, 5 libraries, 4 bookstores
│
├── models/
│   ├── book.py              # Search, detail, availability, location inventory
│   ├── bookmark.py          # Bookmark toggle and user bookmark listing
│   ├── library.py           # Library and Bookstore listing + inventory
│   ├── loan.py              # Issue/return loans, active and full history
│   ├── saved_location.py    # Save/unsave locations per user
│   └── user.py              # Registration, lookup, profile updates
│
├── routes/
│   ├── auth_routes.py       # Login, register, post-registration location step, logout
│   ├── book_routes.py       # Search, book detail, bookmarks, location pages
│   ├── loan_routes.py       # Member dashboard, borrow, return
│   ├── profile_routes.py    # Profile view/edit, quick stats
│   ├── owner_routes.py      # Branch-scoped owner portal
│   └── admin_routes.py      # Global admin panel
│
├── utils/
│   ├── google_books.py      # Google Books API with ISBN + title/author fallback
│   └── book_cache.py        # Thread-safe persistent disk cache
│
└── templates/               # Jinja2 templates (includes /admin and /owner subdirs)
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- MySQL 8.0

### 1. Clone the repository

```bash
git clone https://github.com/sanbidcantcode/ArdenLeaf.git
cd ArdenLeaf
```

### 2. Set up the Python environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your MySQL credentials:

```
SECRET_KEY=your_secret_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=ardenleaf
MYSQL_PORT=3306
```

### 4. Initialize and seed the database

In your MySQL client:

```sql
source database/schema.sql
source database/seed_expanded.sql
```

### 5. Run the application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Deploying To Railway

This project is Railway-ready and already includes [railway.toml](D:/Projects%20of%20Coding/Database%20Project/ArdenLeaf/railway.toml) with this start command:

```toml
[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT \"app:create_app()\""
```

### 1. Create the Railway project

1. Push this repository to GitHub.
2. In Railway, create a new project.
3. Add two services:
   - a GitHub-backed service for this Flask app
   - a MySQL service

### 2. Set application variables

In the Flask service, set:

```env
SECRET_KEY=generate-a-long-random-secret
```

You do not need to manually rename Railway's MySQL variables. Railway provides `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, and `MYSQLPORT`, and the app now supports those names directly.

### 3. Initialize the database

After the MySQL service is created, run the SQL files against that Railway database:

```sql
source database/schema.sql
source database/seed_expanded.sql
```

You can do this from:
- a local MySQL client connected to Railway's MySQL public TCP proxy, or
- Railway's MySQL service shell if you prefer a project-local workflow

### 4. Generate a public domain

In the Flask service:
1. Open `Settings`
2. Open `Networking`
3. Click `Generate Domain`

### 5. Redeploy and verify

Once variables and schema are in place, redeploy the Flask service and confirm:
- home page loads
- `/auth` works
- book search loads data
- login works for a seeded account

### Notes

- The app uses MySQL, so deployment is not complete until the schema is loaded.
- The Google Books integration calls an external API at runtime; if that API is slow or rate-limits, the app still runs but some enrichment fields may be empty.

---

## Test Accounts

All passwords are stored as `scrypt` hashes in the database. The seed provides accounts for every role:

| Role | Email | Password |
|---|---|---|
| Member | alice@example.com | hashed_pw_1 |
| Member | bob@example.com | hashed_pw_2 |
| Customer | charlie@example.com | hashed_pw_3 |
| Customer | diana@example.com | hashed_pw_4 |
| Admin | admin@ardenleaf.com | admin123 |
| LibraryAdmin — Connaught Place | lib1@ardenleaf.com | libpass1 |
| LibraryAdmin — Bandra | lib2@ardenleaf.com | libpass2 |
| StoreAdmin — Footnotes, Bangalore | store1@ardenleaf.com | storepass1 |
| StoreAdmin — The Margin, Delhi | store2@ardenleaf.com | storepass2 |

---

## Key User Flows

**Borrowing a book**
Search or browse a location → open book detail → click Borrow on an available library copy → a `Loan` record is created with a 14-day due date and the `BookCopy` status is set to `Borrowed`.

**Returning a book**
Open the Member dashboard → click Return → `ReturnDate` is written to the `Loan` record → `BookCopy` status resets to `Available` → the `LoanFines` view stops accruing.

**Owner dashboard**
LibraryAdmin or StoreAdmin logs in → auth layer queries `LocationAdmin` to resolve their branch → session is populated with branch name, ID, and type → the `/owner` dashboard renders inventory and loan data filtered to that branch only.

**Bookmarking**
Click the bookmark icon on any book page → the route checks `Bookmark.is_bookmarked()` and either inserts or deletes the row → the UI updates live via JSON response without a page reload.

---

## License

MIT
