# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from app.controllers.entities import controller_auth, controller_register

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login. Recebe JSON com email e senha.
    Retorna um token JWT se for bem-sucedido.
    """
    data = request.get_json()
    response, error, status_code = controller_auth.login(data)
    
    if error:
        return jsonify({"erro": error}), status_code
    
    return jsonify(response), status_code

@auth_routes.route('/register', methods=['POST'])
def register():
    """
    Endpoint de registro público.
    Recebe o JSON complexo do formulário de registro inteligente.
    """
    data = request.get_json()
    response, error, status_code = controller_register.register_user(data)
    
    if error:
        return jsonify({"erro": error}), status_code
    
    return jsonify(response), status_code