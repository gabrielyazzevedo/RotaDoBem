from pydantic import BaseModel, validator
from typing import Optional
from datetime import date
from config.db import connect_db

class Doacao(BaseModel):
    doador_id: str
    alimento: str
    quantidade: float
    unidade: str  
    validade: date
    status: str = 'pendente'  # 'pendente', 'aceita', 'à caminho', 'expirada'
    data_criacao: date = date.today()
    receptor_id: Optional[str] = None

    @validator('quantidade')
    def quantidade_positiva(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser positiva')
        return v

    @validator('status')
    def validar_status(cls, v):
        if v not in ['pendente', 'aceita', 'à caminho', 'expirada']:
            raise ValueError('Status inválido')
        return v

    def save(self):
        db = connect_db()
        result = db.doacoes.insert_one(self.dict(exclude_unset=True))
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.doacoes.find_one({"_id": id})
        if data:
            data['_id'] = str(data['_id'])
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




