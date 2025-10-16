# -*- coding: utf-8 -*-
"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Database
    DB_URI = os.getenv('DB_URI', 'mongodb://localhost:27017/doacoesDB')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DB_URI = os.getenv('TEST_DB_URI', 'mongodb://localhost:27017/doacoesDB_test')

# Configuração por ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
