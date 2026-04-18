import os
from dotenv import load_dotenv

load_dotenv()


def _env(*keys, default=None):
    """Return the first non-empty environment variable from the given keys."""
    for key in keys:
        value = os.environ.get(key)
        if value not in (None, ''):
            return value
    return default


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ardenleaf-dev-secret-key-change-in-prod')
    # Supports both local .env names and Railway's built-in MySQL variables.
    MYSQL_HOST = _env('MYSQL_HOST', 'MYSQLHOST')
    MYSQL_USER = _env('MYSQL_USER', 'MYSQLUSER')
    MYSQL_PASSWORD = _env('MYSQL_PASSWORD', 'MYSQLPASSWORD')
    MYSQL_DB = _env('MYSQL_DB', 'MYSQLDATABASE')
    MYSQL_DB_PORT = int(_env('MYSQL_PORT', 'MYSQLPORT', default=3306))
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
