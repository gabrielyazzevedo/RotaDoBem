# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from app.config.database import connect_db
from bson import ObjectId
from app.models.entities.model_usuarioUnificado import Endereco

class StatusRotaEnum(str, Enum):
    """Define os status possíveis de uma rota."""
    PENDENTE = "pendente"       # Rota calculada, aguardando motorista
    EM_ANDAMENTO = "em_andamento" # Motorista aceitou e está a caminho
    CONCLUIDA = "concluida"     # Motorista finalizou a entrega
    CANCELADA = "cancelada"     # Rota foi cancelada

class Rota(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    doacao_id: str  # ID da doação que esta rota atende
    motorista_id: Optional[str] = None # ID do motorista (atribuído depois)
    status: StatusRotaEnum = StatusRotaEnum.PENDENTE
    
    # Dados da Origem (Doador) e Destino (Receptor)
    endereco_origem: Endereco
    endereco_destino: Endereco

    # Dados calculados pelo Google Maps (controller_rota)
    distancia_texto: str
    duracao_texto: str
    resumo_rota: str
    google_maps_link: str

    # Tempo para controle
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_conclusao: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True # Salva "pendente" no DB"

    # --- Métodos do BD ---

    def save(self):
        """Salva ou atualiza uma rota no banco de dados."""
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        
        if self.id: # Se tem ID, é um update
            db.rotas.update_one({"_id": self.id}, {"$set": data})
        else: # Se não tem ID, é um insert
            result = db.rotas.insert_one(data)
            self.id = result.inserted_id
        return self

    @classmethod
    def find_by_id(cls, id: str):
        """Busca uma rota pelo seu ID."""
        db = connect_db()
        try:
            data = db.rotas.find_one({"_id": ObjectId(id)})
            if data:
                return cls(**data)
        except:
            return None
        return None

    @classmethod
    def find_by_doacao_id(cls, doacao_id: str):
        """Busca uma rota pelo ID da doação."""
        db = connect_db()
        data = db.rotas.find_one({"doacao_id": doacao_id})
        if data:
            return cls(**data)
        return None

    @classmethod
    def find_all(cls, query: dict = {}):
        """Busca todas as rotas (ou filtra por uma query)."""
        db = connect_db()
        rotas = list(db.rotas.find(query))
        return [cls(**r) for r in rotas]

    @classmethod
    def update(cls, id: str, data: dict):
        """Atualiza campos específicos de uma rota."""
        db = connect_db()
        
        # Garante que dados sensíveis não sejam sobrescritos
        data.pop('_id', None)
        data.pop('id', None)
        data.pop('doacao_id', None) # Não deve mudar a doação de uma rota
        
        # Se o status for concluida, atualiza a data de conclusão
        if data.get("status") == StatusRotaEnum.CONCLUIDA.value:
            data['data_conclusao'] = datetime.now()

        result = db.rotas.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, id: str):
        """Deleta uma rota."""
        db = connect_db()
        try:
            result = db.rotas.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except:
            return False