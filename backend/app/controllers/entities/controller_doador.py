from app.models.entities.model_usuarioUnificado import Doador, RoleEnum
from pydantic import ValidationError

def create_doador(data):
    try:
        data['role'] = RoleEnum.DOADOR
        novo_doador = Doador(**data)
        
        novo_doador.save() 
        
        doador_dict = novo_doador.dict()
        doador_dict.pop('senha', None) 
        
        return doador_dict, None
    except ValidationError as e:
        return None, e.errors()
    except ValueError as e: # Captura erro de email duplicado
        return None, str(e)
    except Exception as e:
        return None, str(e)

def get_all_doador():
    try:
        doador = Doador.find_all_by_role(RoleEnum.DOADOR)
        return [a.dict(exclude={'senha'}) for a in doador], None
    except Exception as e:
        return None, str(e)

def get_doador(id):
    doador = Doador.find_by_id(id)
    
    if doador and doador.role == RoleEnum.DOADOR:
        return doador.dict(exclude={'senha'}), None
    
    return None, "Doador não encontrado."

def update_doador(id, data):
    try:
        success = Doador.update_user(id, data, role_check=RoleEnum.DOADOR)
        if success:
            return {"mensagem": "Doador atualizado com sucesso."}, None
        return None, "Doador não encontrado ou dados inalterados."
    except Exception as e:
        return None, str(e)

def delete_doador(id):
    try:
        success = Doador.delete_user(id, role_check=RoleEnum.DOADOR)
        if success:
            return {"mensagem": "Doador deletado com sucesso."}, None
        return None, "Doador não encontrado."
    except Exception as e:
        return None, str(e)