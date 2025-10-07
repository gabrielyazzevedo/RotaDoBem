from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from config.db import connect_db

class Estoque(BaseModel):
    alimento: str
    quantidade: float
    unidade: str 
    local: str
    data_atualizacao: datetime = datetime.now()

    @validator('quantidade')
    def quantidade_positiva(cls, v):
        if v < 0:
            raise ValueError('Quantidade deve ser não-negativa')
        return v

    def save(self):
        db = connect_db()
        result = db.estoque.insert_one(self.dict(exclude_unset=True))
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.estoque.find_one({"_id": id})
        if data:
            data['_id'] = str(data['_id'])
            return cls(**data)
        return None

    @classmethod
    def find_all(cls):
        db = connect_db()
        estoque = list(db.estoque.find())
        for e in estoque:
            e['_id'] = str(e['_id'])
        return [cls(**e) for e in estoque]




