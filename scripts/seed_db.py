import mysql.connector
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to reach config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def seed():
    load_dotenv()
    
    # Establish connection using the same config as the main app
    print(f"Connecting to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_DB_PORT} as {Config.MYSQL_USER}...")
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_DB_PORT
        )
        cursor = connection.cursor()
        
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'seed_data.sql')
        print(f"Reading SQL from {sql_file_path}...")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            full_sql = f.read()
            
        # Split by ';' but only if it's not inside a string (overly simplified version)
        # Better: split manually and handle the multi-line inserts
        statements = full_sql.split(';')
        
        print(f"Executing {len(statements)} statements...")
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue
            
            try:
                cursor.execute(statement)
                if i % 10 == 0:
                    print(f"Executed {i} statements...")
            except Exception as se:
                print(f"Error on statement {i}:")
                print(statement)
                print(se)
                raise se
                
        connection.commit()
        print("Success! Database has been re-seeded.")
        
    except Exception as e:
        print(f"MAJOR ERROR: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    seed()
