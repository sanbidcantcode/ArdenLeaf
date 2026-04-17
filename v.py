import sys
import time
sys.path.insert(0, '.')
from utils.google_books import get_book_details

books = [
    ('978-0062073488', 'And Then There Were None', 'Agatha Christie'),
    ('978-0439708180', 'Harry Potter and the Sorcerers Stone', 'J.K. Rowling'),
    ('9780062315007', 'The Alchemist', 'Paulo Coelho'),
    ('9780062316110', 'Sapiens', 'Yuval Noah Harari'),
    ('9780735211292', 'Atomic Habits', 'James Clear'),
]

for isbn, title, author in books:
    result = get_book_details(isbn, title=title, author=author)
    cover = result.get('cover_image', 'MISSING')
    print(f'{title}: {cover}')
    time.sleep(1) # Slow run to avoid API rate limit
