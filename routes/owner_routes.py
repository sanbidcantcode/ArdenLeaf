from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_db_connection
from datetime import date

owner_bp = Blueprint('owner', __name__)

@owner_bp.before_request
def require_owner():
    if session.get('user_type') not in ('LibraryAdmin', 'StoreAdmin'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

@owner_bp.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    loc_id = session.get('location_id')
    loc_type = session.get('location_type')

    stats = {}
    copies = []
    history = []

    try:
        if loc_type == 'Library':
            cursor.execute("SELECT COUNT(*) as total FROM BookCopy WHERE LibraryID = %s", (loc_id,))
            stats['total'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) as available FROM BookCopy WHERE LibraryID = %s AND Status = 'Available'", (loc_id,))
            stats['available'] = cursor.fetchone()['available']
            cursor.execute("SELECT COUNT(*) as borrowed FROM BookCopy WHERE LibraryID = %s AND Status = 'Borrowed'", (loc_id,))
            stats['borrowed'] = cursor.fetchone()['borrowed']

            cursor.execute("""
                SELECT b.ISBN, b.Title, 
                    COUNT(bc.CopyID) as TotalCopies,
                    SUM(bc.Status = 'Available') as Available,
                    SUM(bc.Status = 'Borrowed') as Borrowed
                FROM BookCopy bc
                JOIN Book b ON bc.ISBN = b.ISBN
                WHERE bc.LibraryID = %s
                GROUP BY b.ISBN, b.Title
            """, (loc_id,))
            copies = cursor.fetchall()

            cursor.execute("""
                SELECT u.Name as MemberName, b.Title as BookTitle,
                    l.IssueDate, l.DueDate, l.ReturnDate
                FROM Loan l
                JOIN User u ON l.MemberID = u.UserID
                JOIN BookCopy bc ON l.CopyID = bc.CopyID
                JOIN Book b ON bc.ISBN = b.ISBN
                WHERE bc.LibraryID = %s
                ORDER BY l.IssueDate DESC
                LIMIT 20
            """, (loc_id,))
            history = cursor.fetchall()
            today = date.today()
            for row in history:
                if row['ReturnDate']:
                    row['Status'] = 'Returned'
                elif row['DueDate'] and row['DueDate'] < today:
                    row['Status'] = 'Overdue'
                else:
                    row['Status'] = 'Active'

        else:  # StoreAdmin
            cursor.execute("SELECT COUNT(*) as total FROM BookCopy WHERE StoreID = %s", (loc_id,))
            stats['total'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) as available FROM BookCopy WHERE StoreID = %s AND Status = 'Available'", (loc_id,))
            stats['available'] = cursor.fetchone()['available']
            cursor.execute("SELECT COUNT(*) as sold FROM BookCopy WHERE StoreID = %s AND Status = 'Sold'", (loc_id,))
            stats['sold'] = cursor.fetchone()['sold']

            cursor.execute("""
                SELECT b.ISBN, b.Title,
                    COUNT(bc.CopyID) as TotalCopies,
                    SUM(bc.Status = 'Available') as Available,
                    SUM(bc.Status = 'Sold') as Sold,
                    bc.Price
                FROM BookCopy bc
                JOIN Book b ON bc.ISBN = b.ISBN
                WHERE bc.StoreID = %s
                GROUP BY b.ISBN, b.Title, bc.Price
            """, (loc_id,))
            copies = cursor.fetchall()

    except Exception as e:
        print(f"Owner dashboard error: {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template('owner/dashboard.html', stats=stats, copies=copies, history=history)


@owner_bp.route('/copies/add', methods=['GET', 'POST'])
def add_copy():
    loc_id = session.get('location_id')
    loc_type = session.get('location_type')

    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        price = request.form.get('price', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if loc_type == 'Library':
                cursor.execute("INSERT INTO BookCopy (ISBN, LibraryID) VALUES (%s, %s)", (isbn, loc_id))
            else:
                cursor.execute(
                    "INSERT INTO BookCopy (ISBN, StoreID, Price) VALUES (%s, %s, %s)",
                    (isbn, loc_id, price if price else None)
                )
            conn.commit()
            flash('Copy added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error adding copy: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('owner.add_copy'))

    return render_template('owner/add_copy.html')


@owner_bp.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()

        if not isbn or not title:
            flash('ISBN and Title are required.', 'error')
            return redirect(url_for('owner.add_book'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Book (ISBN, Title, PublicationYear) VALUES (%s, %s, %s)",
                (isbn, title, year if year else None)
            )
            conn.commit()
            flash('Book added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error adding book: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('owner.add_book'))

    return render_template('owner/add_book.html')
