# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.controllers.entities import controller_doador
from app.middleware.auth import auth_required

doador_routes = Blueprint('doador_routes', __name__)

@doador_routes.route('/doadores', methods=['POST'])
def create():
    data = request.get_json()
    doador, error = controller_doador.create_doador(data)
    if error:
        return jsonify({"erro": error}), 422
    return jsonify(doador), 201

@doador_routes.route('/doadores', methods=['GET'])
@auth_required
def get_all():
    doadores, error = controller_doador.get_all_doadores()
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(doadores), 200

@doador_routes.route('/doadores/<string:id>', methods=['GET'])
@auth_required
def get_one(id):
    id_do_usuario_logado = get_jwt_identity()
    if id_do_usuario_logado != id:
        return jsonify({"erro": "Acesso n�o autorizado para este recurso"}), 403

    doador, error = controller_doador.get_doador(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(doador), 200

@doador_routes.route('/doadores/<string:id>', methods=['PUT'])
@auth_required
def update(id):
    id_do_usuario_logado = get_jwt_identity()
    if id_do_usuario_logado != id:
        return jsonify({"erro": "Acesso n�o autorizado para este recurso"}), 403

    data = request.get_json()
    response, error = controller_doador.update_doador(id, data)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@doador_routes.route('/doadores/<string:id>', methods=['DELETE'])
@auth_required
def delete(id):
    id_do_usuario_logado = get_jwt_identity()
    if id_do_usuario_logado != id:
        return jsonify({"erro": "Acesso n�o autorizado para este recurso"}), 403

    response, error = controller_doador.delete_doador(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200