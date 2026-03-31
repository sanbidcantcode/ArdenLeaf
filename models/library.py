from database.db import get_db_connection

class Library:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Library")
        libraries = cursor.fetchall()
        cursor.close()
        conn.close()
        return libraries

    @staticmethod
    def get_inventory(library_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT bc.CopyID, bc.Status, b.Title, b.ISBN 
            FROM BookCopy bc
            JOIN Book b ON bc.ISBN = b.ISBN
            WHERE bc.LibraryID = %s
        """
        cursor.execute(sql, (library_id,))
        inventory = cursor.fetchall()
        cursor.close()
        conn.close()
        return inventory

class Bookstore:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Bookstore")
        stores = cursor.fetchall()
        cursor.close()
        conn.close()
        return stores

    @staticmethod
    def get_inventory(store_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT bc.CopyID, bc.Status, b.Title, b.ISBN 
            FROM BookCopy bc
            JOIN Book b ON bc.ISBN = b.ISBN
            WHERE bc.StoreID = %s
        """
        cursor.execute(sql, (store_id,))
        inventory = cursor.fetchall()
        cursor.close()
        conn.close()
        return inventory
