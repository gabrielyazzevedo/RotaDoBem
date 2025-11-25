# -*- coding: utf-8 -*-
import os
import requests
import traceback
from app.models.entities.model_doacao import Doacao
from app.models.entities.model_usuarioUnificado import Doador, Receptor, RoleEnum, Motorista
from app.models.entities.model_rota import Rota, StatusRotaEnum
from datetime import datetime

def obter_enderecos_por_doacao(doacao_id):
    try:
        doacao = Doacao.find_by_id(doacao_id)
        if not doacao: return None, "Doação não encontrada."

        doador = Doador.find_by_id(doacao.doador_id)
        receptor = Receptor.find_by_id(doacao.receptor_id)

        if not doador or not receptor: return None, "Doador ou Receptor não encontrados."

        return {
            "origem": doador.endereco.model_dump(),
            "destino": receptor.endereco.model_dump()
        }, None
    except Exception as e:
        return None, str(e)

def calcular_e_salvar_rota(doacao_id):
    try:
        rota_existente = Rota.find_by_doacao_id(doacao_id)
        if rota_existente: return rota_existente.model_dump(mode='json'), None

        enderecos, erro = obter_enderecos_por_doacao(doacao_id)
        if erro: return None, erro

        # MOCK (Simulação) por padrão
        dados_rota = {
            "doacao_id": doacao_id,
            "endereco_origem": enderecos['origem'],
            "endereco_destino": enderecos['destino'],
            "distancia_texto": "5.2 km (Simulado)",
            "duracao_texto": "15 mins (Simulado)",
            "resumo_rota": "Via Principal",
            "google_maps_link": f"https://www.google.com/maps/dir/?api=1&origin={enderecos['origem']['cep']}&destination={enderecos['destino']['cep']}"
        }

        # ... (código anterior da função) ...

        # Tenta API Real se tiver chave
        API_KEY = os.getenv('API_KEY')
        if API_KEY:
            print(f"🔄 Tentando conectar Google Maps com chave: {API_KEY[:5]}...") # Mostra inicio da chave
            try:
                origem = f"{enderecos['origem']['cep']}"
                destino = f"{enderecos['destino']['cep']}"
                url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origem}&destination={destino}&key={API_KEY}&language=pt-BR"
                
                resp = requests.get(url, timeout=5)
                print(f"📡 Status HTTP Google: {resp.status_code}") # 200 = Conectou
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"📦 Resposta Google: {data['status']}") # OK, REQUEST_DENIED, etc.
                    
                    if data['status'] == 'OK':
                        leg = data['routes'][0]['legs'][0]
                        dados_rota['distancia_texto'] = leg['distance']['text']
                        dados_rota['duracao_texto'] = leg['duration']['text']
                        dados_rota['resumo_rota'] = data['routes'][0]['summary']
                        dados_rota['google_maps_link'] = f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}"
                        print("✅ Rota calculada com sucesso pela API!")
                    else:
                        # AQUI VAI APARECER O MOTIVO DO ERRO
                        print(f"❌ Erro na API do Google: {data.get('error_message', 'Sem mensagem')}")
                else:
                    print(f"❌ Erro de Conexão: {resp.text}")

            except Exception as api_err:
                print(f"❌ Exceção ao conectar Google: {api_err}")

        nova_rota = Rota(**dados_rota)
        nova_rota.save()
        return nova_rota.model_dump(mode='json'), None
    except Exception as e:
        traceback.print_exc()
        return None, f"Erro interno ao calcular rota: {str(e)}"

def atribuir_motorista_rota(rota_id, motorista_id):
    try:
        if not motorista_id:
            return None, "ID do motorista não identificado."

        rota = Rota.find_by_id(rota_id)
        if not rota: return None, "Rota não encontrada"
        
        # Atualiza Rota
        Rota.update(rota_id, {"motorista_id": motorista_id, "status": StatusRotaEnum.EM_ANDAMENTO.value})
        # Atualiza Doação
        Doacao.update(rota.doacao_id, {"status": "a caminho", "motorista_id": motorista_id})
        
        return {"mensagem": "Corrida aceita com sucesso! Boa entrega."}, None
    except Exception as e:
        traceback.print_exc()
        return None, f"Erro ao aceitar corrida: {str(e)}"

def marcar_rota_status(rota_id, novo_status):
    try:
        rota = Rota.find_by_id(rota_id)
        if not rota: return None, "Rota não encontrada"

        Rota.update(rota_id, {"status": novo_status})
        
        if novo_status == StatusRotaEnum.CONCLUIDA.value:
            Doacao.update(rota.doacao_id, {"status": "recebida"}) 
        elif novo_status == StatusRotaEnum.CANCELADA.value:
            Doacao.update(rota.doacao_id, {"status": "aceita", "motorista_id": None}) 

        return {"mensagem": f"Status atualizado para {novo_status}."}, None
    except Exception as e:
        traceback.print_exc()
        return None, f"Erro ao atualizar status: {str(e)}"

def get_todas_rotas(status=None):
    try:
        query = {}
        if status: query['status'] = status
        rotas = Rota.find_all(query)
        return [r.model_dump(mode='json') for r in rotas], None
    except Exception as e:
        return None, str(e)

def get_rota_por_id(id):
    try:
        r = Rota.find_by_id(id)
        if r: return r.model_dump(mode='json'), None
        return None, "Não encontrada"
    except Exception as e:
        return None, str(e)