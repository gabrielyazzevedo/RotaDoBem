# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.controllers.entities import controller_estoque
from app.middleware.auth import auth_required, role_required

estoque_routes = Blueprint('estoque_routes', __name__)

@estoque_routes.route('/receptores/<string:receptor_id>/estoque', methods=['GET'])
@auth_required
def get_estoque_por_receptor(receptor_id):
    """
    Endpoint para VISUALIZAR o estoque de um receptor.
    Acesso permitido para o próprio receptor ou para um admin.
    """
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get("role") != 'admin' and id_usuario_logado != receptor_id:
        return jsonify({"erro": "Acesso não autorizado"}), 403

    itens, error = controller_estoque.listar_estoque_por_receptor(receptor_id)
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(itens), 200

@estoque_routes.route('/estoque/<string:item_id>', methods=['GET'])
@auth_required
def get_item(item_id):
    """
    Pega um item de estoque específico.
    A autorização (verificar se o item pertence ao usuário logado)
    deve ser feita dentro do controller.
    """
    item, error = controller_estoque.get_item_por_id(item_id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(item), 200

@estoque_routes.route('/estoque', methods=['POST'])
@auth_required
@role_required('admin')
def add_item_manualmente():
    """
    Endpoint para ADICIONAR um item manualmente (restrito a admins).
    """
    data = request.get_json()
    item, error = controller_estoque.adicionar_item_ao_estoque(data)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(item), 201

@estoque_routes.route('/estoque/<string:item_id>', methods=['PUT'])
@auth_required
@role_required('admin')
def ajustar_item(item_id):
    """
    Endpoint para AJUSTAR a quantidade de um item (restrito a admins).
    """
    data = request.get_json()
    response, error = controller_estoque.ajustar_quantidade_item(item_id, data)
    if error:
        return jsonify({"erro": error}), 400
    return jsonify(response), 200

@estoque_routes.route('/estoque/<string:item_id>/baixa', methods=['PUT'])
@auth_required 
def dar_baixa_item(item_id):
    """
    Endpoint para RECEPTOR ou ADMIN registrar a SAÍDA de um item do estoque.
    O JSON deve conter: {"quantidade": valor_da_saida}
    """
    id_usuario_logado = get_jwt_identity()
    claims = get_jwt() 
    data = request.get_json()
    
    response, error = controller_estoque.dar_baixa_estoque(item_id, data, id_usuario_logado, claims)
    
    if error:
        status_code = 403 if "Acesso não autorizado" in error else 400
        return jsonify({"erro": error}), status_code
    
    return jsonify(response), 200