# models/model_motorista.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from app.config.database import connect_db
from bson import ObjectId
import re

class Motorista(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    nome_completo: str
    cpf: str
    telefone: str
    email: EmailStr
    senha: str  # Deveria ser criptografado (hash)
    cnh: str
    placa_veiculo: str
    status: str = 'disponivel'  # Ex: 'disponivel', 'em_rota', 'inativo'

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF deve estar no formato 000.000.000-00')
        return v
    
    @validator('telefone')
    def validar_telefone(cls, v):
        if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', v):
            raise ValueError('Telefone deve estar no formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX')
        return v
    
    # --- Métodos do BD
    def save(self):
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        result = db.motoristas.insert_one(data)
        self.id = result.inserted_id
        return self

    @classmethod
    def find_all(cls):
        db = connect_db()
        motoristas = list(db.motoristas.find())
        return [cls(**m) for m in motoristas]

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.motoristas.find_one({"_id": ObjectId(id)})
        if data:
            return cls(**data)
        return None

    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        result = db.motoristas.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        result = db.motoristas.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0