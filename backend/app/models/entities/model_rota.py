# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from enum import Enum
from app.config.database import connect_db
from bson import ObjectId
from app.models.entities.model_usuarioUnificado import Endereco

# Helper para Pydantic V2 aceitar ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class StatusRotaEnum(str, Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"

class Rota(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias='_id')
    doacao_id: str
    motorista_id: Optional[str] = None
    status: StatusRotaEnum = StatusRotaEnum.PENDENTE
    
    # Dados de Endereço
    endereco_origem: Endereco
    endereco_destino: Endereco

    # Dados Google Maps
    distancia_texto: str
    duracao_texto: str
    resumo_rota: str
    google_maps_link: str

    # Datas
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_conclusao: Optional[datetime] = None

    # Configuração Pydantic V2
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )

    # --- Métodos do BD ---

    def save(self):
        db = connect_db()
        # mode='json' ajuda a converter sub-modelos (Endereço) corretamente
        data = self.model_dump(by_alias=True, exclude_none=True)
        
        if data.get('_id') is None:
            data.pop('_id', None)
        
        if self.id:
            db.rotas.update_one({"_id": ObjectId(self.id)}, {"$set": data})
        else:
            result = db.rotas.insert_one(data)
            self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        try: obj_id = ObjectId(id)
        except: return None
        db = connect_db()
        data = db.rotas.find_one({"_id": obj_id})
        if data: return cls(**data)
        return None

    @classmethod
    def find_by_doacao_id(cls, doacao_id: str):
        db = connect_db()
        data = db.rotas.find_one({"doacao_id": doacao_id})
        if data: return cls(**data)
        return None

    @classmethod
    def find_all(cls, query: dict = {}):
        db = connect_db()
        rotas = list(db.rotas.find(query))
        return [cls(**r) for r in rotas]

    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        
        # Limpeza de campos protegidos
        for f in ['_id', 'id', 'doacao_id']:
            data.pop(f, None)
        
        if data.get("status") == StatusRotaEnum.CONCLUIDA.value:
            data['data_conclusao'] = datetime.now()

        result = db.rotas.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        return db.rotas.delete_one({"_id": ObjectId(id)}).deleted_count > 0