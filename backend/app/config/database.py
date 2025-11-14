# -*- coding: utf-8 -*-
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

DB_URI = os.getenv('DB_URI')

def connect_db():
    try:
        client = MongoClient(DB_URI, serverSelectionTimeoutMS=5000) 
        
        client.admin.command('ping') 
        
        db = client['doacoesDB']
        
        print(f"Conexao com o MongoDB estabelecida com sucesso!")
        return db
    except Exception as e:
        print(f"Erro de autenticação/conexão ao conectar ao MongoDB: {str(e)}")
        raise


if __name__ == "__main__":
    db_doacoes = connect_db() 
    
    try:
        # A coleção 'doacoesDB' dentro da database 'doacoesDB'
        test_collection = db_doacoes['teste_db'] 
        
        test_collection.insert_one({"status": "DB 'doacoesDB' ativada. Teste de escrita bem-sucedido."})
        print("Documento de teste inserido com sucesso. O banco de dados está ativo.")
        

        test_collection.delete_one({"status": "DB 'teste' criado e ativado."}) 
    except Exception as e:
        print(f"Erro ao inserir documento de teste (Verifique a permissão de escrita): {e}")