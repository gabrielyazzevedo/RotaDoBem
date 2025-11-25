# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.controllers.entities import controller_rota
from app.middleware.auth import auth_required, roles_required, role_required
from flask_jwt_extended import get_jwt_identity

rota_routes = Blueprint('rota_routes', __name__)

@rota_routes.route('/rotas/calcular/<string:doacao_id>', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista']) 
def calcular_rota_para_doacao(doacao_id):
    dados_completos, error = controller_rota.calcular_e_salvar_rota(doacao_id)
    status_code = 404 if error and "não encontrada" in error else 400 if error else 200
    if error: return jsonify({"erro": error}), status_code
    return jsonify(dados_completos), 200

@rota_routes.route('/rotas', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista', 'receptor']) # Receptor também pode precisar ver status
def get_all_rotas():
    status = request.args.get('status') 
    rotas, error = controller_rota.get_todas_rotas(status)
    if error: return jsonify({"erro": error}), 500
    return jsonify(rotas), 200

@rota_routes.route('/rotas/<string:rota_id>', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista']) 
def get_rota(rota_id):
    rota, error = controller_rota.get_rota_por_id(rota_id)
    if error: return jsonify({"erro": error}), 404
    return jsonify(rota), 200

# --- CORREÇÃO PRINCIPAL AQUI ---
@rota_routes.route('/rotas/<string:rota_id>/atribuir', methods=['PUT'])
@auth_required
@roles_required(['admin', 'motorista']) # AGORA MOTORISTA PODE ACEITAR!
def atribuir_rota(rota_id):
    data = request.get_json()
    motorista_id = data.get('motorista_id')
    
    # Se não vier ID no JSON (caso do motorista aceitando a própria corrida),
    # tentamos pegar do token de quem está logado.
    if not motorista_id:
        motorista_id = get_jwt_identity()

    response, error = controller_rota.atribuir_motorista_rota(rota_id, motorista_id)
    
    if error: return jsonify({"erro": error}), 400
    return jsonify(response), 200

@rota_routes.route('/rotas/<string:rota_id>/status', methods=['PUT'])
@auth_required
@roles_required(['admin', 'motorista'])
def atualizar_status_rota(rota_id):
    data = request.get_json()
    novo_status = data.get('status')
    if not novo_status: return jsonify({"erro": "status é obrigatório"}), 400
        
    response, error = controller_rota.marcar_rota_status(rota_id, novo_status)
    if error: return jsonify({"erro": error}), 400
    return jsonify(response), 200