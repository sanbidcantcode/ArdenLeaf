from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from database.db import get_db_connection

auth_bp = Blueprint('auth', __name__)


# ── Combined login / register page ──────────────────────────────────────────

@auth_bp.route('/auth', methods=['GET', 'POST'])
def auth_page():
    """Single-page auth: hosts both login and sign-up forms."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # ── LOGIN ────────────────────────────────────────────────────────────
        if form_type == 'login':
            email    = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            user = User.get_by_email(email)
            if user and user['PasswordHash'] == password:
                session['user_id']   = user['UserID']
                session['user_name'] = user['Name']
                session['user_type'] = user['UserType']
                flash('Welcome back, {}!'.format(user['Name']), 'success')
                # LibraryAdmin / StoreAdmin → owner dashboard
                if user['UserType'] in ('LibraryAdmin', 'StoreAdmin'):
                    conn2 = get_db_connection()
                    cur2 = conn2.cursor(dictionary=True)
                    cur2.execute("SELECT * FROM LocationAdmin WHERE UserID = %s", (user['UserID'],))
                    loc = cur2.fetchone()
                    cur2.close()
                    conn2.close()
                    if loc:
                        if loc['LibraryID']:
                            conn3 = get_db_connection()
                            cur3 = conn3.cursor(dictionary=True)
                            cur3.execute("SELECT Name FROM Library WHERE LibraryID = %s", (loc['LibraryID'],))
                            loc_row = cur3.fetchone()
                            cur3.close()
                            conn3.close()
                            session['location_id']   = loc['LibraryID']
                            session['location_type'] = 'Library'
                            session['location_name'] = loc_row['Name'] if loc_row else 'Your Library'
                        else:
                            conn3 = get_db_connection()
                            cur3 = conn3.cursor(dictionary=True)
                            cur3.execute("SELECT Name FROM Bookstore WHERE StoreID = %s", (loc['StoreID'],))
                            loc_row = cur3.fetchone()
                            cur3.close()
                            conn3.close()
                            session['location_id']   = loc['StoreID']
                            session['location_type'] = 'Bookstore'
                            session['location_name'] = loc_row['Name'] if loc_row else 'Your Store'
                    return redirect(url_for('owner.dashboard'))
                # Members go to their dashboard; Customers go home
                if user['UserType'] == 'Member':
                    return redirect(url_for('loans.dashboard'))
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
                return render_template('auth.html', show_signup=False,
                                       login_email=email)

        # ── REGISTER ─────────────────────────────────────────────────────────
        elif form_type == 'register':
            name             = request.form.get('name', '').strip()
            email            = request.form.get('email', '').strip()
            password         = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            phone            = request.form.get('phone', '').strip()
            user_type        = 'Member'   # all self-registered users are Members

            # Basic server-side validation
            if not name or not email or not password:
                flash('Please fill in all required fields.', 'error')
                return render_template('auth.html', show_signup=True)

            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('auth.html', show_signup=True)

            if len(password) < 8:
                flash('Password must be at least 8 characters.', 'error')
                return render_template('auth.html', show_signup=True)

            if User.get_by_email(email):
                flash('An account with that email already exists.', 'error')
                return render_template('auth.html', show_signup=True)

            # Create user (plain password stored for demo — swap for hash in prod)
            user_id = User.create(name, email, password, user_type, phone=phone)
            if not user_id:
                flash('Registration failed. Please try again.', 'error')
                return render_template('auth.html', show_signup=True)

            # Auto-login after registration
            session['user_id']   = user_id
            session['user_name'] = name
            session['user_type'] = user_type

            flash('Account created! Let us know where you are.', 'success')
            return redirect(url_for('auth.location_step'))

    # GET — show the combined page with login visible by default
    return render_template('auth.html', show_signup=False)


# ── Location step ────────────────────────────────────────────────────────────

@auth_bp.route('/location', methods=['GET'])
def location_step():
    """Post-registration page — ask user to share or enter location."""
    if not session.get('user_id'):
        return redirect(url_for('auth.auth_page'))
    return render_template('location.html')


@auth_bp.route('/location/save', methods=['POST'])
def save_location():
    """Accept location form submission and redirect home."""
    location = request.form.get('location', '').strip()
    lat      = request.form.get('lat', '').strip()
    lng      = request.form.get('lng', '').strip()

    if location or (lat and lng):
        session['user_location'] = location or f"{lat},{lng}"
        flash('Location saved!', 'success')
    # Send members to dashboard, customers to home
    if session.get('user_type') == 'Member':
        return redirect(url_for('loans.dashboard'))
    return redirect(url_for('index'))


# ── Logout ───────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ── Legacy redirects (keep old URLs working) ─────────────────────────────────

@auth_bp.route('/login')
def login():
    return redirect(url_for('auth.auth_page'))

@auth_bp.route('/register')
def register():
    return redirect(url_for('auth.auth_page'))
