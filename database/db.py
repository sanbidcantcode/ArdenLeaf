import mysql.connector
from flask import current_app

def get_db_connection():
    config = current_app.config
    connection = mysql.connector.connect(
        host=config['MYSQL_HOST'],
        user=config['MYSQL_USER'],
        password=config['MYSQL_PASSWORD'],
        database=config['MYSQL_DB'],
        port=config['MYSQL_DB_PORT']
    )
    return connection
