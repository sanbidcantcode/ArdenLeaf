from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.book import Book
from models.library import Library, Bookstore
from models.bookmark import Bookmark
from models.saved_location import SavedLocation
from utils.google_books import get_book_details
from utils.book_cache import get as cache_get
import time
import math

book_bp = Blueprint('books', __name__)

PER_PAGE = 10


# ── Search ────────────────────────────────────────────────────────────────────

@book_bp.route('/search')
def search():
    query  = request.args.get('q', '')
    page   = max(1, int(request.args.get('page', 1)))

    all_books   = Book.search(query)
    total       = len(all_books)
    total_pages = max(1, math.ceil(total / PER_PAGE))
    page        = min(page, total_pages)

    start = (page - 1) * PER_PAGE
    books = all_books[start: start + PER_PAGE]

    covers = {}
    for book in books:
        isbn = book['ISBN']
        data = get_book_details(isbn, title=book.get('Title'), author=book.get('Authors'))
        covers[isbn] = data.get('cover_image')

    user_id = session.get('user_id')
    bookmarked_isbns = set()
    if user_id:
        for book in books:
            if Bookmark.is_bookmarked(user_id, book['ISBN']):
                bookmarked_isbns.add(book['ISBN'])

    return render_template(
        'search.html',
        books=books,
        query=query,
        covers=covers,
        page=page,
        total_pages=total_pages,
        total=total,
        bookmarked_isbns=bookmarked_isbns,
    )


# ── Book detail ───────────────────────────────────────────────────────────────

@book_bp.route('/book/<isbn>')
def book_detail(isbn):
    book = Book.get_by_isbn(isbn)
    if not book:
        return "Book not found", 404

    availability = Book.get_availability(isbn)
    google_data  = get_book_details(isbn, title=book.get('Title'), author=book.get('Authors'))

    # Check bookmark state for logged-in users
    user_id       = session.get('user_id')
    bookmarked    = Bookmark.is_bookmarked(user_id, isbn) if user_id else False

    return render_template(
        'book_detail.html',
        book=book,
        availability=availability,
        google_data=google_data,
        bookmarked=bookmarked,
    )


# ── Bookmark toggle ───────────────────────────────────────────────────────────

@book_bp.route('/book/<isbn>/bookmark', methods=['POST'])
def bookmark(isbn):
    wants_json = (
        'application/json' in request.headers.get('Accept', '') or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )

    if not session.get('user_id'):
        if wants_json:
            return jsonify({'success': False, 'message': 'Please log in to bookmark books.', 'bookmarked': False})
        flash('Please log in to bookmark books.', 'error')
        return redirect(url_for('auth.auth_page'))

    user_id = session['user_id']
    book    = Book.get_by_isbn(isbn)

    if Bookmark.is_bookmarked(user_id, isbn):
        Bookmark.remove_bookmark(user_id, isbn)
        now_bookmarked = False
        message = 'Bookmark removed.'
        toast_type = 'info'
    else:
        Bookmark.add_bookmark(user_id, isbn)
        now_bookmarked = True
        message = 'Bookmarked! Find it in your bookmarks anytime.'
        toast_type = 'success'

    if wants_json:
        return jsonify({
            'success':    True,
            'bookmarked': now_bookmarked,
            'message':    message,
            'type':       toast_type,
            'title':      book['Title'] if book else '',
            'isbn':       isbn,
        })

    flash(message, toast_type)
    return redirect(url_for('books.book_detail', isbn=isbn))


# ── Bookmarks page ────────────────────────────────────────────────────────────

@book_bp.route('/bookmarks')
def bookmarks_page():
    if not session.get('user_id'):
        flash('Please log in to view your bookmarks.', 'error')
        return redirect(url_for('auth.auth_page'))

    user_id   = session['user_id']
    bookmarks = Bookmark.get_user_bookmarks(user_id)

    all_genres = set()
    from models.book import Book
    
    # Attach cover images and availability from disk cache/DB
    for bm in bookmarks:
        cached = cache_get(bm['ISBN']) or {}
        bm['cover_image'] = cached.get('cover_image')
        
        # Check availability
        copies = Book.get_availability(bm['ISBN'])
        bm['is_available'] = any(c['Status'] == 'Available' for c in copies)
        
        if bm['Genres']:
            for g in bm['Genres'].split(','):
                all_genres.add(g.strip())

    return render_template('bookmarks.html', 
                           bookmarks=bookmarks, 
                           unique_genres=sorted(list(all_genres)))


# ── Saved Locations ("Your Libraries") ───────────────────────────────────────

@book_bp.route('/libraries')
def libraries_list():
    if not session.get('user_id'):
        flash('Please log in to view your saved locations.', 'error')
        return redirect(url_for('auth.auth_page'))

    from models.saved_location import SavedLocation
    saved = SavedLocation.get_user_saved(session['user_id'])
    return render_template('libraries.html', saved=saved)


@book_bp.route('/locations')
def locations():
    libs = Library.get_all()
    stores = Bookstore.get_all()
    
    combined = []
    for l in libs:
        combined.append({
            'ID': l['LibraryID'],
            'Name': l['Name'],
            'Location': l['Location'],
            'Type': 'Library'
        })
    for s in stores:
        combined.append({
            'ID': s['StoreID'],
            'Name': s['Name'],
            'Location': s['Location'],
            'Type': 'Bookstore'
        })
    
    return render_template('locations.html', locations=combined)
    
@book_bp.route('/locations/<loc_type>/<int:location_id>')
def location_detail(loc_type, location_id):
    location = None

    if loc_type == 'Library':
        libs = Library.get_all()
        for l in libs:
            if l['LibraryID'] == location_id:
                location = {
                    'ID': l['LibraryID'],
                    'Name': l['Name'],
                    'Location': l['Location'],
                    'Type': 'Library'
                }
                break
    elif loc_type == 'Bookstore':
        stores = Bookstore.get_all()
        for s in stores:
            if s['StoreID'] == location_id:
                location = {
                    'ID': s['StoreID'],
                    'Name': s['Name'],
                    'Location': s['Location'],
                    'Type': 'Bookstore'
                }
                break

    if not location:
        from flask import abort
        abort(404)

    # Fetch books at this location
    books = Book.get_books_at_location(location_id, location['Type'])

    # Attach cover images from cache
    for book in books:
        cached = cache_get(book['ISBN']) or {}
        book['cover_image'] = cached.get('cover_image')

    # Check if user has saved this location
    user_id = session.get('user_id')
    is_saved = SavedLocation.is_saved(user_id, location_id, location['Type']) if user_id else False

    return render_template(
        'location_detail.html',
        location=location,
        books=books,
        is_saved=is_saved,
    )


@book_bp.route('/locations/<int:location_id>/save', methods=['POST'])
def save_location(location_id):
    wants_json = (
        'application/json' in request.headers.get('Accept', '') or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )

    if not session.get('user_id'):
        if wants_json:
            return jsonify({'success': False, 'message': 'Please log in to save locations.', 'saved': False})
        flash('Please log in to save locations.', 'error')
        return redirect(url_for('auth.auth_page'))

    user_id = session['user_id']
    location_type = request.form.get('location_type', 'Library')

    if SavedLocation.is_saved(user_id, location_id, location_type):
        SavedLocation.unsave(user_id, location_id, location_type)
        now_saved = False
        message = 'Location removed from saved.'
        toast_type = 'info'
    else:
        SavedLocation.save(user_id, location_id, location_type)
        now_saved = True
        message = 'Location saved! Find it in Your Libraries.'
        toast_type = 'success'

    if wants_json:
        return jsonify({
            'success': True,
            'saved': now_saved,
            'message': message,
            'type': toast_type,
        })

    flash(message, toast_type)
    return redirect(url_for('books.location_detail', loc_type=location_type, location_id=location_id))
