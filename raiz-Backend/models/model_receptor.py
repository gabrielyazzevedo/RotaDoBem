from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from config.db import connect_db
import re
from pydantic import Field
from bson import ObjectId

class Endereco(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @validator('cep')
    def validar_cep(cls, v):
        if not re.match(r'^\d{5}-\d{3}$', v):
            raise ValueError('Erro! CEP deve estar no formato 00000-000')
        return v

class ResponsavelLegal(BaseModel):
    nome_completo: str
    cpf: str
    cargo: str

    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('Erro! CPF deve estar no formato 000.000.000-00')
        return v

class Receptor(BaseModel):
    razao_social: str
    cnpj: str
    endereco: Endereco
    telefones: List[str] = []
    email: EmailStr
    responsavel_legal: ResponsavelLegal
    horario_disponibilidade: str
    declaracao_anvisa: bool
    tipo_receptor: str  # Ex:'ong', 'comunidade', 'individuo'
    tipos_alimentos_aceitos: List[str] = []  # Ex: 'fruta', 'enlatado', 'carne'
    necessidade_nutricional: Optional[List[str]] = []  # Ex:'baixo_acucar', 'sem_gluten', 'sem_lactose'
    numero_beneficiarios: int
    capacidade_armazenamento: str
    tipo_armazenamento: List[str] = []  # Ex:'geladeira', 'despensa'
    restricoes_recebimento: Optional[str] = None
    alvara_sanitario: bool

    @validator('cnpj')
    def validar_cnpj(cls, v):
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', v):
            raise ValueError('Erro! CNPJ deve estar no formato 00.000.000/0000-00')
        return v

    @validator('telefones')
    def validar_telefones(cls, v):
        for tel in v:
            if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', tel):
                raise ValueError('Erro! Telefone deve estar no formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX')
        return v

    @validator('numero_beneficiarios')
    def validar_beneficiarios(cls, v):
        if v < 0:
            raise ValueError('Erro! N�mero de benefici�rios deve ser n�o-negativo')
        return v

    def save(self):
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        result = db.receptores.insert_one(data)
        self.id = str(result.inserted_id)
        return self
    
    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        result = db.receptores.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.receptores.find_one({"_id": ObjectId(id)})
        if data:
            return cls(**data)
        return None

    @classmethod
    def find_all(cls):
        db = connect_db()
        receptores = list(db.receptores.find())
        for r in receptores:
            r['_id'] = str(r['_id'])
        return [cls(**r) for r in receptores]
    
    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        result = db.receptores.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        result = db.receptores.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0




