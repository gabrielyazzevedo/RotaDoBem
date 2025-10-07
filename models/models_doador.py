from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from config.db import connect_db
import re
from enum import Enum


class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str

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

class TipoDoadorEnum(str, Enum):
    """Doadores permitidos."""
    MERCADO = "mercado"
    FEIRANTE = "feirante"
    FABRICA = "fabrica alimenticia"
    COMERCIO = "comércio alimenticio"


class Doador(BaseModel):
    razao_social: str
    cnpj: str
    endereco: Endereco
    telefones: List[str] = []
    email: EmailStr
    responsavel_legal: ResponsavelLegal
    horario_disponibilidade: str
    declaracao_anvisa: bool
    
    tipo_doador: TipoDoadorEnum 
    
    tipos_alimentos: List[str] = []  # Ex:'fruta', 'enlatado', 'carne'
    frequencia_doacao: str  # 'diario', 'semanal', 'mensal', 'esporadico'
    capacidade_armazenamento: Optional[str] = None

    @validator('cnpj')
    def validar_cnpj(cls, v):
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', v):
            raise ValueError('Erro! CNPJ deve estar no formato 00.000.000/0000-00')
        return v


    @validator('frequencia_doacao')
    def validar_frequencia(cls, v):
        if v not in ['diario', 'semanal', 'mensal', 'esporádico']:
            raise ValueError('Frequência deve ser "diario", "semanal", "mensal" ou "esporádico"')
        return v

    @validator('telefones')
    def validar_telefones(cls, v):
        for tel in v:
            if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', tel):
                raise ValueError('Telefone deve estar no formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX')
        return v

    def save(self):
        db = connect_db()
        result = db.doadores.insert_one(self.dict(exclude_unset=True))
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.doadores.find_one({"_id": id})
        if data:
            data['_id'] = str(data['_id'])
            return cls(**data)
        return None

    @classmethod
    def find_all(cls):
        db = connect_db()
        doadores = list(db.doadores.find())
        for d in doadores:
            d['_id'] = str(d['_id'])
        return [cls(**d) for d in doadores]




