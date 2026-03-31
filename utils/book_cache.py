"""
utils/book_cache.py

Disk-based cache for Google Books API data.
Stores data as a JSON file so it persists across server restarts.
Capped at MAX_ENTRIES to prevent unbounded growth.
"""

import json
import os
import threading

CACHE_FILE = os.path.join(os.path.dirname(__file__), '.book_cache.json')
MAX_ENTRIES = 500   # max ISBNs to store

# Thread lock so parallel access doesn't corrupt the file
_lock = threading.Lock()


def _load() -> dict:
    """Read the cache file from disk. Returns {} if missing or corrupt."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(cache: dict) -> None:
    """Write the cache dict back to disk."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[book_cache] Could not write cache: {e}")


def get(isbn: str) -> dict | None:
    """Return cached data for isbn, or None if not cached."""
    with _lock:
        cache = _load()
        return cache.get(isbn)


def set(isbn: str, data: dict) -> None:
    """Store data for isbn. Evicts oldest entries if over MAX_ENTRIES."""
    with _lock:
        cache = _load()
        if len(cache) >= MAX_ENTRIES and isbn not in cache:
            # Remove the first (oldest) entry
            oldest = next(iter(cache))
            del cache[oldest]
        cache[isbn] = data
        _save(cache)


def is_cached(isbn: str) -> bool:
    """Return True if the isbn has been cached (even if the result was empty)."""
    with _lock:
        cache = _load()
        return isbn in cache
