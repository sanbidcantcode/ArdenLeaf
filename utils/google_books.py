"""
utils/google_books.py

Fetches enrichment data for a book from the Google Books API using its ISBN.
Uses a disk-based cache (utils/.book_cache.json) so each ISBN is only ever
fetched once — results survive server restarts.
"""

import requests
import time
from utils import book_cache

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"


def get_book_details(isbn: str, title: str = None, author: str = None) -> dict:
    """
    Fetch book metadata from the Google Books API by ISBN, with title/author fallback.

    Checks the disk cache first (using original isbn as key).
    """
    # --- Cache hit ---
    cached = book_cache.get(isbn)
    if cached is not None:
        return cached

    clean_isbn = isbn.replace('-', '').replace(' ', '').strip()

    # --- 1. Primary Search: By ISBN ---
    try:
        response = requests.get(
            GOOGLE_BOOKS_API,
            params={"q": f"isbn:{clean_isbn}"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"[google_books] Rate limited for ISBN {isbn}, will retry later")
            return {}
        print(f"[google_books] ISBN search failed for {isbn}: {e}")
        data = {"totalItems": 0}
    except Exception as e:
        print(f"[google_books] ISBN search connection error for {isbn}: {e}")
        data = {"totalItems": 0}

    # --- 2. Fallback Search: By Title+Author ---
    if data.get("totalItems", 0) == 0 and title:
        time.sleep(0.3) # Rate limit protection for second call
        try:
            query = f"intitle:{title}"
            if author:
                query += f"+inauthor:{author}"
            
            print(f"[google_books] Falling back to title search: {query}")
            response = requests.get(
                GOOGLE_BOOKS_API,
                params={"q": query},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"[google_books] Rate limited during fallback for {title}")
                return {}
            print(f"[google_books] Fallback search failed for {title}: {e}")
            data = {"totalItems": 0}
        except Exception as e:
            print(f"[google_books] Fallback connection error for {title}: {e}")
            data = {"totalItems": 0}

    items = data.get("items")
    if not items:
        # Only cache "empty" results if the call actually succeeded with totalItems=0
        if data.get("totalItems") == 0:
            book_cache.set(isbn, {})
        return {}

    # Extract info from the best match
    volume_info = items[0].get("volumeInfo", {})
    image_links = volume_info.get("imageLinks", {})

    cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail") or None
    if cover_url:
        cover_url = cover_url.replace("http://", "https://")

    result = {
        "cover_image":    cover_url,
        "description":    volume_info.get("description") or None,
        "page_count":     volume_info.get("pageCount") or None,
        "average_rating": volume_info.get("averageRating") or None,
        "ratings_count":  volume_info.get("ratingsCount") or None,
        "language":       volume_info.get("language") or None,
        "preview_link":   volume_info.get("previewLink") or None,
        "categories":     volume_info.get("categories") or None,
    }

    book_cache.set(isbn, result)
    return result
