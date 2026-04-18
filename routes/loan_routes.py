from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.loan import Loan
from utils.book_cache import get as cache_get
from database.db import get_db_connection
import datetime


loan_bp = Blueprint('loans', __name__)


# ── Helper ───────────────────────────────────────────────────────────────────

def _require_member():
    """Return None if the session is a valid Member, else a redirect response."""
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('auth.auth_page'))
    if session.get('user_type') != 'Member':
        flash('Only library members can access this page.', 'error')
        return redirect(url_for('index'))
    return None


# ── Dashboard ─────────────────────────────────────────────────────────────────

@loan_bp.route('/dashboard')
def dashboard():
    guard = _require_member()
    if guard:
        return guard

    member_id   = session['user_id']
    active_loans = Loan.get_active_loans(member_id)

    # Attach cover images from disk cache (no new API calls here)
    for loan in active_loans:
        cached = cache_get(loan['ISBN']) or {}
        loan['cover_image'] = cached.get('cover_image')

    from routes.profile_routes import get_quick_stats
    stats = get_quick_stats(member_id)

    # Fetch histories for modals
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    all_loans = []
    fines = []
    try:
        # Full borrow history
        cursor.execute("""
            SELECT 
                l.LoanID, b.Title, b.ISBN,
                COALESCE(lib.Name, s.Name) AS SourceName,
                l.IssueDate, l.ReturnDate, l.DueDate
            FROM Loan l
            JOIN BookCopy bc ON l.CopyID = bc.CopyID
            JOIN Book b ON bc.ISBN = b.ISBN
            LEFT JOIN Libraries lib ON bc.LibraryID = lib.LibraryID
            LEFT JOIN Bookstores s ON bc.StoreID = s.StoreID
            WHERE l.MemberID = %s
            ORDER BY l.IssueDate DESC
        """, (member_id,))
        all_loans = cursor.fetchall()
            
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
        """, (member_id,))
        fines = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching dashboard histories: {e}")
    finally:
        cursor.close()
        conn.close()

    today = datetime.date.today()
    overdue_count = sum(
        1 for loan in active_loans
        if loan.get('DueDate') and (
            loan['DueDate'].date() if hasattr(loan['DueDate'], 'date') else loan['DueDate']
        ) < today
    )

    return render_template('dashboard.html', loans=active_loans,
                           all_loans=all_loans,
                           fines=fines,
                           active_loans_count=stats['active_loans'],
                           total_loans=stats['total_borrowed'],
                           bookmarks_count=stats['bookmarks'],
                           fines_due=stats['fines'],
                           overdue_count=overdue_count)


# ── My Loans (full history) ───────────────────────────────────────────────────

@loan_bp.route('/my_loans')
def my_loans():
    guard = _require_member()
    if guard:
        return guard

    loans = Loan.get_member_loans(session['user_id'])
    return render_template('loans.html', loans=loans)


# ── Borrow (form POST with copy_id in body) ──────────────────────────────────

@loan_bp.route('/loans/borrow', methods=['POST'])
def borrow_book():
    wants_json = 'application/json' in request.headers.get('Accept', '')
    
    guard = _require_member()
    if guard:
        if wants_json:
            return jsonify({'success': False, 'message': 'Please log in to continue.'})
        return guard

    copy_id = request.form.get('copy_id', type=int)
    if not copy_id:
        if wants_json:
            return jsonify({'success': False, 'message': 'Invalid request — no copy specified.'})
        flash('Invalid request — no copy specified.', 'error')
        return redirect(request.referrer or url_for('books.search'))

    success, msg = Loan.issue_loan(copy_id, session['user_id'])
    if wants_json:
        if success:
            return jsonify({'success': True, 'message': 'Borrowed! Due in 14 days', 'type': 'success'})
        return jsonify({'success': False, 'message': msg, 'type': 'error'})

    if success:
        flash('Borrowed! Due in 14 days', 'success')
        return redirect(url_for('loans.dashboard'))
    else:
        flash(msg, 'error')
        return redirect(request.referrer or url_for('books.search'))


# ── Borrow (legacy URL-param route kept for compatibility) ────────────────────

@loan_bp.route('/borrow/<int:copy_id>', methods=['POST'])
def borrow(copy_id):
    guard = _require_member()
    if guard:
        return guard

    success, msg = Loan.issue_loan(copy_id, session['user_id'])
    if success:
        flash('Book borrowed successfully! Due in 14 days.', 'success')
        return redirect(url_for('loans.dashboard'))
    else:
        flash(msg, 'error')
        return redirect(request.referrer or url_for('loans.dashboard'))


# ── Return ────────────────────────────────────────────────────────────────────

@loan_bp.route('/loans/return/<int:loan_id>', methods=['POST'])
def return_book(loan_id):
    guard = _require_member()
    if guard:
        return guard

    success, msg = Loan.return_loan(loan_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('loans.dashboard'))
