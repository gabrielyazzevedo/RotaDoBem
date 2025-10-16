from pydantic import BaseModel, validator
from typing import Optional
from datetime import date
from app.config.database import connect_db
from pydantic import Field
from bson import ObjectId

class Doacao(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    doador_id: str
    alimento: str
    quantidade: float
    unidade: str  
    validade: date
    status: str = 'pendente'  # 'pendente', 'aceita', '� caminho', 'expirada'
    data_criacao: date = date.today()
    receptor_id: Optional[str] = None
    motorista_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @validator('quantidade')
    def quantidade_positiva(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser positiva')
        return v

    @validator('status')
    def validar_status(cls, v):
        if v not in ['pendente', 'aceita', '� caminho', 'expirada']:
            raise ValueError('Status inv�lido')
        return v

    def save(self):
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        result = db.doacoes.insert_one(data)
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.doacoes.find_one({"_id": ObjectId(id)})
        if data:
            return cls(**data) 
        return None

    @classmethod
    def find_all(cls, status: Optional[str] = None):
        db = connect_db()
        query = {}
        if status:
            query['status'] = status
        doacoes = list(db.doacoes.find(query))
        for d in doacoes:
            d['_id'] = str(d['_id'])
        return [cls(**d) for d in doacoes]
    
    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        result = db.doacoes.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        result = db.doacoes.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0




