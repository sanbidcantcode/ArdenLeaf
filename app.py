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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
