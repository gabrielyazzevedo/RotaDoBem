from app.models.entities.model_usuarioUnificado import Admin, RoleEnum
from pydantic import ValidationError

def create_admin(data):
    try:
        data['role'] = RoleEnum.ADMIN
        novo_admin = Admin(**data)
        
        novo_admin.save() 
        
        admin_dict = novo_admin.dict()
        admin_dict.pop('senha', None) 
        
        return admin_dict, None
    except ValidationError as e:
        return None, e.errors()
    except ValueError as e: # Captura erro de email duplicado
        return None, str(e)
    except Exception as e:
        return None, str(e)

def get_all_admins():
    try:
        admins = Admin.find_all_by_role(RoleEnum.ADMIN)
        return [a.dict(exclude={'senha'}) for a in admins], None
    except Exception as e:
        return None, str(e)

def get_admin(id):
    admin = Admin.find_by_id(id)
    
    if admin and admin.role == RoleEnum.ADMIN:
        return admin.dict(exclude={'senha'}), None
    
    return None, "Admin não encontrado."

def update_admin(id, data):
    try:
        success = Admin.update_user(id, data, role_check=RoleEnum.ADMIN)
        if success:
            return {"mensagem": "Admin atualizado com sucesso."}, None
        return None, "Admin não encontrado ou dados inalterados."
    except Exception as e:
        return None, str(e)

def delete_admin(id):
    try:
        success = Admin.delete_user(id, role_check=RoleEnum.ADMIN)
        if success:
            return {"mensagem": "Admin deletado com sucesso."}, None
        return None, "Admin não encontrado."
    except Exception as e:
        return None, str(e)