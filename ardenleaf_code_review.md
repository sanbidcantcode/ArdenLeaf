# ArdenLeaf — Technical Code Review
**Perspective:** Senior software engineer / junior dev hiring evaluation  
**Verdict:** Solid foundation with meaningful gaps. Fix the items in Section 1 before showing this to anyone.

---

## 1. SECURITY ISSUES

### 🔴 Critical

**No CSRF protection anywhere.**  
Every form that mutates state — borrowing books (`/loans/borrow`), returning books (`/loans/return/<id>`), editing a profile (`/profile`), toggling bookmarks — is wide open to Cross-Site Request Forgery. Flask has `flask-wtf` which adds CSRF tokens in one line. Without it, any malicious website can silently trigger actions on behalf of a logged-in user. This is table-stakes for any web application and its absence will be flagged immediately.

**Admin and Owner auth guards are trivially bypassable via `before_request`.**  
`routes/admin_routes.py:6` and `routes/owner_routes.py:7` both use `@bp.before_request` to enforce role checks. The pattern itself is fine, but `before_request` does **not** fire for Flask static files. More critically, if someone adds a new route to those blueprints and forgets how `before_request` works (e.g. during refactoring), the guard disappears silently. The professional pattern is a `@login_required` / `@role_required` decorator applied explicitly per route. This makes auth intent visible and auditable.

**The `admin/loans` route (`admin_routes.py:179`, line 196) uses `JOIN Libraries` without a `LEFT JOIN`, silently dropping all loans for bookstore copies.**  
This is a data correctness bug that looks like a security gap if an admin is making decisions based on what they see. The dashboard version at line 48 uses `LEFT JOIN Libraries` correctly, but the `/admin/loans` page does not.

### 🟠 Moderate

**Session does not expire. No `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, or `SESSION_COOKIE_SAMESITE` settings in `config.py`.**  
These three flags should be set for any deployed app:
```python
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # Inaccessible to JS
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF mitigation
PERMANENT_SESSION_LIFETIME = 3600 # 1-hour expiry
```
Without them, session cookies are vulnerable in transit and to XSS.

**No input validation on profile update (`profile_routes.py:52–57`).**  
`name`, `email`, and `phone` are stripped but never validated. A recruiter will ask: what happens if someone submits an empty name? An invalid email? A 10,000-character string? `User.update_profile` blindly passes whatever it receives to the DB query. Minimum: check email format with a regex, enforce max lengths, reject blank names.

**No ISBN validation before database writes (`admin_routes.py:86`, `owner_routes.py:102`).**  
`isbn` comes directly from form data and is written to the DB after only a `.strip()`. An attacker (or a typo) can insert garbage ISBNs. A basic 10/13-digit format check would catch 99% of issues.

---

## 2. CODE QUALITY ISSUES

### `models/library.py` — Two classes doing nearly identical things
`Library` and `Bookstore` are structurally identical: `get_all()` and `get_inventory()`. This cries out for a single `Location` base class or a factory function. As-is, any change to the query pattern needs to be made twice and has already caused bugs (the `Library`→`Libraries` rename was manually applied to both).

### `auth_routes.py:28–56` — Login handler opens 3 separate DB connections for one request
For admin/owner login, the code opens `conn2` then closes it, then opens `conn3` then closes it. There's no reason to do this — use one connection and two cursor executes. Three round-trips to the database for a single login is measurably slow.

### `profile_routes.py:147` — `import json` inside a function
```python
import json
return render_template(...)
```
All imports belong at the top of the file. This is a style violation, not a runtime error, but it reads as inexperience. Same applies to `book_routes.py:135` (`from models.book import Book` inside a function after already importing it at the top of the file).

### `profile_routes.py:157–160` — Dead route with placeholder comments
```python
# For now, we'll just show the locations page or a placeholder
# In a real app we might fetch user-specific saved locations.
# We will reuse the locations logic or just redirect to books.libraries_list
return redirect(url_for('books.libraries_list'))
```
This route (`/saved-locations`) exists, redirects somewhere else, and has three comment lines explaining what a real implementation would look like. Either implement it or delete it. Placeholder comments like "in a real app" are exactly the kind of thing that gets you asked hard questions in interviews.

### `loan_routes.py:40` — Cross-blueprint import for a shared utility
```python
from routes.profile_routes import get_quick_stats
```
Importing a function from another routes module is a circular dependency waiting to happen and signals poor separation of concerns. `get_quick_stats` belongs in a service layer or its own utility module (e.g. `utils/stats.py`), not in `profile_routes`.

### `admin_routes.py:14–15` — Two cursors opened on the same connection
```python
cursor = conn.cursor()
...
db_cursor = conn.cursor(dictionary=True)
```
Two cursors open simultaneously on one connection. This works with `mysql-connector-python` but is confusing and unnecessary. Open one dictionary cursor, use it everywhere.

### `models/library.py` — No try/except on `get_all()`
`Library.get_all()` and `Bookstore.get_all()` have no error handling whatsoever. If the DB is down, these raise uncaught exceptions that bubble up to the user as a 500 with a traceback. Every other model handles this correctly — library.py is the odd one out.

### Inconsistent `print()` vs logging
`bookmark.py` uses `print(f"[bookmark] add error: {e}")`, `google_books.py` uses `print(f"[google_books] ...")`. These are good structured-format prints, but they should use Python's `logging` module. `print()` to stdout in production means these messages vanish or get mixed with Gunicorn's access logs. `logging.getLogger(__name__)` is the correct approach and is what any production codebase uses.

---

## 3. DATABASE DESIGN ISSUES

### `SavedLocation.LocationID` has no foreign key
`schema.sql:149–157`: `SavedLocation.LocationID` is a plain `INT`, not a foreign key to either `Libraries` or `Bookstores`. This is a deliberate trade-off (the comment in `BookCopy` makes the same note about XOR constraints), but it means the DB will happily store `LocationID = 999999` with no referential integrity check. This could be solved with a trigger or with two nullable FKs and a CHECK constraint. Even noting it in the schema comment would be better than leaving it silent.

### No indexes on the most-queried columns
Missing indexes that would noticeably affect performance at scale:
- `Loan(MemberID)` — every dashboard load does a full table scan on Loan filtered by MemberID
- `Loan(ReturnDate)` — every active-loan query filters on this
- `Bookmark(UserID)` — every bookmark check/list does a full scan
- `BookCopy(LibraryID)`, `BookCopy(StoreID)` — queried in nearly every book availability check

For a student project the tables are small and it won't matter. But a recruiter will ask "what happens when there are 100,000 loans?".

### `BookCopy` XOR constraint is fully unenforced at the database level
The comment says it's enforced at the application level, which is honest. But there's nothing stopping a direct SQL insert from creating a copy with both `LibraryID` and `StoreID` set, or neither. MySQL 8.0.16+ supports `CHECK` constraints:
```sql
CHECK (
    (LibraryID IS NOT NULL AND StoreID IS NULL) OR
    (LibraryID IS NULL AND StoreID IS NOT NULL)
)
```
This is a known limitation you've documented — mention it in your README as a technical decision.

### `LoanFines` is a VIEW, not a table — fine amounts can't be "paid"
The schema correctly uses a derived view for fines (calculated from due dates). But the `profile_routes.py` code has a comment noting there's no `FinePaid` field. If fines are ever meant to be settled, the view approach breaks down — you'd need a `FinePaid` boolean or a separate `Payment` table. The current design works as read-only, but the domain model is incomplete.

### Skipped number in schema comments
Comments go `-- 3. Specialization: Member` then jump to `-- 5. Publisher`. The `Customer` table (comment `4.`) was removed but the numbering wasn't fixed. Minor, but shows the schema was modified without cleanup.

---

## 4. THINGS THAT LOOK UNPROFESSIONAL

**`profile_routes.py:157–160` — Comments that expose unfinished thinking**
Already noted above. A recruiter looking at this code will see "in a real app" and think: "This is not a real app."

**`admin_routes.py:210` — Bare `except Exception as e: print(e)`**
```python
except Exception as e:
    print(e)
    loans = []
```
Silencing an exception with a bare print and returning an empty list means a broken DB query shows the admin an empty loans list with no indication anything is wrong. At minimum, flash an error message.

**`requirements.txt` has no pinned transitive dependencies**
Pinning only 6 top-level packages is correct for a portfolio project. This is fine — just be ready to explain it in an interview.

**`import json` inside a route function (`profile_routes.py:147`)**
Already flagged under Code Quality. In an interview context, this will be the first thing a reviewer notices.

**Three `print()` calls in routes** (`admin_routes.py:210`, `profile_routes.py:38`, `profile_routes.py:142`) that produce no useful output format. Using `print(e)` where `e` is an Exception gives you the error string but no stack trace and no file/line context.

---

## 5. MISSING BEST PRACTICES

### Missing: Rate limiting on auth endpoints
`/auth` (POST) is completely open to brute-force attacks. No rate limiting, no account lockout, no CAPTCHA. For production, `Flask-Limiter` with `@limiter.limit("5 per minute")` on the auth route is the minimum expectation.

### Missing: Password change functionality
The profile page lets users update name, email, and phone — but not their password. Users cannot change their own password. This is a fundamental account management feature.

### Missing: Proper HTTP status codes on error returns
`book_routes.py:62`:
```python
return "Book not found", 404
```
This is correct. But `admin_routes.py:10` and `owner_routes.py:11` return redirects on unauthorized access instead of 403. A redirect to the homepage for an unauthorized request is user-friendly, but it masks the actual error from API consumers or monitoring tools.

### Missing: `PERMANENT_SESSION_LIFETIME` and session refresh
Sessions created at login never expire. A user who closes their browser retains their session indefinitely (until the server restarts or the `SECRET_KEY` changes).

### Missing: Gunicorn workers config in `railway.toml`
```toml
startCommand = "gunicorn --bind 0.0.0.0:$PORT \"app:create_app()\""
```
No `--workers` flag means Gunicorn defaults to 1 synchronous worker. Under any real load, requests queue. The standard formula is `2 * CPU_cores + 1`. For Railway's smallest instance: `--workers 3`.

### Missing: `__init__.py` in database/ and routes/
`utils/` has an `__init__.py`. `routes/` and `database/` don't, which means they're not proper packages. It works because Flask's import magic resolves them, but it's inconsistent and breaks some static analysis tools.

---

## 6. GENUINE STRENGTHS

**The model layer is properly separated and consistent.**  
Every model (`bookmark.py`, `saved_location.py`, `loan.py`, `book.py`) follows the same pattern: `conn = cursor = None`, try/finally with explicit closes, parameterized queries, meaningful error returns. No SQL injection risk anywhere — 100% of queries use `%s` placeholders. This shows real understanding of database safety, and a recruiter will notice.

**Werkzeug password hashing is used correctly.**  
`auth_routes.py:92` uses `generate_password_hash(password)` and `check_password_hash(user['PasswordHash'], password)` at line 23. Passwords are never stored in plaintext. This is the right answer and correctly uses Werkzeug's `pbkdf2:sha256` scheme by default.

**The API/form dual-response pattern is well implemented.**  
The `wants_json` detection in `book_routes.py:84–86`, `loan_routes.py:118`, and `profile_routes.py:62` is a genuinely good pattern. The same route handles both AJAX and form submissions cleanly. This shows understanding of progressive enhancement.

**`utils/book_cache.py` is production-quality.**  
Thread-safe with a `threading.Lock`, graceful degradation on corrupt cache files, capped at `MAX_ENTRIES`, survives server restarts. This is far above the level most junior developers would write.

**`config.py` — The `_env()` fallback function is clean.**  
Supporting both `MYSQL_HOST` and `MYSQLHOST` (Railway's naming) through a single utility function is thoughtful. It shows awareness of deployment environment differences.

**The LoanFines view is architecturally sound.**  
Handling fines as a derived view rather than computing them in Python on every request shows understanding of pushing computation to the database layer where it belongs.

**`schema.sql` is the most impressive file in the project.**  
Correct use of `ON DELETE CASCADE` vs `ON DELETE SET NULL` throughout. The `BookCopy` design (nullable LibraryID/StoreID with comments explaining the XOR decision) and the inline comment about MySQL 8.0 CHECK constraint limitations shows research and intentional design, not just copying a tutorial schema. For a student project, this is genuinely strong.

---

## Summary Table

| Area | Rating | Key Issue |
|---|---|---|
| Security | ⚠️ Needs Work | No CSRF, no session flags, no rate limiting |
| Code Quality | ✅ Good | Minor: in-function imports, cross-blueprint import |
| Database | ✅ Strong | No indexes, SavedLocation FK gap |
| Professionalism | ⚠️ Needs Work | Placeholder comments, bare `print(e)` |
| Best Practices | ⚠️ Needs Work | No password change, no session expiry |
| Strengths | ✅ Standout | Schema design, cache layer, parameterized queries, dual-response pattern |

**Bottom line for a junior position:** The backend architecture and database design are better than average for a student project. The security gaps (CSRF above all else) are the only things that would stop this from making it past a technical screen. Fix CSRF, add session cookie flags, delete the placeholder comment in `saved_locations`, and this becomes a strong portfolio piece.
