from pydantic import BaseModel, EmailStr
from typing import Optional
from app.config.database import connect_db
from pydantic import Field
from bson import ObjectId

class Admin(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    nome: str
    email: EmailStr
    senha: str
    nivel_acesso: str = 'superadmin'

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def save(self):
        db = connect_db()
        data = self.dict(by_alias=True, exclude_none=True)
        result = db.admins.insert_one(data)
        self.id = str(result.inserted_id)
        return self

    @classmethod
    def find_by_id(cls, id: str):
        db = connect_db()
        data = db.admins.find_one({"_id": ObjectId(id)})
        if data:
            return cls(**data)
        return None

    @classmethod
    def find_all(cls):
        db = connect_db()
        admins = list(db.admins.find())
        for a in admins:
            a['_id'] = str(a['_id'])
        return [cls(**a) for a in admins]
    
    @classmethod
    def update(cls, id: str, data: dict):
        db = connect_db()
        result = db.admins.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, id: str):
        db = connect_db()
        result = db.admins.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0




