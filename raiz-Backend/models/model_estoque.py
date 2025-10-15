from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from config.db import connect_db
from bson import ObjectId

class Estoque(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    receptor_id: str  # IMPORTANTE: Adicionar a referência ao receptor
    alimento: str
    quantidade: float
    unidade: str 
    local: Optional[str] = None # Onde está armazenado (ex: 'geladeira 1', 'prateleira A')
    data_atualizacao: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @validator('quantidade')
    def quantidade_nao_negativa(cls, v):
        if v < 0:
            raise ValueError('Quantidade não pode ser negativa')
        return v

    # --- Métodos do BD

    def save(self):
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        result = db.estoque.insert_one(data)
        self.id = result.inserted_id
        return self

    @classmethod
    def find_by_receptor_id(cls, receptor_id: str):
        db = connect_db()
        itens = list(db.estoque.find({"receptor_id": receptor_id}))
        return [cls(**item) for item in itens]

    @classmethod
    def find_one_by_details(cls, receptor_id: str, alimento: str, unidade: str):
        db = connect_db()
        data = db.estoque.find_one({
            "receptor_id": receptor_id,
            "alimento": alimento,
            "unidade": unidade
        })
        if data:
            return cls(**data)
        return None
        
    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.estoque.find_one({"_id": ObjectId(id)})
        if data:
            return cls(**data)
        return None

    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        # Atualiza a data quando uma alteração for feita
        data['data_atualizacao'] = datetime.now()
        result = db.estoque.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def increment_quantity(cls, id: str, quantidade: float):
        db = connect_db()
        result = db.estoque.update_one(
            {"_id": ObjectId(id)},
            {
                "$inc": {"quantidade": quantidade},
                "$set": {"data_atualizacao": datetime.now()}
            }
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        result = db.estoque.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0