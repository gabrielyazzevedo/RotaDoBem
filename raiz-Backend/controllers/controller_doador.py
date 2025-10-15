from models.model_doador import Doador
from pydantic import ValidationError

def create_doador(data):
    try:
        novo_doador = Doador(**data)
        novo_doador.save()
        return novo_doador.dict(), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)

def get_all_doadores():
    try:
        doadores = Doador.find_all()
        return [doador.dict() for doador in doadores], None
    except Exception as e:
        return None, str(e)

def get_doador(id):
    doador = Doador.find_by_id(id)
    if doador:
        return doador.dict(), None
    return None, "Doador não encontrado."

def update_doador(id, data):
    if not Doador.find_by_id(id):
        return None, "Doador não encontrado."

    if Doador.update(id, data):
        return {"mensagem": "Doador atualizado com sucesso."}, None
    return None, "Dados inalterados ou erro ao atualizar."

def delete_doador(id):
    if Doador.delete(id):
        return {"mensagem": "Doador deletado com sucesso."}, None
    return None, "Doador não encontrado."