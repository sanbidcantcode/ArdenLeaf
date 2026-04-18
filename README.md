# ArdenLeaf

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-9.4-orange?logo=mysql&logoColor=white) ![Railway](https://img.shields.io/badge/Deployed-Railway-purple?logo=railway&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green)

> A centralized book discovery and library management platform built for India's independent libraries and bookstores.

**Live:** https://ardenleaf-production.up.railway.app

---

## Overview

ArdenLeaf connects multiple libraries and bookstores into a single platform. Users can discover books, check real-time availability across partner locations, borrow from libraries, and track their reading history — all from one place.

The platform supports three distinct user roles: regular members, per-location library/bookstore owners, and a global super-admin.

---

## Screenshots

> Visit the [live demo](https://ardenleaf-production.up.railway.app) to explore the platform. Sample accounts are provided below.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL |
| Frontend | Jinja2, Tailwind CSS |
| External API | Google Books API |
| Deployment | Railway |

---

## Try the Live Demo

No installation required — the app is deployed and ready to use.

Log in with one of these pre-seeded accounts to explore the platform without registering:

| Role | Email | Password |
|---|---|---|
| Admin | admin@ardenleaf.com | admin123 |
| Library Owner 1 | lib1@ardenleaf.com | libpass1 |
| Library Owner 2 | lib2@ardenleaf.com | libpass2 |
| Bookstore Owner 1 | store1@ardenleaf.com | storepass1 |
| Bookstore Owner 2 | store2@ardenleaf.com | storepass2 |
| Member | Register a new account | — |

**Admin** can manage the global book catalog, add locations, and monitor all active loans across the platform.

**Library Owner** gets a scoped portal showing only their location's inventory, borrow history, and copy management.

**Member** can search books, check availability, borrow from libraries, bookmark titles, and track loans and fines from a personal dashboard.

---

## Key Features

- ✅ Full-text book search with Google Books API integration — cover images, descriptions, ratings, and page counts fetched automatically with disk-based caching to stay within API rate limits
- ✅ Real-time availability across all partner libraries and bookstores, with per-copy status tracking (Available / Borrowed / Sold)
- ✅ Borrow and return flow with 14-day loan periods and automatic overdue fine calculation (₹2/day)
- ✅ Bookmark system with genre filtering, availability filtering, and live search
- ✅ Member dashboard with active loan cards, borrowing history modal, and fines overview
- ✅ Per-location owner portal scoped by session — owners only see their own data
- ✅ Super-admin panel with clickable stat cards that expand into live data tables
- ✅ Saved locations system for users to follow their preferred libraries and bookstores
- ✅ CSRF protection on all forms and AJAX requests via Flask-WTF

---

## Database Design

15 tables with a specialization pattern for user types (Member, Admin, LibraryAdmin, StoreAdmin). Key design decisions:

- `BookCopy` separates physical inventory from the book catalog — one ISBN can have many copies across many locations
- `LoanFines` is a MySQL VIEW that derives fine amounts from due dates rather than storing them, keeping the data model clean
- `LocationAdmin` links owner accounts to exactly one library or bookstore, enforced at the application layer
- All queries use parameterized statements — no raw string interpolation

---

## Architecture

The app follows a Blueprint-based modular structure with a clear separation between routes, models, and utilities.

```
ArdenLeaf/
├── app.py               # App factory, blueprint registration
├── config.py            # Environment-based configuration
├── routes/              # Flask blueprints (auth, books, loans, admin, owner, profile)
├── models/              # Database access layer (parameterized queries only)
├── utils/               # Google Books API client, disk cache
├── templates/           # Jinja2 templates (standalone pages + admin/owner subdirs)
├── database/            # Schema and seed SQL files
└── static/              # CSS
```

---

## Security

- CSRF protection on all forms and AJAX requests via Flask-WTF
- Passwords hashed with Werkzeug's PBKDF2-SHA256 — never stored in plaintext
- Session cookies configured with HttpOnly, SameSite=Lax, and Secure flags
- All database queries use parameterized statements — no raw string interpolation
- Role-based access control enforced at the blueprint level via before_request guards

---

## Local Setup

```bash
git clone https://github.com/sanbidcantcode/ArdenLeaf.git
cd ArdenLeaf
pip install -r requirements.txt
```

Create a `.env` file:
```
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DB=
MYSQL_PORT=
SECRET_KEY=
```

Run the schema and seed files against your MySQL instance, then:

```bash
python app.py
```

---

## Known Limitations & Next Steps

- Bookstore purchase flow is UI-only — no payment integration
- No rate limiting on auth endpoints (Flask-Limiter planned)
- Google Books API coverage varies by ISBN; title/author fallback search is used when needed
- Database indexes on high-query columns (Loan.MemberID, Bookmark.UserID) would be added before scaling

---

Built by [Sanbid](https://github.com/sanbidcantcode) · [Live Demo](https://ardenleaf-production.up.railway.app) · [GitHub](https://github.com/sanbidcantcode/ArdenLeaf)
