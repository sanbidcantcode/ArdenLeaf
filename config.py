import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ardenleaf-dev-secret-key-123'
    # Default MySQL credentials (can be overridden by .env)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'ardenleaf'
    MYSQL_DB_PORT = os.environ.get('MYSQL_PORT') or 3306
