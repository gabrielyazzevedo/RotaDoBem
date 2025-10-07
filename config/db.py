# -*- coding: utf-8 -*-
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Variaveis de ambiente do arquivo .env
load_dotenv()

# String de conexao do banco
DB_URI = os.getenv('DB_URI')

def connect_db():
    try:
        
        client = MongoClient(DB_URI, serverSelectionTimeoutMS=5000) 
        # Testa a conexao pingando no servidor
        client.admin.command('ping')
        db = client['doacoesDB']
        print("Conexao com o MongoDB estabelecida com sucesso!")
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {str(e)}")
        raise
