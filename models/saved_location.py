from database.db import get_db_connection


class SavedLocation:

    @staticmethod
    def save(user_id, location_id, location_type):
        """Save a location (Library or Bookstore), silently ignoring duplicates."""
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT IGNORE INTO SavedLocation (UserID, LocationID, LocationType) "
                "VALUES (%s, %s, %s)",
                (user_id, location_id, location_type)
            )
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"[saved_location] save error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def unsave(user_id, location_id, location_type):
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM SavedLocation WHERE UserID = %s AND LocationID = %s "
                "AND LocationType = %s",
                (user_id, location_id, location_type)
            )
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"[saved_location] unsave error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def is_saved(user_id, location_id, location_type):
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM SavedLocation WHERE UserID = %s AND LocationID = %s "
                "AND LocationType = %s LIMIT 1",
                (user_id, location_id, location_type)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[saved_location] is_saved error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_user_saved(user_id):
        """Return all saved locations for the user with name/location info."""
        conn = cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT
                    sl.SavedID, sl.LocationID, sl.LocationType, sl.CreatedAt,
                    COALESCE(l.Name, s.Name) AS Name,
                    COALESCE(l.Location, s.Location) AS Location
                FROM SavedLocation sl
                LEFT JOIN Library l ON sl.LocationType = 'Library' AND sl.LocationID = l.LibraryID
                LEFT JOIN Bookstore s ON sl.LocationType = 'Bookstore' AND sl.LocationID = s.StoreID
                WHERE sl.UserID = %s
                ORDER BY sl.CreatedAt DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[saved_location] get_user_saved error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
