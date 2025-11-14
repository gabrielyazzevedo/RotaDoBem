# -*- coding: utf-8 -*-

from app.models.entities.model_usuarioUnificado import Motorista, RoleEnum
from pydantic import ValidationError

def create_motorista(data):
    """Cria um novo motorista usando o modelo unificado."""
    try:
        data['role'] = RoleEnum.MOTORISTA
        novo_motorista = Motorista(**data)
        

        novo_motorista.save() 
        
        motorista_dict = novo_motorista.dict()
        motorista_dict.pop('senha', None) 
        
        return motorista_dict, None
    except ValidationError as e:
        return None, e.errors()
    except ValueError as e: 
        return None, str(e)
    except Exception as e:
        return None, str(e)

def get_all_motoristas():
    """Busca todos os motoristas do banco."""
    try:
        motoristas = Motorista.find_all_by_role(RoleEnum.MOTORISTA)
        return [m.dict(exclude={'senha'}) for m in motoristas], None
    except Exception as e:
        return None, str(e)

def get_motorista(id):
    """Busca um motorista pelo ID."""
    motorista = Motorista.find_by_id(id)
    
    if motorista and motorista.role == RoleEnum.MOTORISTA:
        return motorista.dict(exclude={'senha'}), None
    
    return None, "Motorista não encontrado."

def update_motorista(id, data):
    """Atualiza os dados de um motorista."""
    try:
        success = Motorista.update_user(id, data, role_check=RoleEnum.MOTORISTA)
        
        if success:
            return {"mensagem": "Motorista atualizado com sucesso."}, None
        return None, "Motorista não encontrado ou dados inalterados."
    except Exception as e:
        return None, str(e)

def delete_motorista(id):
    """Deleta um motorista do banco."""
    try:
        success = Motorista.delete_user(id, role_check=RoleEnum.MOTORISTA)
        
        if success:
            return {"mensagem": "Motorista deletado com sucesso."}, None
        return None, "Motorista não encontrado."
    except Exception as e:
        return None, str(e)