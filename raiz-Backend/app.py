# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from bson import ObjectId
import json
from dotenv import load_dotenv

load_dotenv()

# Importa os blueprints de todas as  rotas
from routes.route_admin import admin_routes
from routes.route_doador import doador_routes
from routes.route_receptor import receptor_routes
from routes.route_doacao import doacao_routes
from routes.route_estoque import estoque_routes
from routes.route_motorista import motorista_routes
from routes.route_rota import rota_routes

# Classe auxiliar para que o Flask consiga converter o ObjectId do MongoDB para JSON
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)

app.json_encoder = JSONEncoder

# --- Registro de todos os Blueprints (Rotas) ---
app.register_blueprint(admin_routes, url_prefix='/api')
app.register_blueprint(doador_routes, url_prefix='/api')
app.register_blueprint(receptor_routes, url_prefix='/api')
app.register_blueprint(doacao_routes, url_prefix='/api')
app.register_blueprint(estoque_routes, url_prefix='/api')
app.register_blueprint(motorista_routes, url_prefix='/api')
app.register_blueprint(rota_routes, url_prefix='/api')


# Uma rota principal para verificar se a API está funcionando
@app.route("/api")
def index():
    return jsonify({
        "status": "API Rota do Bem está no ar!",
        "versao": "1.0.0"
    })

# Bloco padrão aplicação desenvolvimento
if __name__ == '__main__':
    # host='0.0.0.0' permite que a API seja acessada de fora do container/máquina
    # debug=True faz o servidor reiniciar automaticamente a cada mudança no código
    app.run(host='0.0.0.0', port=5000, debug=True)