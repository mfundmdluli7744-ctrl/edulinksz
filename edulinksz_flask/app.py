from flask import Flask, render_template, redirect, url_for, request
from extensions import db, login_manager
from models import User, SchoolProfile
from werkzeug.security import generate_password_hash

import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-edulinksz')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///edulinksz.db')
    # Handle Heroku's postgres:// vs postgresql://
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import blueprints
    from auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.parent import parent_bp
    from routes.principal import principal_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    app.register_blueprint(principal_bp, url_prefix='/principal')
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.before_request
    def log_request_info():
        app.logger.debug('Path: %s', request.path)

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.error('404 Error: %s at %s', e, request.path)
        return "404 - Not Found - The route is missing in app.py", 404

    return app

app = create_app()

if __name__ == '__main__':
    # Use Render PORT, bind to 0.0.0.0, no debug in production
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
