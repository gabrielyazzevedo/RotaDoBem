# controllers/controller_rota.py
import os
import requests
from app.models.entities.model_doacao import Doacao
from app.models.entities.model_doador import Doador
from app.models.entities.model_receptor import Receptor

def obter_enderecos_por_doacao(doacao_id):
    """
    Busca os endereços de origem (Doador) e destino (Receptor) de uma doação.
    """
    doacao = Doacao.find_by_id(doacao_id)
    if not doacao:
        return None, "Doação não encontrada."

    doador = Doador.find_by_id(doacao.doador_id)
    receptor = Receptor.find_by_id(doacao.receptor_id)

    if not doador or not receptor:
        return None, "Doador ou Receptor associado à doação não foi encontrado."

    dados_rota = {
        "doacao_id": doacao_id,
        "origem": {
            "id": doador.id,
            "razao_social": doador.razao_social,
            "endereco": doador.endereco.dict()
        },
        "destino": {
            "id": receptor.id,
            "razao_social": receptor.razao_social,
            "endereco": receptor.endereco.dict()
        }
    }
    return dados_rota, None


def calcular_melhor_rota(doacao_id):
    """
    Orquestra a busca dos endereços e a chamada à API do Google Maps.
    """
    dados_locais, error = obter_enderecos_por_doacao(doacao_id)
    if error:
        return None, error

    # Formata os endereços em uma string única para a API
    end_origem_obj = dados_locais['origem']['endereco']
    end_destino_obj = dados_locais['destino']['endereco']
    
    str_origem = f"{end_origem_obj['logradouro']}, {end_origem_obj['numero']}, {end_origem_obj['cidade']}, {end_origem_obj['estado']}"
    str_destino = f"{end_destino_obj['logradouro']}, {end_destino_obj['numero']}, {end_destino_obj['cidade']}, {end_destino_obj['estado']}"

    # Pega a chave da API do arquivo .env
    API_KEY = os.getenv('API_KEY')
    if not API_KEY:
        return None, "Chave da API do Google Maps não configurada no .env"

    # Monta a URL da Directions API
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={str_origem}&destination={str_destino}&key={API_KEY}&language=pt-BR"

    try:
        response = requests.get(url)
        response.raise_for_status() 
        dados_google = response.json()

        if dados_google['status'] != 'OK':
            return None, f"Erro da API do Google: {dados_google.get('error_message', dados_google['status'])}"
        
        # Anexa o resultado do Google aos dados locais
        dados_locais['calculo_rota'] = {
            'distancia': dados_google['routes'][0]['legs'][0]['distance']['text'],
            'duracao': dados_google['routes'][0]['legs'][0]['duration']['text'],
            'resumo_rota': dados_google['routes'][0]['summary'],
            'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={str_origem}&destination={str_destino}"
        }

        return dados_locais, None

    except requests.exceptions.RequestException as e:
        return None, f"Erro de comunicação com a API do Google: {e}"