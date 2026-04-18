from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def require_admin():
    if session.get('user_type') != 'Admin':
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('index'))

@admin_bp.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total Books
    cursor.execute("SELECT COUNT(*) FROM Book")
    total_books = cursor.fetchone()[0]
    
    # Active Loans
    cursor.execute("SELECT COUNT(*) FROM Loan WHERE ReturnDate IS NULL")
    active_loans = cursor.fetchone()[0]
    
    # Total Members
    cursor.execute("SELECT COUNT(*) FROM User WHERE UserType = 'Member'")
    total_members = cursor.fetchone()[0]
    
    # Partner Locations
    cursor.execute("SELECT (SELECT COUNT(*) FROM Libraries) + (SELECT COUNT(*) FROM Bookstores)")
    total_locations = cursor.fetchone()[0]

    # Detailed Data for Panels
    db_cursor = conn.cursor(dictionary=True) # Use dictionary cursor for detail lists
    
    # Books list
    db_cursor.execute("SELECT ISBN, Title FROM Book ORDER BY Title")
    books_list = db_cursor.fetchall()

    # Active loans list
    db_cursor.execute("""
        SELECT u.Name AS MemberName, b.Title AS BookTitle, 
               lib.Name AS LibraryName, l.IssueDate, l.DueDate
        FROM Loan l
        JOIN User u ON l.MemberID = u.UserID
        JOIN BookCopy bc ON l.CopyID = bc.CopyID
        JOIN Book b ON bc.ISBN = b.ISBN
        LEFT JOIN Libraries lib ON bc.LibraryID = lib.LibraryID
        WHERE l.ReturnDate IS NULL
        ORDER BY l.DueDate ASC
    """)
    active_loans_list = db_cursor.fetchall()

    # Members list
    db_cursor.execute("""
        SELECT u.Name, u.Email, m.MembershipDate, m.MaxBooks
        FROM User u JOIN Member m ON u.UserID = m.UserID
        ORDER BY u.Name
    """)
    members_list = db_cursor.fetchall()

    # Locations list
    db_cursor.execute("SELECT LibraryID AS ID, Name, Location, 'Library' AS Type FROM Libraries")
    libs = db_cursor.fetchall()
    db_cursor.execute("SELECT StoreID AS ID, Name, Location, 'Bookstore' AS Type FROM Bookstores")
    stores = db_cursor.fetchall()
    locations_list = libs + stores

    db_cursor.close()
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                            total_books=total_books, 
                            active_loans=active_loans, 
                            total_members=total_members, 
                            total_locations=total_locations,
                            books_list=books_list,
                            active_loans_list=active_loans_list,
                            members_list=members_list,
                            locations_list=locations_list)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()
        
        if not isbn or not title:
            flash('ISBN and Title are required.', 'error')
            return redirect(url_for('admin.add_book'))

        # Insert Book
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Book (ISBN, Title, PublicationYear) VALUES (%s, %s, %s)", 
                           (isbn, title, year if year else None))
            conn.commit()
            flash('Book added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error adding book: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin.add_book'))

    return render_template('admin/add_book.html')

@admin_bp.route('/copies/add', methods=['GET', 'POST'])
def add_copy():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        loc_type = request.form.get('loc_type')
        loc_id = request.form.get('loc_id')
        price = request.form.get('price')

        try:
            if loc_type == 'Library':
                cursor.execute("INSERT INTO BookCopy (ISBN, LibraryID) VALUES (%s, %s)", (isbn, loc_id))
            else:
                cursor.execute("INSERT INTO BookCopy (ISBN, StoreID, Price) VALUES (%s, %s, %s)", (isbn, loc_id, price if price else None))
            conn.commit()
            flash('Book copy added!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error adding copy: {str(e)}', 'error')

        return redirect(url_for('admin.add_copy'))

    # GET request needs lists of locs
    cursor.execute("SELECT * FROM Libraries")
    libraries = cursor.fetchall()
    cursor.execute("SELECT * FROM Bookstores")
    bookstores = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/add_copy.html', libraries=libraries, bookstores=bookstores)

@admin_bp.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        loc_type = request.form.get('type')
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        
        if not name or not address:
            flash('Name and Address are required.', 'error')
            return redirect(url_for('admin.add_location'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if loc_type == 'Library':
                cursor.execute("INSERT INTO Libraries (Name, Location) VALUES (%s, %s)", (name, address))
            else:
                cursor.execute("INSERT INTO Bookstores (Name, Location) VALUES (%s, %s)", (name, address))
            conn.commit()
            flash('Location added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error adding location: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin.add_location'))

    return render_template('admin/add_location.html')

@admin_bp.route('/loans')
def loans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                u.Name AS MemberName,
                b.Title AS BookTitle,
                lib.Name AS LibraryName,
                l.IssueDate,
                l.DueDate,
                l.ReturnDate
            FROM Loan l
            JOIN User u ON l.MemberID = u.UserID
            JOIN BookCopy bc ON l.CopyID = bc.CopyID
            JOIN Book b ON bc.ISBN = b.ISBN
            JOIN Libraries lib ON bc.LibraryID = lib.LibraryID
            WHERE l.ReturnDate IS NULL
            ORDER BY l.DueDate ASC
        """
        cursor.execute(sql)
        loans = cursor.fetchall()
        from datetime import date
        today = date.today()
        for loan in loans:
            if loan['DueDate'] and loan['DueDate'] < today:
                loan['Status'] = 'Overdue'
            else:
                loan['Status'] = 'Active'
    except Exception as e:
        print(e)
        loans = []
    finally:
        cursor.close()
        conn.close()
        
    return render_template('admin/loans.html', loans=loans)
