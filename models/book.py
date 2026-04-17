from database.db import get_db_connection

class Book:
    @staticmethod
    def search(query=None):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    b.ISBN, b.Title, b.PublicationYear,
                    p.Name AS PublisherName,
                    GROUP_CONCAT(DISTINCT a.Name SEPARATOR ', ') AS Authors,
                    GROUP_CONCAT(DISTINCT bg.Genre SEPARATOR ', ') AS Genres
                FROM Book b
                LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
                LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN
                LEFT JOIN Author a ON ba.AuthorID = a.AuthorID
                LEFT JOIN Book_Genre bg ON b.ISBN = bg.ISBN
            """
            params = []
            if query:
                sql += " WHERE b.Title LIKE %s OR a.Name LIKE %s OR bg.Genre LIKE %s"
                like_q = f"%{query}%"
                params.extend([like_q, like_q, like_q])
                
            sql += " GROUP BY b.ISBN"
            
            cursor.execute(sql, tuple(params))
            books = cursor.fetchall()
            return books
        except Exception as e:
            print(f"Error searching books: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_by_isbn(isbn):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    b.ISBN, b.Title, b.PublicationYear,
                    p.Name AS PublisherName,
                    GROUP_CONCAT(DISTINCT a.Name SEPARATOR ', ') AS Authors,
                    GROUP_CONCAT(DISTINCT bg.Genre SEPARATOR ', ') AS Genres
                FROM Book b
                LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
                LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN
                LEFT JOIN Author a ON ba.AuthorID = a.AuthorID
                LEFT JOIN Book_Genre bg ON b.ISBN = bg.ISBN
                WHERE b.ISBN = %s
                GROUP BY b.ISBN
            """
            cursor.execute(sql, (isbn,))
            book = cursor.fetchone()
            return book
        except Exception as e:
            print(f"Error fetching book by ISBN: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_availability(isbn):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    bc.CopyID, bc.Status,
                    l.Name AS LibraryName,
                    s.Name AS StoreName
                FROM BookCopy bc
                LEFT JOIN Library l ON bc.LibraryID = l.LibraryID
                LEFT JOIN Bookstore s ON bc.StoreID = s.StoreID
                WHERE bc.ISBN = %s
            """
            cursor.execute(sql, (isbn,))
            copies = cursor.fetchall()
            return copies
        except Exception as e:
            print(f"Error fetching book availability: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_books_at_location(location_id, location_type):
        """
        Return all books that have at least one copy at the given library or bookstore,
        grouped by book with the copy's status and CopyID.
        location_type: 'Library' or 'Bookstore'
        """
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            if location_type == 'Library':
                id_col = 'bc.LibraryID'
            else:
                id_col = 'bc.StoreID'

            sql = f"""
                SELECT
                    b.ISBN, b.Title, b.PublicationYear,
                    GROUP_CONCAT(DISTINCT a.Name ORDER BY a.Name SEPARATOR ', ') AS Authors,
                    GROUP_CONCAT(DISTINCT bg.Genre ORDER BY bg.Genre SEPARATOR ', ') AS Genres,
                    p.Name AS PublisherName,
                    MIN(bc.CopyID) AS CopyID,
                    MAX(CASE WHEN bc.Status = 'Available' THEN 1 ELSE 0 END) AS is_available,
                    SUM(CASE WHEN bc.Status = 'Available' THEN 1 ELSE 0 END) AS available_copies,
                    SUM(CASE WHEN bc.Status = 'Borrowed' THEN 1 ELSE 0 END) AS borrowed_copies,
                    COUNT(bc.CopyID) AS total_copies,
                    bc.Price, bc.DiscountPercent
                FROM BookCopy bc
                JOIN Book b ON bc.ISBN = b.ISBN
                LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
                LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN
                LEFT JOIN Author a ON ba.AuthorID = a.AuthorID
                LEFT JOIN Book_Genre bg ON b.ISBN = bg.ISBN
                WHERE {id_col} = %s
                GROUP BY b.ISBN, b.Title, b.PublicationYear, p.Name, bc.Price, bc.DiscountPercent
                ORDER BY is_available DESC, b.Title ASC
            """
            cursor.execute(sql, (location_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching books at location: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

