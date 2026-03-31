"""
scripts/refresh_db.py

Drops and recreates the entire ardenleaf database from schema.sql + seed_data.sql.
Uses mysql.connector's multi=True for proper multi-statement execution.
"""

import mysql.connector
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def run_sql_file(cursor, filepath):
    """Execute an entire .sql file using multi-statement mode."""
    print(f"\n--- Running {os.path.basename(filepath)} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    results = cursor.execute(sql, multi=True)
    count = 0
    for result in results:
        count += 1
        if result.with_rows:
            result.fetchall()

    print(f"   Done: {count} statements executed.")


def main():
    load_dotenv()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(base_dir, 'database', 'schema.sql')
    seed_path   = os.path.join(base_dir, 'database', 'seed_data.sql')

    print(f"Connecting to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_DB_PORT} as {Config.MYSQL_USER}...")

    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        port=Config.MYSQL_DB_PORT,
    )
    cursor = connection.cursor()

    try:
        # Step 0: Nuke the database completely and recreate it
        print("\nStep 0: Dropping and recreating database...")
        cursor.execute("DROP DATABASE IF EXISTS ardenleaf")
        cursor.execute("CREATE DATABASE ardenleaf")
        connection.commit()
        print("   Done: Database dropped and recreated.")

        # Step 1: Run schema (creates all tables fresh)
        run_sql_file(cursor, schema_path)
        connection.commit()

        # Step 2: Run seed data (no truncate conflicts since tables are fresh)
        run_sql_file(cursor, seed_path)
        connection.commit()

        # Step 3: Verify
        cursor.execute("SELECT COUNT(*) FROM ardenleaf.Book")
        book_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ardenleaf.BookCopy")
        copy_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ardenleaf.Author")
        author_count = cursor.fetchone()[0]

        print(f"\n========================================")
        print(f"  DATABASE REFRESHED SUCCESSFULLY!")
        print(f"     Books:   {book_count}")
        print(f"     Authors: {author_count}")
        print(f"     Copies:  {copy_count}")
        print(f"========================================")
        print(f"\nRefresh your browser at http://127.0.0.1:5000/search")

    except mysql.connector.Error as e:
        print(f"\nMySQL Error: {e}")
        print(f"   Error code: {e.errno}")
        print(f"   SQL State:  {e.sqlstate}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
