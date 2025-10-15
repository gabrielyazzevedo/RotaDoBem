from models.model_receptor import Receptor
from pydantic import ValidationError

def create_receptor(data):
    try:
        novo_receptor = Receptor(**data)
        novo_receptor.save()
        return novo_receptor.dict(), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)

def get_all_receptores():
    try:
        receptores = Receptor.find_all()
        return [receptor.dict() for receptor in receptores], None
    except Exception as e:
        return None, str(e)

def get_receptor(id):
    receptor = Receptor.find_by_id(id)
    if receptor:
        return receptor.dict(), None
    return None, "Receptor não encontrado."

def update_receptor(id, data):
    if not Receptor.find_by_id(id):
        return None, "Receptor não encontrado."

    if Receptor.update(id, data):
        return {"mensagem": "Receptor atualizado com sucesso."}, None
    return None, "Dados inalterados ou erro ao atualizar."

def delete_receptor(id):
    if Receptor.delete(id):
        return {"mensagem": "Receptor deletado com sucesso."}, None
    return None, "Receptor não encontrado."