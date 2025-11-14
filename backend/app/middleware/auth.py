# -*- coding: utf-8 -*-
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from jwt.exceptions import ExpiredSignatureError

# Decorator para verificar se o usuario esta logado
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except (NoAuthorizationError, InvalidHeaderError) as e:
            return jsonify({
                "error": "Cabecalho de autorizacao ausente ou invalido.",
                "details": str(e)
            }), 401
        except ExpiredSignatureError as e:
            return jsonify({
                "error": "Token de acesso expirado.",
                "details": str(e)
            }), 401
        except Exception as e:
            return jsonify({
                "error": "Nao foi possivel validar o token de acesso.",
                "details": str(e)
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar se o usuario tem a permissao (role) necessaria
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != required_role:
                return jsonify({"error": f"Acesso restrito. Requer permissao de '{required_role}'."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def roles_required(required_roles):
    """
    Decorator que verifica se o usuario tem uma das roles necessarias.
    Recebe uma lista de roles permitidas.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in required_roles:
                return jsonify({"error": "Acesso restrito. Permissao insuficiente."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator