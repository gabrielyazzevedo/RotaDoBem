# -*- coding: utf-8 -*-

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from enum import Enum
from app.config.database import connect_db
from bson import ObjectId
import re
from passlib.context import CryptContext

class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    id: Optional[ObjectId] = Field(None, alias='_id') 

    @validator('cep')
    def validar_cep(cls, v):
        if not re.match(r'^\d{5}-\d{3}$', v):
            raise ValueError('CEP deve estar no formato 00000-000')
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True  # Permite usar alias '_id'

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
    id: Optional[ObjectId] = Field(None, alias='_id')
    nome: str
    email: EmailStr
    senha: str
    telefones: List[str] = []
    role: RoleEnum
    ativo: bool = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        use_enum_values = True

    # --- MÉTODOS DE SEGURANÇA DE SENHA ---
    def set_password(self, plain_password):
        self.senha = pwd_context.hash(plain_password)

    def check_password(self, plain_password):
        return pwd_context.verify(plain_password, self.senha)

    # --- MÉTODOS DE BANCO DE DADOS ---
    def save(self):
        """Salva o usuário no banco de dados. Se a senha não estiver criptografada, ela será."""
        db = connect_db()
        
        if not self.senha.startswith("$2b$"):
            self.set_password(self.senha)

        data = self.dict(by_alias=True, exclude_none=True)
        
        # Garante que o email seja único
        existing = db.usuarios.find_one({"email": self.email})
        if existing and (self.id is None or existing['_id'] != self.id):
            raise ValueError(f"Usuário com email {self.email} já existe.")

        if self.id: # Se tem ID, é um update
            db.usuarios.update_one({"_id": self.id}, {"$set": data})
        else: # Se não tem ID, é um insert
            result = db.usuarios.insert_one(data)
            self.id = result.inserted_id
        return self

    # --- MÉTODOS DE BANCO DE DADOS ---
    
    @classmethod
    def connect_db(cls):
        """Helper para obter a conexão do DB"""
        return connect_db()

    @classmethod
    def _get_model_by_role(cls, role: str):
        """Helper para retornar a classe Pydantic correta."""
        
        model_map = {
            "admin": Admin,
            "doador": Doador,
            "receptor": Receptor,
            "motorista": Motorista
        }
        
        return model_map.get(role, cls)

    @classmethod
    def find_by_email(cls, email: str):
        """Encontra um usuário por email e retorna o modelo Pydantic correto (Admin, Doador, etc.)."""
        db = connect_db()
        data = db.usuarios.find_one({"email": email})
        if not data:
            return None
        
        role = data.get("role")
        model = cls._get_model_by_role(role)
        return model(**data)

    @classmethod
    def find_by_id(cls, id: str):
        try:
            obj_id = ObjectId(id)
        except:
            return None # ID inválido
        
        db = connect_db()
        data = db.usuarios.find_one({"_id": obj_id})
        if not data:
            return None
        
        role = data.get("role")
        model = cls._get_model_by_role(role)
        return model(**data)

            
    @classmethod
    def find_all_by_role(cls, role: RoleEnum):
        """Retorna todos os usuários de uma role específica."""
        db = connect_db()
        users_data = list(db.usuarios.find({"role": role.value}))
        
        model = cls._get_model_by_role(role.value)
        
        # Retorna uma lista de instâncias do modelo Pydantic
        return [model(**data) for data in users_data]

    @classmethod
    def update_user(cls, id: str, data: dict, role_check: RoleEnum = None):
        """Atualiza um usuário no banco de dados."""
        db = connect_db()
        
        # Remove campos que não devem ser atualizados diretamente
        data.pop('role', None)
        data.pop('email', None)
        data.pop('_id', None)
        data.pop('id', None)

        # Se uma nova senha for fornecida, criptografa ela
        if 'senha' in data and data['senha']:
            data['senha'] = pwd_context.hash(data['senha'])
        else:
            data.pop('senha', None) # Remove se for vazia
        
        query = {"_id": ObjectId(id)}
        if role_check:
            query["role"] = role_check.value # Garante que estamos atualizando o usuario certo
        
        result = db.usuarios.update_one(query, {"$set": data})
        return result.modified_count > 0

    @classmethod
    def delete_user(cls, id: str, role_check: RoleEnum = None):
        """Deleta um usuário do banco de dados."""
        db = connect_db()
        query = {"_id": ObjectId(id)}
        if role_check:
            query["role"] = role_check.value
            
        result = db.usuarios.delete_one(query)
        return result.deleted_count > 0

# HERDAM DE USUÁRIO

class Admin(Usuario):
    role: RoleEnum = Field(RoleEnum.ADMIN, const=True) # Valor fixo
    nivel_acesso: str = 'superadmin'

class Motorista(Usuario):
    role: RoleEnum = Field(RoleEnum.MOTORISTA, const=True)
    cpf: str
    cnh: str
    placa_veiculo: str
    status: str = 'disponivel'

    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF deve estar no formato 000.000.000-00')
        return v

class Doador(Usuario):
    role: RoleEnum = Field(RoleEnum.DOADOR, const=True)
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
            raise ValueError('CNPJ deve estar no formato 00.000.000/0000-00')
        return v

class Receptor(Usuario):
    role: RoleEnum = Field(RoleEnum.RECEPTOR, const=True)
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
            raise ValueError('CNPJ deve estar no formato 00.000.000/0000-00')
        return v