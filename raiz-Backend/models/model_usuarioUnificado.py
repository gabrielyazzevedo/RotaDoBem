# models/usuario_unificado.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from enum import Enum
from config.db import connect_db
from bson import ObjectId
import re
from passlib.context import CryptContext

# 1. CONTEXTO DE CRIPTOGRAFIA PARA SENHAS
# Usaremos isso para nunca salvar senhas em texto puro
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 2. MODELOS AUXILIARES (que você já tinha)
# Mantivemos os modelos que são usados dentro de outros
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
            raise ValueError('CEP deve estar no formato 00000-000')
        return v

class ResponsavelLegal(BaseModel):
    nome_completo: str
    cpf: str
    cargo: str

    @validator('cpf')
    def validar_cpf(cls, v):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
            raise ValueError('CPF deve estar no formato 000.000.000-00')
        return v


# 3. ENUM PARA OS PAPÉIS (ROLES)
# Isso garante que só possamos usar os 4 tipos definidos
class RoleEnum(str, Enum):
    ADMIN = "admin"
    DOADOR = "doador"
    RECEPTOR = "receptor"
    MOTORISTA = "motorista"


# 4. O MODELO BASE UNIFICADO
# Contém os campos que TODOS os usuários têm em comum
class Usuario(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    nome: str  # Campo unificado para nome, nome_completo ou razão_social
    email: EmailStr
    senha: str
    telefones: List[str] = []
    role: RoleEnum # O campo que define o tipo de usuário
    ativo: bool = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True # Garante que o valor do Enum seja salvo como string

    # --- MÉTODOS DE SEGURANÇA DE SENHA ---
    def set_password(self, plain_password):
        self.senha = pwd_context.hash(plain_password)

    def check_password(self, plain_password):
        return pwd_context.verify(plain_password, self.senha)

    # --- MÉTODOS DE BANCO DE DADOS ---
    def save(self):
        """Salva o usuário no banco de dados. Se a senha não estiver criptografada, ela será."""
        db = connect_db()
        
        # Criptografa a senha antes de salvar, se necessário
        if not self.senha.startswith("$2b$"):
            self.set_password(self.senha)

        data = self.dict(by_alias=True, exclude_none=True)
        
        # Garante que o email seja único
        if db.usuarios.find_one({"email": self.email}):
            raise ValueError(f"Usuário com email {self.email} já existe.")

        result = db.usuarios.insert_one(data)
        self.id = result.inserted_id
        return self

    @classmethod
    def find_by_email(cls, email: str):
        """Encontra um usuário por email e retorna o modelo Pydantic correto (Admin, Doador, etc.)."""
        db = connect_db()
        data = db.usuarios.find_one({"email": email})
        if not data:
            return None
        
        # "Fábrica" de modelos: decide qual classe usar baseado no 'role'
        role = data.get("role")
        if role == RoleEnum.ADMIN:
            return Admin(**data)
        elif role == RoleEnum.DOADOR:
            return Doador(**data)
        elif role == RoleEnum.RECEPTOR:
            return Receptor(**data)
        elif role == RoleEnum.MOTORISTA:
            return Motorista(**data)
        else:
            return Usuario(**data) # Fallback

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.usuarios.find_one({"_id": ObjectId(id)})
        if not data:
            return None
        # Usa a mesma lógica de "fábrica" do find_by_email
        role = data.get("role")
        model_map = {
            RoleEnum.ADMIN: Admin,
            RoleEnum.DOADOR: Doador,
            RoleEnum.RECEPTOR: Receptor,
            RoleEnum.MOTORISTA: Motorista
        }
        model = model_map.get(role, cls)
        return model(**data)


# 5. MODELOS ESPECÍFICOS QUE HERDAM DE USUÁRIO
# Eles trazem os campos comuns e adicionam os seus próprios

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