# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from app.controllers.entities import controller_admin
from app.middleware.auth import auth_required, role_required

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admins', methods=['POST'])
@auth_required
@role_required('admin')
def create():
    data = request.get_json()
    admin, error = controller_admin.create_admin(data)
    if error:
        return jsonify({"erro": error}), 422
    return jsonify(admin), 201

@admin_routes.route('/admins', methods=['GET'])
@auth_required
@role_required('admin')
def get_all():
    admins, error = controller_admin.get_all_admins()
    if error:
        return jsonify({"erro": error}), 500
    return jsonify(admins), 200

@admin_routes.route('/admins/<string:id>', methods=['GET'])
@auth_required
@role_required('admin')
def get_one(id):
    admin, error = controller_admin.get_admin(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(admin), 200

@admin_routes.route('/admins/<string:id>', methods=['PUT'])
@auth_required
@role_required('admin')
def update(id):
    data = request.get_json()
    response, error = controller_admin.update_admin(id, data)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200

@admin_routes.route('/admins/<string:id>', methods=['DELETE'])
@auth_required
@role_required('admin')
def delete(id):
    response, error = controller_admin.delete_admin(id)
    if error:
        return jsonify({"erro": error}), 404
    return jsonify(response), 200