# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from controllers import controller_receptor
from middleware.auth import auth_required, role_required

receptor_routes = Blueprint('receptor_routes', __name__)

@receptor_routes.route('/receptores', methods=['POST'])
@auth_required
@role_required('admin')
def create():
    data = request.get_json()
    receptor, error = controller_receptor.create_receptor(data)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(receptor), 201

@receptor_routes.route('/receptores', methods=['GET'])
@auth_required
@role_required('admin')
def get_all():
    receptores, error = controller_receptor.get_all_receptores()
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(receptores), 200

@receptor_routes.route('/receptores/<string:id>', methods=['GET'])
@auth_required
def get_one(id):
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != 'admin' and id_usuario_logado != id:
        return jsonify({"erro": "Acesso n�o autorizado"}), 403

    receptor, error = controller_receptor.get_one_receptor(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(receptor), 200

@receptor_routes.route('/receptores/<string:id>', methods=['PUT'])
@auth_required
def update(id):
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != 'admin' and id_usuario_logado != id:
        return jsonify({"erro": "Acesso n�o autorizado"}), 403

    data = request.get_json()
    response, error = controller_receptor.update_receptor(id, data)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@receptor_routes.route('/receptores/<string:id>', methods=['DELETE'])
@auth_required
@role_required('admin')
def delete(id):
    response, error = controller_receptor.delete_receptor(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200