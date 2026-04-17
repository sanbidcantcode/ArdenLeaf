# ArdenLeaf

> A unified book discovery and lending platform that connects libraries and bookstores into one seamless experience.

ArdenLeaf lets users search for books, check live availability across partner libraries and bookstores, borrow physical copies, track loans and fines, and save their favourite books and locations — all from a single portal. Library and store owners each get their own dedicated dashboard, and administrators can manage the whole network from the admin panel.

---

## Features

### For Members (Library Users)
- Search books by title, author, or genre across the entire network
- View book details enriched with cover art, descriptions, and ratings from the Google Books API
- Borrow available library copies directly from the platform (14-day loan period)
- View active loans, full history, and calculated overdue fines on a personal dashboard
- Bookmark books for later and manage them from a dedicated bookmarks page with genre filtering
- Save partner library/bookstore locations to a personal shortlist

### For Customers (Bookstore Users)
- Browse books available for purchase at partner bookstores with live pricing
- Save favourite store locations
- Bookmark books of interest

### For Library & Store Owners
- Dedicated `/owner` portal showing inventory health stats for their specific branch
- LibraryAdmins: view active loans, overdue status, and available/borrowed copy counts
- StoreAdmins: view available and sold copy counts with pricing summaries
- Add new books to the global catalogue and register physical copies at their branch

### For Admins
- Global `/admin` panel with system-wide stats (total books, active loans, members, locations)
- Add new libraries and bookstores to the network
- Register new book records and physical copies at any location
- View and monitor all active loans across all branches

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask 3.0.2 |
| Database | MySQL 8 |
| ORM / Queries | Raw SQL via `mysql-connector-python` 8.3.0 |
| Templates | Jinja2 (included with Flask) |
| Frontend | HTML5 + Vanilla CSS (no frameworks) |
| External API | Google Books API (cover art, descriptions, ratings) |
| Environment Config | `python-dotenv` 1.0.1 |

---

## Project Structure

```
ArdenLeaf/
├── app.py                  # App factory, blueprint registration, cache prewarming
├── config.py               # Configuration loaded from .env
├── requirements.txt
│
├── database/
│   ├── db.py               # MySQL connection helper
│   ├── schema.sql          # Full schema: all tables, views, constraints
│   └── seed_expanded.sql   # Sample data for development
│
├── models/
│   ├── book.py             # Book search, detail, availability, location inventory
│   ├── bookmark.py         # Add, remove, and list user bookmarks
│   ├── library.py          # Library and Bookstore listing + inventory
│   ├── loan.py             # Issue and return loans, fetch active/full history
│   ├── saved_location.py   # Save/unsave libraries and bookstores per user
│   └── user.py             # User creation, lookup, and profile updates
│
├── routes/
│   ├── auth_routes.py      # Login, register, location step, logout
│   ├── book_routes.py      # Search, book detail, bookmarks, locations
│   ├── loan_routes.py      # Member dashboard, borrow, return
│   ├── profile_routes.py   # Profile view/edit and quick stats
│   ├── owner_routes.py     # Owner portal (inventory + loan history per branch)
│   └── admin_routes.py     # Admin panel (global management)
│
├── utils/
│   ├── google_books.py     # Google Books API integration with ISBN + title/author fallback
│   └── book_cache.py       # Thread-safe disk cache for API responses (.book_cache.json)
│
└── templates/
    ├── index.html
    ├── auth.html
    ├── dashboard.html
    ├── search.html
    ├── book_detail.html
    ├── bookmarks.html
    ├── locations.html
    ├── location_detail.html
    ├── profile.html
    ├── admin/
    └── owner/
```

---

## Database Schema Overview

The schema (`database/schema.sql`) models a book lending / discovery network:

- **User** — Base table with five roles: `Member`, `Customer`, `Admin`, `LibraryAdmin`, `StoreAdmin`
- **Member / Customer** — Specialization tables (inherits from User)
- **LocationAdmin** — Maps LibraryAdmin/StoreAdmin users to exactly one Library or Bookstore
- **Book / Author / Publisher / Book_Genre / Book_Author** — Full book catalogue with many-to-many author and genre relationships
- **Library / Bookstore** — Two types of physical partner locations
- **BookCopy** — A physical instance of a book at a specific location (status: `Available`, `Borrowed`, `Sold`)
- **Loan** — Records of active and past borrowing by Members, linked to a BookCopy
- **Bookmark** — User-to-book saves with a unique constraint preventing duplicates
- **LoanFines (VIEW)** — Derived attribute: calculates overdue fines at $2.00/day automatically

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- MySQL 8.0 running locally

### 1. Clone and install dependencies

```bash
git clone https://github.com/sanbidcantcode/ArdenLeaf.git
cd ArdenLeaf
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example and fill in your MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ardenleaf
SECRET_KEY=your_secret_key_here
```

### 3. Initialize the database

Open your MySQL client and run:

```sql
source database/schema.sql
source database/seed_expanded.sql
```

### 4. Run the application

```bash
python app.py
```

Navigate to **http://127.0.0.1:5000**

---

## Test Accounts (from seed data)

| Role | Email | Password |
|---|---|---|
| Member | alice@example.com | hashed_pw_1 |
| Admin | admin@ardenleaf.com | admin_pass |
| LibraryAdmin | lib_admin@example.com | hashed_pw_la |
| StoreAdmin | store_admin@example.com | hashed_pw_sa |

> **Note:** Passwords are stored in plain text for this academic project. Do not use this in production.

---

## Key Flows

**Borrowing a book:** Search → View book detail → click Borrow on an available library copy → loan is created with a 14-day due date → status tracked in your dashboard.

**Returning a book:** Dashboard → click Return → loan is closed with today's date → copy becomes available again → any fine calculated by the `LoanFines` view disappears.

**Bookmarking:** Click the bookmark icon on any book (works from search, detail, and location pages) → toggle saved/unsaved with live UI feedback.

**Owner login:** LibraryAdmin or StoreAdmin logs in → system resolves their assigned branch from `LocationAdmin` → session stores branch name and type → redirected to `/owner/` dashboard scoped to their location only.

---

## Google Books API

On server startup, a background thread preloads cover art and metadata for every book in the database. All API responses are cached to `utils/.book_cache.json` (up to 500 entries) and persist across restarts. If an ISBN search returns no results, the system retries automatically using the book's title and author. When no data is available at all, the UI gracefully falls back to a placeholder cover.

---

## Academic Context

ArdenLeaf was built as a Database Systems course project. The schema intentionally demonstrates:

- Entity supertype/subtype (User → Member / Customer)
- Multivalued attributes (User_Phone, Book_Genre)
- Weak / dependent entities (BookCopy)
- Derived attributes via SQL views (LoanFines)
- Enforced application-level XOR constraints (BookCopy belongs to Library OR Bookstore, not both)
