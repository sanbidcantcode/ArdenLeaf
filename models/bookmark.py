from database.db import get_db_connection


class Bookmark:

    @staticmethod
    def add_bookmark(user_id, isbn):
        """Insert a bookmark, silently ignoring duplicates (UNIQUE constraint)."""
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT IGNORE INTO Bookmark (UserID, ISBN) VALUES (%s, %s)",
                (user_id, isbn)
            )
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"[bookmark] add error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def remove_bookmark(user_id, isbn):
        """Delete a bookmark for the given user and isbn."""
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Bookmark WHERE UserID = %s AND ISBN = %s",
                (user_id, isbn)
            )
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"[bookmark] remove error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def is_bookmarked(user_id, isbn):
        """Return True if the user has bookmarked this isbn."""
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM Bookmark WHERE UserID = %s AND ISBN = %s LIMIT 1",
                (user_id, isbn)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[bookmark] is_bookmarked error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_user_bookmarks(user_id):
        """
        Return all bookmarked books for a user with full book details.
        Joins Bookmark → Book → Author (via Book_Author) → genres (via Book_Genre).
        """
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT
                    bm.BookmarkID,
                    bm.CreatedAt,
                    b.ISBN,
                    b.Title,
                    b.PublicationYear,
                    GROUP_CONCAT(DISTINCT a.Name ORDER BY a.Name SEPARATOR ', ') AS Authors,
                    GROUP_CONCAT(DISTINCT bg.Genre ORDER BY bg.Genre SEPARATOR ', ') AS Genres,
                    p.Name AS PublisherName
                FROM Bookmark bm
                JOIN Book b ON bm.ISBN = b.ISBN
                LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN
                LEFT JOIN Author a ON ba.AuthorID = a.AuthorID
                LEFT JOIN Book_Genre bg ON b.ISBN = bg.ISBN
                LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
                WHERE bm.UserID = %s
                GROUP BY
                    bm.BookmarkID, bm.CreatedAt,
                    b.ISBN, b.Title, b.PublicationYear, p.Name
                ORDER BY bm.CreatedAt DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[bookmark] get_user_bookmarks error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
