# -*- coding: utf-8 -*-
# Crie em: backend/app/controllers/entities/controller_register.py

# Importa as classes que vamos criar
from app.models.entities.model_usuarioUnificado import Doador, Receptor, Motorista
from pydantic import ValidationError

def register_user(data):
    """
    Cria um novo usuário (Doador, Receptor ou Motorista) 
    com base no 'role' e nos dados complexos fornecidos.
    """
    
    if data.get('senha') != data.get('confirmar_senha'):
        return None, "Senhas não coincidem.", 400

    role = data.get('role')
    
    model_map = {
        "doador": Doador,
        "receptor": Receptor,
        "motorista": Motorista
    }
    
    UserClass = model_map.get(role)
    
    if not UserClass:
        return None, f"Tipo de usuário '{role}' é inválido.", 400
        
    try:
        # Pydantic tentará validar os dados aninhados (endereco, etc.)
        new_user = UserClass(**data)
        
        # O método save() criptografa a senha e checa email duplicado
        new_user.save()
        
        user_dict = new_user.dict(exclude={'senha'})
        
        return user_dict, None, 201 # 201 Created

    except ValidationError as e:
        # Se faltar CNPJ, Endereço, etc., o erro será pego aqui
        return None, e.errors(), 422 
    except ValueError as e:
        # Pega o erro de "email duplicado"
        return None, str(e), 400 
    except Exception as e:
        return None, str(e), 500