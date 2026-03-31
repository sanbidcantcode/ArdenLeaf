# ARCHITECTURE: ArdenLeaf System Overview

## System Components

### 1. User Interface (Frontend)
- **Technology**: HTML5, Vanilla CSS, Jinja Templates (Python Flask)
- **Role**: Provides the user-facing interface for searching, browsing, and managing books and loans.
- **Interactions**: Sends requests to the backend via HTTP routes and renders dynamic content from templates.

### 2. Backend (Application Logic)
- **Technology**: Python, Flask
- **Role**: Handles application logic, processes user requests, interacts with the database, and returns dynamic content to the frontend.
- **Blueprints**: Organized into `auth_bp`, `book_bp`, and `loan_bp` for modular routing.
- **Models**: Defines structured data models (Book, Library, Loan, User) for interacting with the database.

### 3. Database Layer (Structured Storage)
- **Technology**: MySQL
- **Role**: Stores persistent data including users, books, libraries, bookstores, loans, and related metadata.
- **Schema**: Defined in `database/schema.sql` with tables for `Users`, `Books`, `Libraries`, `Bookstores`, `Loans`.
- **Seed Data**: Populated during initialization using `database/seed_data.sql`.

## System Flow

1. **User Request**: A user interacts with the frontend (e.g., search query, login, borrow request).
2. **Routing**: The Flask backend receives the request and directs it to the appropriate route (e.g., `book_routes.py`, `auth_routes.py`).
3. **Logic Processing**: The backend logic processes the request, interacting with the database through model methods (e.g., `Book.search()`).
4. **Data Interaction**: The database layer (MySQL) executes queries and returns the results to the models.
5. **Template Rendering**: The Flask backend uses the retrieved data to render Jinja templates (e.g., `search.html`, `book_detail.html`).
6. **User Response**: The rendered HTML content is returned to the user's browser for display.

## Dependency Graph
- **Flask** (Web Framework)
- **MySQL-connector-python** (Database Driver)
- **python-dotenv** (Environment Configuration)
- **Werkzeug** (WSGI Utility Library)
