# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from app.controllers.entities import controller_rota
from app.middleware.auth import auth_required, roles_required

rota_routes = Blueprint('rota_routes', __name__)

@rota_routes.route('/rotas/calcular/<string:doacao_id>', methods=['GET'])
@auth_required
@roles_required(['admin', 'motorista'])
def calcular_rota_para_doacao(doacao_id):
    """
    Endpoint que calcula a melhor rota para uma doação.
    Acesso restrito a administradores e motoristas.
    """
    dados_completos, error = controller_rota.calcular_melhor_rota(doacao_id)
    
    if error:
        status_code = 404 if "não encontrada" in error else 400
        return jsonify({"erro": error}), status_code
    
    return jsonify(dados_completos), 200