from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.book import Book
from models.library import Library, Bookstore
from models.bookmark import Bookmark
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
        data = get_book_details(isbn)
        covers[isbn] = data.get('cover_image')
        if data and not data.get('_from_cache'):
            time.sleep(0.12)

    return render_template(
        'search.html',
        books=books,
        query=query,
        covers=covers,
        page=page,
        total_pages=total_pages,
        total=total,
    )


# ── Book detail ───────────────────────────────────────────────────────────────

@book_bp.route('/book/<isbn>')
def book_detail(isbn):
    book = Book.get_by_isbn(isbn)
    if not book:
        return "Book not found", 404

    availability = Book.get_availability(isbn)
    google_data  = get_book_details(isbn)

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
    wants_json = 'application/json' in request.headers.get('Accept', '')

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

    # Attach cover images from disk cache — no new API calls
    for bm in bookmarks:
        cached = cache_get(bm['ISBN']) or {}
        bm['cover_image'] = cached.get('cover_image')

    return render_template('bookmarks.html', bookmarks=bookmarks)


# ── Libraries / Bookstores ────────────────────────────────────────────────────

@book_bp.route('/libraries')
def libraries_list():
    libraries = Library.get_all()
    return render_template('libraries.html', locations=libraries, type="Library")


@book_bp.route('/bookstores')
def bookstores_list():
    stores = Bookstore.get_all()
    return render_template('libraries.html', locations=stores, type="Bookstore")

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
