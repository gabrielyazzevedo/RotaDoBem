# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from app.controllers.entities import controller_dashboard
from app.middleware.auth import auth_required

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/stats', methods=['GET'])
@auth_required 
def get_stats():
    """
    Endpoint para buscar as estatísticas do dashboard.
    O app.js (loadDashboard) chama esta rota.
    """
    stats, error = controller_dashboard.get_dashboard_stats()
    
    if error:
        return jsonify({"erro": error}), 500
    
    return jsonify(stats), 200
    