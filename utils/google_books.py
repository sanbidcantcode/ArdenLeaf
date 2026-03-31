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


def get_book_details(isbn: str) -> dict:
    """
    Fetch book metadata from the Google Books API by ISBN.

    Checks the disk cache first. Only calls the API when the ISBN has never
    been fetched before. Returns an empty dict {} on failure or no results.
    """
    # --- Cache hit ---
    cached = book_cache.get(isbn)
    if cached is not None:
        return cached

    # --- API call ---
    try:
        response = requests.get(
            GOOGLE_BOOKS_API,
            params={"q": f"isbn:{isbn}"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        print(f"[google_books] Fetched ISBN {isbn} → {response.status_code}, items: {data.get('totalItems', 0)}")
    except requests.exceptions.HTTPError as e:
        print(f"[google_books] HTTP {e.response.status_code} for ISBN {isbn}")
        book_cache.set(isbn, {})   # cache the failure so we don't retry
        return {}
    except Exception as e:
        print(f"[google_books] Request failed for ISBN {isbn}: {e}")
        return {}   # don't cache network timeouts — may be transient

    items = data.get("items")
    if not items:
        book_cache.set(isbn, {})
        return {}

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
