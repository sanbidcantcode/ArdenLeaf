from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.book_routes import book_bp
    from routes.loan_routes import loan_bp
    from routes.profile_routes import profile_bp
    from routes.admin_routes import admin_bp
    from routes.owner_routes import owner_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(owner_bp, url_prefix='/owner')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', code=500, message="Internal server error"), 500

    return app

def prewarm_cache():
    from models.book import Book
    from utils.google_books import get_book_details
    from utils.book_cache import is_cached
    import threading
    import time
    
    def _warm():
        try:
            # Add a startup delay so the app is fully ready
            time.sleep(2)
            books = Book.search('')
            print(f"[prewarm] Starting cache check for {len(books)} books...")
            for book in books:
                isbn = book['ISBN']
                if not is_cached(isbn):
                    get_book_details(isbn, title=book.get('Title'), author=book.get('Authors'))
                    time.sleep(0.5) # Gentle rate protection
            print('[prewarm] Cache warming complete.')
        except Exception as e:
            print(f'[prewarm] Error: {e}')
    
    t = threading.Thread(target=_warm, daemon=True)
    t.start()

if __name__ == '__main__':
    app = create_app()
    prewarm_cache()
    app.run(debug=True)
