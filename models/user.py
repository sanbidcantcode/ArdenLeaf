from database.db import get_db_connection


class User:

    @staticmethod
    def get_by_email(email):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE Email = %s", (email,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create(name, email, password_hash, user_type, phone=None):
        """
        Create a new User row plus the appropriate specialisation record
        (Member or Customer). Optionally stores a phone number.

        Returns the new UserID on success, or None on failure.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert base user
            cursor.execute(
                "INSERT INTO User (Name, Email, PasswordHash, UserType) VALUES (%s, %s, %s, %s)",
                (name, email, password_hash, user_type)
            )
            user_id = cursor.lastrowid

            # Insert specialisation record
            if user_type == 'Member':
                cursor.execute(
                    "INSERT INTO Member (UserID, MembershipDate, MaxBooks) VALUES (%s, CURDATE(), 5)",
                    (user_id,)
                )
            elif user_type == 'Customer':
                cursor.execute(
                    "INSERT INTO Customer (UserID, LoyaltyPoints) VALUES (%s, 0)",
                    (user_id,)
                )

            # Optionally store phone number
            if phone:
                cursor.execute(
                    "INSERT INTO User_Phone (Phone, UserID) VALUES (%s, %s)",
                    (phone, user_id)
                )

            conn.commit()
            return user_id
        except Exception as e:
            if conn: conn.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                if user['UserType'] == 'Member':
                    cursor.execute("SELECT * FROM Member WHERE UserID = %s", (user_id,))
                    user.update(cursor.fetchone() or {})
                elif user['UserType'] == 'Customer':
                    cursor.execute("SELECT * FROM Customer WHERE UserID = %s", (user_id,))
                    user.update(cursor.fetchone() or {})

                cursor.execute("SELECT Phone FROM User_Phone WHERE UserID = %s", (user_id,))
                user['Phones'] = [row['Phone'] for row in cursor.fetchall()]

            return user
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_profile(user_id, name, email, phone):
        """
        Updates a user's name, email, and replaces their phone number.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE User SET Name = %s, Email = %s WHERE UserID = %s",
                (name, email, user_id)
            )

            cursor.execute("DELETE FROM User_Phone WHERE UserID = %s", (user_id,))
            if phone:
                cursor.execute(
                    "INSERT INTO User_Phone (Phone, UserID) VALUES (%s, %s)",
                    (phone, user_id)
                )

            conn.commit()
            return True, "Profile updated successfully."
        except Exception as e:
            if conn: conn.rollback()
            print(f"Error updating profile: {e}")
            return False, "Failed to update profile."
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
