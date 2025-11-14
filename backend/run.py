# -*- coding: utf-8 -*-
"""
Ponto de entrada da aplicação Rota do Bem
Sistema de doações de alimentos
"""
from app import create_app
from app.config.settings import config
from app.middleware.error_handler import register_error_handlers
import os

def main():
    """Função principal para executar a aplicação"""
    app = create_app()
    
    # Configuração do ambiente
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[env])
    
    # Registrar handlers de erro
    register_error_handlers(app)
    
    # Configurações de execução
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = app.config.get('DEBUG', True)
    
    print("=" * 50)
    print("    Rota do Bem - Backend API")
    print("=" * 50)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📡 API: http://{host}:{port}/api")
    print(f"🔧 Modo: {env}")
    print(f"🐛 Debug: {'Ativado' if debug else 'Desativado'}")
    print("=" * 50)
    print("💡 Pressione Ctrl+C para parar o servidor")
    print("-" * 50)
 
    app.run(
        host=host,
        port=port,
        debug=debug
    )

if __name__ == '__main__':
    main()