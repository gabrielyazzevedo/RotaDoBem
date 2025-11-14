# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.controllers.entities import controller_rota
from app.middleware.auth import auth_required, roles_required, role_required
from flask_jwt_extended import get_jwt_identity

rota_routes = Blueprint('rota_routes', __name__)

@rota_routes.route('/rotas/calcular/<string:doacao_id>', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista']) # Admin ou Motorista podem calcular
def calcular_rota_para_doacao(doacao_id):
    """
    Endpoint que calcula e salva a melhor rota para uma doação.
    Se a rota já foi calculada, apenas retorna os dados salvos.
    """
    dados_completos, error = controller_rota.calcular_e_salvar_rota(doacao_id)
    
    if error:
        status_code = 404 if "não encontrada" in error else 400
        return jsonify({"erro": error}), status_code
    
    return jsonify(dados_completos), 200


@rota_routes.route('/rotas', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista']) # Admin e Motorista podem ver as rotas
def get_all_rotas():
    """Retorna todas as rotas, opcionalmente filtradas por status."""
    status = request.args.get('status') 
    rotas, error = controller_rota.get_todas_rotas(status)
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(rotas), 200

@rota_routes.route('/rotas/<string:rota_id>', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista']) # Admin ou motorista podem ver
def get_rota(rota_id):
    """Retorna uma rota específica pelo ID."""
    rota, error = controller_rota.get_rota_por_id(rota_id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(rota), 200

@rota_routes.route('/rotas/<string:rota_id>/atribuir', methods=['PUT'])
@auth_required
@role_required('admin') # Apenas admin atribui rotas
def atribuir_rota(rota_id):
    """Atribui um motorista a uma rota (JSON: {"motorista_id": "..."})."""
    data = request.get_json()
    motorista_id = data.get('motorista_id')
    if not motorista_id:
        return jsonify({"erro": "motorista_id é obrigatório"}), 400
        
    response, error = controller_rota.atribuir_motorista_rota(rota_id, motorista_id)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(response), 200

@rota_routes.route('/rotas/<string:rota_id>/status', methods=['PUT'])
@auth_required
@roles_required(['admin', 'motorista']) # Motorista pode concluir/cancelar
def atualizar_status_rota(rota_id):
    """
    Atualiza o status de uma rota (JSON: {"status": "concluida" | "cancelada"}).
    Usado pelo motorista ou admin.
    """
    data = request.get_json()
    novo_status = data.get('status')
    if not novo_status:
        return jsonify({"erro": "status é obrigatório"}), 400
        
    response, error = controller_rota.marcar_rota_status(rota_id, novo_status)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(response), 200