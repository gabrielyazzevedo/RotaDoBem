# -*- coding: utf-8 -*-
from pydantic import BaseModel, validator, Field, BeforeValidator, ConfigDict
from typing import Optional, Annotated
from datetime import date, datetime, time
from app.config.database import connect_db
from bson import ObjectId

# Helper para aceitar ObjectId como string
PyObjectId = Annotated[str, BeforeValidator(str)]

class Doacao(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias='_id')
    doador_id: str
    alimento: str
    quantidade: float
    unidade: str  
    validade: datetime 
    status: str = 'pendente' 
    data_criacao: datetime = Field(default_factory=datetime.now)
    receptor_id: Optional[str] = None
    motorista_id: Optional[str] = None

    # Configuração Pydantic V2
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    @validator('quantidade')
    def quantidade_positiva(cls, v):
        if v <= 0: raise ValueError('Quantidade deve ser positiva')
        return v

    @validator('status')
    def validar_status(cls, v):
        permitidos = ['pendente', 'aceita', 'a caminho', 'recebida', 'expirada']
        if v not in permitidos: raise ValueError(f'Status inválido.')
        return v

    # --- DB METHODS ---
    def save(self):
        db = connect_db()
        data = self.model_dump(by_alias=True, exclude_none=True)
        
        if data.get('_id') is None: data.pop('_id', None)

        # Converter data para datetime para o Mongo aceitar
        if isinstance(data.get('validade'), date) and not isinstance(data.get('validade'), datetime):
             data['validade'] = datetime.combine(data['validade'], time.min)

        if self.id:
             db.doacoes.update_one({"_id": ObjectId(self.id)}, {"$set": data})
        else:
             result = db.doacoes.insert_one(data)
             self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        try: obj_id = ObjectId(id)
        except: return None
        db = connect_db()
        data = db.doacoes.find_one({"_id": obj_id})
        if not data: return None
        return cls(**data) 

    @classmethod
    def find_all(cls, query: dict = {}):
        db = connect_db()
        doacoes = list(db.doacoes.find(query)) 
        return [cls(**d) for d in doacoes]
    
    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        return db.doacoes.update_one({"_id": ObjectId(id)}, {"$set": data}).modified_count > 0

    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        return db.doacoes.delete_one({"_id": ObjectId(id)}).deleted_count > 0