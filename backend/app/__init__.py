# -*- coding: utf-8 -*-

from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager 
from app.config.database import connect_db
from app.middleware.auth import auth_required
from app.routes.route_auth import auth_routes
from app.routes.route_dashboard import dashboard_routes 
from app.routes.route_admin import admin_routes
from app.routes.route_doador import doador_routes
from app.routes.route_receptor import receptor_routes
from app.routes.route_doacao import doacao_routes
from app.routes.route_estoque import estoque_routes
from app.routes.route_motorista import motorista_routes
from app.routes.route_rota import rota_routes

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    
    jwt = JWTManager(app)
    
    # Blueprints
    app.register_blueprint(auth_routes, url_prefix='/api')  
    app.register_blueprint(dashboard_routes, url_prefix='/api')
    app.register_blueprint(admin_routes, url_prefix='/api')
    app.register_blueprint(doador_routes, url_prefix='/api')
    app.register_blueprint(receptor_routes, url_prefix='/api')
    app.register_blueprint(doacao_routes, url_prefix='/api')
    app.register_blueprint(estoque_routes, url_prefix='/api')
    app.register_blueprint(motorista_routes, url_prefix='/api')
    app.register_blueprint(rota_routes, url_prefix='/api')
    
    # Rota principal
    @app.route("/")
    def index():
        return send_from_directory('../../frontend', 'index.html')

    @app.route("/api")
    def index_api():
        return {
            "status": "API Rota do Bem está no ar!",
            "versao": "1.0.0"
        }

    # Rota para a página de Login
    @app.route("/login")
    def login_page():
        return send_from_directory('../../frontend', 'login.html')

    # Rota para o Dashboard
    @app.route("/dashboard")
    def dashboard_page():
        return send_from_directory('../../frontend', 'dashboard.html')

    @app.route("/register")
    def register_page():
        return send_from_directory('../../frontend', 'register.html')
        
    # Rotas para CSS e JS 
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory('../../frontend/css', filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory('../../frontend/js', filename)

    @app.route('/images/<path:filename>')
    def serve_images(filename):
        return send_from_directory('../../frontend/images', filename)
    
    return app