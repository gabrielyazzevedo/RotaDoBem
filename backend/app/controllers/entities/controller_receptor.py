# -*- coding: utf-8 -*-

from app.models.entities.model_usuarioUnificado import Receptor, RoleEnum
from pydantic import ValidationError

def create_receptor(data):
    try:
        data['role'] = RoleEnum.RECEPTOR
        novo_receptor = Receptor(**data)
        
        novo_receptor.save() 
        
        receptor_dict = novo_receptor.dict()
        receptor_dict.pop('senha', None) 
        
        return receptor_dict, None
    except ValidationError as e:
        return None, e.errors()
    except ValueError as e: # Captura erro de email duplicado
        return None, str(e)
    except Exception as e:
        return None, str(e)

def get_all_receptor():
    try:
        receptor = Receptor.find_all_by_role(RoleEnum.RECEPTOR)
        return [a.dict(exclude={'senha'}) for a in receptor], None
    except Exception as e:
        return None, str(e)

def get_receptor(id):
    receptor = receptor.find_by_id(id)
    
    if receptor and receptor.role == RoleEnum.RECEPTOR:
        return receptor.dict(exclude={'senha'}), None
    
    return None, "Receptor não encontrado."

def update_receptor(id, data):
    try:
        success = Receptor.update_user(id, data, role_check=RoleEnum.RECEPTOR)
        if success:
            return {"mensagem": "Receptor atualizado com sucesso."}, None
        return None, "Receptor não encontrado ou dados inalterados."
    except Exception as e:
        return None, str(e)

def delete_receptor(id):
    try:
        success = Receptor.delete_user(id, role_check=RoleEnum.RECEPTOR)
        if success:
            return {"mensagem": "Receptor deletado com sucesso."}, None
        return None, "Receptor não encontrado."
    except Exception as e:
        return None, str(e)