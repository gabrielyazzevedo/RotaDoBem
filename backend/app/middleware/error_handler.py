# -*- coding: utf-8 -*-
"""
Handler global de erros da aplicação
"""
from flask import jsonify
from app.exceptions.custom_exceptions import RotaDoBemException

def register_error_handlers(app):
    """Registra os handlers de erro na aplicação"""
    
    @app.errorhandler(RotaDoBemException)
    def handle_custom_exception(error):
        return jsonify({
            'error': error.message,
            'status_code': error.status_code
        }), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Endpoint não encontrado',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'error': 'Erro interno do servidor',
            'status_code': 500
        }), 500
    
    @app.errorhandler(422)
    def handle_validation_error(error):
        return jsonify({
            'error': 'Erro de validação',
            'status_code': 422
        }), 422
