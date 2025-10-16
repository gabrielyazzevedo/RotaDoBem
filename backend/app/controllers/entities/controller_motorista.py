from app.models.entities.model_motorista import Motorista
from pydantic import ValidationError

def create_motorista(data):
    try:
        motorista = Motorista(**data)
        motorista.save()
        return motorista.dict(), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)

def get_all_motoristas():
    motoristas = Motorista.find_all()
    return [m.dict() for m in motoristas], None

def get_motorista(id):
    motorista = Motorista.find_by_id(id)
    if motorista:
        return motorista.dict(), None
    return None, "Motorista não encontrado."

# ... necessário adicionar delete