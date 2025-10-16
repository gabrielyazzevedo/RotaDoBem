from app.models.entities.model_admin import Admin
from pydantic import ValidationError

def create_admin(data):
    try:
        novo_admin = Admin(**data)
        novo_admin.save()
        return novo_admin.dict(), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)

def get_all_admins():
    try:
        admins = Admin.find_all()
        return [admin.dict() for admin in admins], None
    except Exception as e:
        return None, str(e)

def get_admin(id):
    admin = Admin.find_by_id(id)
    if admin:
        return admin.dict(), None
    return None, "Admin não encontrado."

def update_admin(id, data):
    if not Admin.find_by_id(id):
        return None, "Admin não encontrado."

    if Admin.update(id, data):
        return {"mensagem": "Admin atualizado com sucesso."}, None
    return None, "Dados inalterados ou erro ao atualizar."

def delete_admin(id):
    if Admin.delete(id):
        return {"mensagem": "Admin deletado com sucesso."}, None
    return None, "Admin não encontrado."