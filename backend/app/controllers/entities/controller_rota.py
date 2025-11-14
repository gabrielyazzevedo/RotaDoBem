# -*- coding: utf-8 -*-

import os
import requests
from app.models.entities.model_doacao import Doacao
from app.models.entities.model_usuarioUnificado import Doador, Receptor, RoleEnum, Motorista
from app.models.entities.model_rota import Rota, StatusRotaEnum

def obter_enderecos_por_doacao(doacao_id):

    doacao = Doacao.find_by_id(doacao_id)
    if not doacao:
        return None, "Doação não encontrada."

    doador = Doador.find_by_id(doacao.doador_id)
    receptor = Receptor.find_by_id(doacao.receptor_id)

    if not doador or not receptor:
        return None, "Doador ou Receptor associado à doação não foi encontrado."
    
    if doador.role != RoleEnum.DOADOR or receptor.role != RoleEnum.RECEPTOR:
        return None, "IDs de usuário não correspondem aos papéis de Doador e Receptor."

    dados_rota = {
        "doacao_id": doacao_id,
        "origem": {
            "id": doador.id,
            "nome": doador.nome, 
            "endereco": doador.endereco.dict()
        },
        "destino": {
            "id": receptor.id,
            "nome": receptor.nome,
            "endereco": receptor.endereco.dict()
        }
    }
    return dados_rota, None


def calcular_e_salvar_rota(doacao_id): # Função principal
    """
    Orquestra a busca dos endereços, a chamada à API do Google Maps
    E SALVA a rota calculada no banco de dados.
    """
    
    # Checa se a rota já foi calculada e salva
    rota_existente = Rota.find_by_doacao_id(doacao_id)
    if rota_existente:
        print(f"INFO: Rota para doação {doacao_id} já existia. Retornando dados do DB.")
        return rota_existente.dict(), None

    # Se não existe, busca os endereços
    dados_locais, error = obter_enderecos_por_doacao(doacao_id)
    if error:
        return None, error

    # Formata os endereços para a API
    end_origem_obj = dados_locais['origem']['endereco']
    end_destino_obj = dados_locais['destino']['endereco']
    
    str_origem = f"{end_origem_obj['logradouro']}, {end_origem_obj['numero']}, {end_origem_obj['cidade']}, {end_origem_obj['estado']}"
    str_destino = f"{end_destino_obj['logradouro']}, {end_destino_obj['numero']}, {end_destino_obj['cidade']}, {end_destino_obj['estado']}"

    # Chama a API do Google
    API_KEY = os.getenv('API_KEY')
    if not API_KEY:
        return None, "Chave da API do Google Maps não configurada no .env"

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={str_origem}&destination={str_destino}&key={API_KEY}&language=pt-BR"

    try:
        response = requests.get(url)
        response.raise_for_status() 
        dados_google = response.json()

        if dados_google['status'] != 'OK':
            return None, f"Erro da API do Google: {dados_google.get('error_message', dados_google['status'])}"
        
        dados_para_salvar = {
            "doacao_id": doacao_id,
            "endereco_origem": end_origem_obj,
            "endereco_destino": end_destino_obj,
            "distancia_texto": dados_google['routes'][0]['legs'][0]['distance']['text'],
            "duracao_texto": dados_google['routes'][0]['legs'][0]['duration']['text'],
            "resumo_rota": dados_google['routes'][0]['summary'],
            "google_maps_link": f"https://www.google.com/maps/dir/?api=1&origin={str_origem}&destination={str_destino}"
        }
        
        nova_rota = Rota(**dados_para_salvar)
        nova_rota.save()

        print(f"INFO: Nova rota para doação {doacao_id} calculada e salva.")
        return nova_rota.dict(), None

    except requests.exceptions.RequestException as e:
        return None, f"Erro de comunicação com a API do Google: {e}"


def get_rota_por_id(rota_id: str):
    rota = Rota.find_by_id(rota_id)
    if not rota:
        return None, "Rota não encontrada"
    return rota.dict(), None

def get_todas_rotas(status: str = None):
    query = {}
    if status:
        try:
            query['status'] = StatusRotaEnum(status).value
        except ValueError:
            return None, f"Status '{status}' inválido."
            
    rotas = Rota.find_all(query)
    return [r.dict() for r in rotas], None

def atribuir_motorista_rota(rota_id: str, motorista_id: str):
    """Atribui um motorista a uma rota e muda o status."""
    
    rota = Rota.find_by_id(rota_id)
    if not rota:
        return None, "Rota não encontrada"
    
    motorista = Motorista.find_by_id(motorista_id)
    if not motorista or motorista.role != RoleEnum.MOTORISTA:
        return None, "Motorista não encontrado ou ID de usuário inválido"
    
    if rota.status != StatusRotaEnum.PENDENTE:
        return None, f"Esta rota não está pendente (Status atual: {rota.status})"

    # Atualiza o ID do motorista e o status da rota
    dados_update = {
        "motorista_id": motorista_id,
        "status": StatusRotaEnum.EM_ANDAMENTO.value
    }
    
    # Atualiza o status da doação
    Doacao.update(rota.doacao_id, {"status": "a caminho"})
    
    # Atualiza o status do motorista
    Motorista.update_user(motorista_id, {"status": "em_rota"})

    if Rota.update(rota_id, dados_update):
        return {"mensagem": "Rota atribuída ao motorista com sucesso."}, None
    
    return None, "Falha ao atualizar a rota."

def marcar_rota_status(rota_id: str, status: str):
    """Muda o status de uma rota (ex: 'concluida', 'cancelada')."""
    
    try:
        # Valida se o status é um membro válido do Enum
        status_enum = StatusRotaEnum(status)
    except ValueError:
        return None, f"Status '{status}' é inválido."

    rota = Rota.find_by_id(rota_id)
    if not rota:
        return None, "Rota não encontrada"

    dados_update = {"status": status_enum.value}
    
    if Rota.update(rota_id, dados_update):
        # Se concluiu a rota, liberar o motorista e atualizar doação
        if status_enum == StatusRotaEnum.CONCLUIDA and rota.motorista_id:
            Motorista.update_user(rota.motorista_id, {"status": "disponivel"})
            # Atualiza a doação para 'recebida', o que dispara a entrada no estoque
            Doacao.update(rota.doacao_id, {"status": "recebida"}) 

        # Se cancelou a rota, liberar o motorista
        elif status_enum == StatusRotaEnum.CANCELADA and rota.motorista_id:
             Motorista.update_user(rota.motorista_id, {"status": "disponivel"})
             Doacao.update(rota.doacao_id, {"status": "pendente"}) # Volta doação p/ pendente

        return {"mensagem": f"Status da rota atualizado para '{status}'."}, None
    
    return None, "Falha ao atualizar o status da rota."