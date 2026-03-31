# STACK: ArdenLeaf Technical Stack Definition

## Core Technologies
- **Backend Language**: Python
- **Backend Framework**: Flask
- **Database**: MySQL (Community Edition)
- **Frontend Language**: HTML5, Vanilla CSS
- **Template Engine**: Jinja (part of Flask)

## Primary Libraries & Versions
- **Flask**: 3.0.2 (Web application development)
- **mysql-connector-python**: 8.3.0 (MySQL database interaction)
- **python-dotenv**: 1.0.1 (Environment variable management)
- **Werkzeug**: 3.0.1 (WSGI utility library)

## Database Schema Structure
- **Users**: User profiles, roles (Member/Admin), authentication details.
- **Books**: Title, author, ISBN, and metadata for book entries.
- **Libraries/Bookstores**: Location, name, contact info, and role (Library/Bookstore).
- **Loans**: Borrowing records, due dates, return status, and associated fines.

## Development & Deployment Environment
- **Development Editor**: Interactive coding environment (e.g., VS Code + Antigravity)
- **Local Development Server**: Flask internal dev server
- **Database Server**: Local MySQL instance
- **Environment Configuration**: `.env` or `config.py` for backend settings.
- **Dependency Management**: `requirements.txt` used for Python package installation.
- **Version Control**: Git-based system for development and tracking.
