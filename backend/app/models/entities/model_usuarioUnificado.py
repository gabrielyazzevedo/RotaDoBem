# -*- coding: utf-8 -*-

from pydantic import BaseModel, EmailStr, Field, validator, BeforeValidator
from typing import Optional, List, Union, Literal, Annotated, Any
from enum import Enum
from app.config.database import connect_db
from bson import ObjectId
import re
from werkzeug.security import generate_password_hash, check_password_hash

# --- TIPO CUSTOMIZADO PARA O ID (PYDANTIC V2) ---
PyObjectId = Annotated[str, BeforeValidator(str)]

class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    id: Optional[PyObjectId] = Field(None, alias='_id') 

    @validator('cep')
    def validar_cep(cls, v):
        if not re.match(r'^\d{5}-\d{3}$', v):
            raise ValueError('CEP deve estar no formato 00000-000')
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True 

class ResponsavelLegal(BaseModel):
    nome_completo: str
    cpf: str
    cargo: str

    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF deve estar no formato 000.000.000-00')
        return v

class RoleEnum(str, Enum):
    ADMIN = "admin"
    DOADOR = "doador"
    RECEPTOR = "receptor"
    MOTORISTA = "motorista"

class Usuario(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias='_id')
    nome: str
    email: EmailStr
    senha: str
    telefones: List[str] = []
    role: RoleEnum
    ativo: bool = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True
        use_enum_values = True

    # --- SEGURANÇA ---
    def set_password(self, plain_password):
        self.senha = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.senha, plain_password)

    # --- DB ---
    def save(self):
        db = connect_db()
        if ':' not in self.senha:
            self.set_password(self.senha)

        data = self.dict(by_alias=True, exclude_none=True)
        if data.get('_id') is None: data.pop('_id', None)

        existing = db.usuarios.find_one({"email": self.email})
        if existing and (self.id is None or str(existing['_id']) != str(self.id)):
            raise ValueError(f"Usuário com email {self.email} já existe.")

        if self.id: 
            db.usuarios.update_one({"_id": ObjectId(self.id)}, {"$set": data})
        else: 
            result = db.usuarios.insert_one(data)
            self.id = str(result.inserted_id)
        return self

    @classmethod
    def connect_db(cls):
        return connect_db()

    @classmethod
    def _get_model_by_role(cls, role: str):
        model_map = {
            "admin": Admin,
            "doador": Doador,
            "receptor": Receptor,
            "motorista": Motorista
        }
        return model_map.get(role, cls)

    @classmethod
    def find_by_email(cls, email: str):
        db = connect_db()
        data = db.usuarios.find_one({"email": email})
        if not data: return None
        return cls._get_model_by_role(data.get("role"))(**data)

    @classmethod
    def find_by_id(cls, id: str):
        try: obj_id = ObjectId(id)
        except: return None
        db = connect_db()
        data = db.usuarios.find_one({"_id": obj_id})
        if not data: return None
        return cls._get_model_by_role(data.get("role"))(**data)
            
    @classmethod
    def find_all_by_role(cls, role: RoleEnum):
        db = connect_db()
        users_data = list(db.usuarios.find({"role": role.value}))
        model = cls._get_model_by_role(role.value)
        return [model(**data) for data in users_data]

    @classmethod
    def update_user(cls, id: str, data: dict, role_check: RoleEnum = None):
        db = connect_db()
        for f in ['role', 'email', '_id', 'id']: data.pop(f, None)
        if 'senha' in data and data['senha']:
            data['senha'] = generate_password_hash(data['senha'])
        else: data.pop('senha', None)
        
        query = {"_id": ObjectId(id)}
        if role_check: query["role"] = role_check.value
        return db.usuarios.update_one(query, {"$set": data}).modified_count > 0

    @classmethod
    def delete_user(cls, id: str, role_check: RoleEnum = None):
        db = connect_db()
        query = {"_id": ObjectId(id)}
        if role_check: query["role"] = role_check.value
        return db.usuarios.delete_one(query).deleted_count > 0

# --- SUBCLASSES SIMPLIFICADAS ---
# Removemos o 'Literal' para evitar conflitos de validação com strings do Mongo

class Admin(Usuario):
    nivel_acesso: str = 'superadmin'

class Motorista(Usuario):
    cpf: str
    cnh: str
    placa_veiculo: str
    status: str = 'disponivel'

    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF inválido')
        return v

class Doador(Usuario):
    cnpj: str
    endereco: Endereco
    responsavel_legal: ResponsavelLegal
    horario_disponibilidade: str
    declaracao_anvisa: bool
    tipos_alimentos: List[str] = []
    frequencia_doacao: str

    @validator('cnpj')
    def validar_cnpj(cls, v):
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', v):
            raise ValueError('CNPJ inválido')
        return v

class Receptor(Usuario):
    cnpj: str
    endereco: Endereco
    responsavel_legal: ResponsavelLegal
    horario_disponibilidade: str
    declaracao_anvisa: bool
    alvara_sanitario: bool
    numero_beneficiarios: int
    capacidade_armazenamento: str
    tipo_armazenamento: List[str] = []

    @validator('cnpj')
    def validar_cnpj(cls, v):
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', v):
            raise ValueError('CNPJ inválido')
        return v