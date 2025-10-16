# -*- coding: utf-8 -*-
"""
Rota do Bem - Backend Application
Factory pattern para criação da aplicação Flask
"""

from flask import Flask, send_from_directory
from app.config.database import connect_db
from app.middleware.auth import auth_required
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
    
    # Registrar blueprints
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
    
    return app
