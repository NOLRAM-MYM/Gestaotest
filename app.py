from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import datetime
import os
from config import Config
from models import db, User, Product, Client, Sale, Category
from forms import LoginForm, RegistrationForm, ProductForm, ClientForm, SaleForm, CategoryForm

# Importar rotas
from routes.auth import auth_bp
from routes.products import products_bp
from routes.clients import clients_bp
from routes.sales import sales_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(clients_bp, url_prefix='/clients')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Rota principal
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Context processors
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)