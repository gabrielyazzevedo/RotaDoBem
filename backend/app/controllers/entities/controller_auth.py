# -*- coding: utf-8 -*-

from app.models.entities.model_usuarioUnificado import Usuario
from flask_jwt_extended import create_access_token
from datetime import timedelta

def login(data):
    """
    Processa a tentativa de login.
    """
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return None, "Email e senha são obrigatórios.", 400

    usuario = Usuario.find_by_email(email)

    if not usuario:
        return None, "Usuário não encontrado.", 404

    if not usuario.check_password(senha):
        return None, "Credenciais inválidas.", 401
    
    # Cria o token JWT se a senha estiver correta
    expires = timedelta(hours=8) 
    
    additional_claims = {
        "role": usuario.role.value, 
        "nome": usuario.nome
    }
    
    access_token = create_access_token(
        identity=str(usuario.id),
        additional_claims=additional_claims,
        expires_delta=expires
    )
    
    # Retorna o token e os dados do usuário
    return {
        "access_token": access_token, 
        "role": usuario.role.value, 
        "id": str(usuario.id)
    }, None, 200