from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.user import User
from database.db import get_db_connection

profile_bp = Blueprint('profile', __name__)

def get_quick_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    stats = {
        'active_loans': 0,
        'total_borrowed': 0,
        'bookmarks': 0,
        'fines': 0.0
    }
    try:
        # Active loans count
        cursor.execute("SELECT COUNT(*) as c FROM Loan WHERE MemberID = %s AND ReturnDate IS NULL", (user_id,))
        row = cursor.fetchone()
        if row: stats['active_loans'] = row['c']
        
        # Total borrowed
        cursor.execute("SELECT COUNT(*) as c FROM Loan WHERE MemberID = %s", (user_id,))
        row = cursor.fetchone()
        if row: stats['total_borrowed'] = row['c']
        
        # Bookmarks count
        cursor.execute("SELECT COUNT(*) as c FROM Bookmark WHERE UserID = %s", (user_id,))
        row = cursor.fetchone()
        if row: stats['bookmarks'] = row['c']
        
        # Fines (sum from the VIEW)
        cursor.execute("SELECT SUM(FineAmount) as f FROM LoanFines WHERE MemberID = %s", (user_id,))
        row = cursor.fetchone()
        if row and row['f']: stats['fines'] = float(row['f'])
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
    finally:
        cursor.close()
        conn.close()
    return stats

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('auth.auth_page'))
        
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        success, message = User.update_profile(user_id, name, email, phone)
        
        if success:
            session['user_name'] = name # Update session name
            
        wants_json = 'application/json' in request.headers.get('Accept', '') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if wants_json:
            return jsonify({
                'success': success,
                'message': message,
                'type': 'success' if success else 'error'
            })
            
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('profile.profile'))
        
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.logout'))
        
    stats = get_quick_stats(user_id)
    
    # Fetch histories for modals
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    history = []
    fines = []
    try:
        # Full borrow history
        cursor.execute("""
            SELECT 
                l.LoanID, b.Title, b.ISBN,
                COALESCE(lib.Name, s.Name) AS SourceName,
                'Borrowed' AS ActionType,
                l.IssueDate, l.ReturnDate
            FROM Loan l
            JOIN BookCopy bc ON l.CopyID = bc.CopyID
            JOIN Book b ON bc.ISBN = b.ISBN
            LEFT JOIN Library lib ON bc.LibraryID = lib.LibraryID
            LEFT JOIN Bookstore s ON bc.StoreID = s.StoreID
            WHERE l.MemberID = %s
            ORDER BY l.IssueDate DESC
        """, (user_id,))
        for row in cursor.fetchall():
            history.append({
                'title': row['Title'],
                'isbn': row['ISBN'],
                'source': row['SourceName'],
                'type': row['ActionType'],
                'date': row['IssueDate'].strftime('%d %b %Y') if row['IssueDate'] else '',
                'returned': row['ReturnDate'].strftime('%d %b %Y') if row['ReturnDate'] else 'Active'
            })
            
        # Fines history
        cursor.execute("""
            SELECT 
                lf.LoanID, b.Title, b.ISBN,
                lf.FineAmount, l.IssueDate, lf.DueDate, lf.ReturnDate
            FROM LoanFines lf
            JOIN Loan l ON lf.LoanID = l.LoanID
            JOIN BookCopy bc ON l.CopyID = bc.CopyID
            JOIN Book b ON bc.ISBN = b.ISBN
            WHERE lf.MemberID = %s AND lf.FineAmount > 0
            ORDER BY l.IssueDate DESC
        """, (user_id,))
        for row in cursor.fetchall():
            # Status badge logic
            # Cleared = returned and fine paid? or just returned? There's no FinePaid field in schema.
            # I will assume: if ReturnDate is not null, it's Cleared (or past due if not returned yet).
            # Wait, the prompt says: "Cleared (returned), Due (not returned, > due_date), Past Due (same)".
            # Actually prompt says: `Cleared = green, Due = yellow, Past Due = red`.
            is_returned = row['ReturnDate'] is not None
            # If not returned, past due is red, due is yellow. But all fine amount > 0 implies it's past due.
            status = 'Cleared' if is_returned else 'Past Due'
            
            fines.append({
                'title': row['Title'],
                'isbn': row['ISBN'],
                'amount': float(row['FineAmount']),
                'start_date': row['IssueDate'].strftime('%d %b %Y') if row['IssueDate'] else '',
                'due_date': row['DueDate'].strftime('%d %b %Y') if row['DueDate'] else '',
                'status': status
            })
    except Exception as e:
        print(f"Error fetching history: {e}")
    finally:
        cursor.close()
        conn.close()
        
    import json
    return render_template('profile.html', user=user, stats=stats, 
                           history_json=json.dumps(history), 
                           fines_json=json.dumps(fines))

@profile_bp.route('/saved-locations')
def saved_locations():
    if not session.get('user_id'):
        flash('Please log in to view your saved locations.', 'error')
        return redirect(url_for('auth.auth_page'))
    # For now, we'll just show the locations page or a placeholder
    # In a real app we might fetch user-specific saved locations.
    # We will reuse the locations logic or just redirect to books.libraries_list
    return redirect(url_for('books.libraries_list'))
