from database.db import get_db_connection

class Loan:
    @staticmethod
    def issue_loan(copy_id, member_id, due_days=14):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if copy is available
            cursor.execute("SELECT Status FROM BookCopy WHERE CopyID = %s And LibraryID IS NOT NULL", (copy_id,))
            copy = cursor.fetchone()
            
            if not copy or copy[0] != 'Available':
                return False, "Copy is not available or does not belong to a library."
                
            # Issue loan
            sql_loan = """
                INSERT INTO Loan (CopyID, MemberID, IssueDate, DueDate) 
                VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY))
            """
            cursor.execute(sql_loan, (copy_id, member_id, due_days))
            
            # Update copy status
            cursor.execute("UPDATE BookCopy SET Status = 'Borrowed' WHERE CopyID = %s", (copy_id,))
            
            conn.commit()
            return True, "Loan issued successfully."
        except Exception as e:
            if conn: conn.rollback()
            print(f"Error issuing loan: {e}")
            return False, f"Error issuing loan: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def return_loan(loan_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get the copy ID for this loan
            cursor.execute("SELECT CopyID FROM Loan WHERE LoanID = %s", (loan_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Loan not found."
                
            copy_id = result[0]
            
            # Update loan record
            cursor.execute("UPDATE Loan SET ReturnDate = CURDATE() WHERE LoanID = %s", (loan_id,))
            
            # Update book copy to available
            cursor.execute("UPDATE BookCopy SET Status = 'Available' WHERE CopyID = %s", (copy_id,))
            
            conn.commit()
            return True, "Book returned."
        except Exception as e:
            if conn: conn.rollback()
            print(f"Error returning loan: {e}")
            return False, f"Error returning loan: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_member_loans(member_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    l.LoanID, l.IssueDate, l.DueDate, l.ReturnDate,
                    b.Title, b.ISBN, bc.CopyID,
                    lf.FineAmount
                FROM Loan l
                JOIN BookCopy bc ON l.CopyID = bc.CopyID
                JOIN Book b ON bc.ISBN = b.ISBN
                LEFT JOIN LoanFines lf ON l.LoanID = lf.LoanID
                WHERE l.MemberID = %s
                ORDER BY l.IssueDate DESC
            """
            cursor.execute(sql, (member_id,))
            loans = cursor.fetchall()
            return loans
        except Exception as e:
            print(f"Error fetching member loans: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_active_loans(member_id):
        """Return only loans that have not been returned yet."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    l.LoanID, l.IssueDate, l.DueDate,
                    b.Title, b.ISBN, bc.CopyID,
                    COALESCE(lf.FineAmount, 0.00) AS FineAmount,
                    CASE WHEN CURDATE() > l.DueDate THEN 1 ELSE 0 END AS IsOverdue
                FROM Loan l
                JOIN BookCopy bc ON l.CopyID = bc.CopyID
                JOIN Book b ON bc.ISBN = b.ISBN
                LEFT JOIN LoanFines lf ON l.LoanID = lf.LoanID
                WHERE l.MemberID = %s AND l.ReturnDate IS NULL
                ORDER BY l.DueDate ASC
            """
            cursor.execute(sql, (member_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching active loans: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

