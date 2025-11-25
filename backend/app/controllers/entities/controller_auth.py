# -*- coding: utf-8 -*-
from app.models.entities.model_usuarioUnificado import Usuario
from flask_jwt_extended import create_access_token
from datetime import timedelta
import traceback
from enum import Enum

def login(data):
    """
    Processa a tentativa de login com tratamento de erros robusto.
    """
    try:
        email = data.get('email')
        senha = data.get('senha')

        if not email or not senha:
            return None, "Email e senha são obrigatórios.", 400

        # Busca o usuário
        usuario = Usuario.find_by_email(email)

        if not usuario:
            return None, "Usuário não encontrado.", 404

        if not usuario.check_password(senha):
            return None, "Credenciais inválidas.", 401
        
        # --- CORREÇÃO AQUI ---
        # Verifica se 'role' é um Enum ou string pura
        user_role = usuario.role
        if isinstance(user_role, Enum):
            role_value = user_role.value
        else:
            role_value = str(user_role)
        # ---------------------

        # Cria o token JWT
        expires = timedelta(hours=8) 
        
        additional_claims = {
            "role": role_value, 
            "nome": usuario.nome
        }
        
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims=additional_claims,
            expires_delta=expires
        )
        
        return {
            "access_token": access_token, 
            "role": role_value, 
            "id": str(usuario.id)
        }, None, 200

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NO LOGIN: {str(e)}")
        traceback.print_exc()
        return None, f"Erro interno do servidor: {str(e)}", 500