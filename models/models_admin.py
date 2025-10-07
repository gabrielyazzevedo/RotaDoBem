from pydantic import BaseModel, EmailStr
from typing import Optional
from config.db import connect_db

class Admin(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    nivel_acesso: str = 'superadmin'

    def save(self):
        db = connect_db()
        result = db.admins.insert_one(self.dict(exclude_unset=True))
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.admins.find_one({"_id": id})
        if data:
            data['_id'] = str(data['_id'])
            return cls(**data)
        return None

    @classmethod
    def find_all(cls):
        db = connect_db()
        admins = list(db.admins.find())
        for a in admins:
            a['_id'] = str(a['_id'])
        return [cls(**a) for a in admins]




