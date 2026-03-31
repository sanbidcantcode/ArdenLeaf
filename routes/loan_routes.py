from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.loan import Loan
from utils.book_cache import get as cache_get

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

    return render_template('dashboard.html', loans=active_loans)


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
