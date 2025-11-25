# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.controllers.entities import controller_doacao
from app.middleware.auth import auth_required

doacao_routes = Blueprint('doacao_routes', __name__)

@doacao_routes.route('/doacoes', methods=['POST'])
@auth_required
def create():
    id_doador = get_jwt_identity()
    data = request.get_json()
    doacao, error = controller_doacao.create_doacao(data, id_doador)
    if error:
        return jsonify({"erro": error}), 422
    return jsonify(doacao), 201

@doacao_routes.route('/doacoes', methods=['GET'])
@auth_required
def get_all():
    claims = get_jwt() 
    status = request.args.get('status') 
    doacoes, error = controller_doacao.get_all_doacoes(claims, status)
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(doacoes), 200

@doacao_routes.route('/doacoes/<string:id>/aceitar', methods=['PUT'])
@auth_required
def aceitar(id):
    """Receptor aceita uma doação pendente"""
    id_receptor = get_jwt_identity() # Pega o ID do token de quem está clicando
    claims = get_jwt()
    
    if claims.get('role') != 'receptor':
        return jsonify({"erro": "Apenas receptores podem aceitar doações."}), 403
        
    response, error = controller_doacao.aceitar_doacao(id, id_receptor)
    
    if error:
        return jsonify({"erro": error}), 400
    
    return jsonify(response), 200

@doacao_routes.route('/doacoes/<string:id>', methods=['GET'])
@auth_required
def get_one(id):
    doacao, error = controller_doacao.get_doacao(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(doacao), 200

@doacao_routes.route('/doacoes/<string:id>', methods=['PUT'])
@auth_required
def update(id):
    data = request.get_json()
    response, error = controller_doacao.update_doacao(id, data)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@doacao_routes.route('/doacoes/<string:id>', methods=['DELETE'])
@auth_required
def delete(id):
    response, error = controller_doacao.delete_doacao(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@doacao_routes.route('/doacoes/<string:id>/atribuir', methods=['PUT'])
@auth_required
def atribuir(id):
    data = request.get_json()
    response, error = controller_doacao.atribuir_motorista(id, data)
    if error:
        status_code = 404 if "não encontrada" in error else 400
        return jsonify({"erro": error}), status_code
    
    return jsonify(response), 200