# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.controllers.entities import controller_motorista
from app.middleware.auth import auth_required, role_required

motorista_routes = Blueprint('motorista_routes', __name__)

@motorista_routes.route('/motoristas', methods=['POST'])
@auth_required
@role_required('admin') # Apenas Admin pode criar motoristas
def create():
    data = request.get_json()
    motorista, error = controller_motorista.create_motorista(data)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(motorista), 201

@motorista_routes.route('/motoristas', methods=['GET'])
@auth_required
@role_required('admin') # Apenas Admin pode ver a lista completa
def get_all():
    motoristas, error = controller_motorista.get_all_motoristas()
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(motoristas), 200

@motorista_routes.route('/motoristas/<string:id>', methods=['GET'])
@auth_required
def get_one(id):
    """Busca um motorista. Admin pode ver qualquer um, Motorista só pode ver a si mesmo."""
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get("role") != 'admin' and id_usuario_logado != id:
        return jsonify({"erro": "Acesso não autorizado"}), 403

    motorista, error = controller_motorista.get_motorista(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(motorista), 200

@motorista_routes.route('/motoristas/<string:id>', methods=['PUT'])
@auth_required
def update(id):
    """Atualiza um motorista. Admin pode atualizar qualquer um, Motorista só a si mesmo."""
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get("role") != 'admin' and id_usuario_logado != id:
        return jsonify({"erro": "Acesso não autorizado"}), 403
        
    data = request.get_json()
    response, error = controller_motorista.update_motorista(id, data)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@motorista_routes.route('/motoristas/<string:id>', methods=['DELETE'])
@auth_required
@role_required('admin') # Apenas Admin pode deletar motoristas
def delete(id):
    response, error = controller_motorista.delete_motorista(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200