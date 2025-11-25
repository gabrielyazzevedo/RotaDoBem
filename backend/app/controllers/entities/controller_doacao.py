# -*- coding: utf-8 -*-
from app.models.entities.model_doacao import Doacao
from pydantic import ValidationError
from flask_jwt_extended import get_jwt_identity
import traceback
from datetime import datetime

def create_doacao(data, id_doador):
    try:
        data['doador_id'] = id_doador
        data['status'] = 'pendente'
        data['receptor_id'] = None
        
        if 'validade' in data and isinstance(data['validade'], str):
            data['validade'] = datetime.strptime(data['validade'], '%Y-%m-%d')

        nova_doacao = Doacao(**data)
        nova_doacao.save()
        # Correção V2: mode='json' converte datas e IDs para string automaticamente
        return nova_doacao.model_dump(mode='json'), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)

def get_all_doacoes(claims, status=None):
    try:
        query = {}
        role = claims.get('role')
        user_id = claims.get('sub') 

        if role == 'doador':
            if status == 'finalizadas':
                # Histórico: O que já foi entregue
                query = {
                    'doador_id': user_id,
                    'status': {'$in': ['recebida', 'concluida']} # Status finais
                }
            else:
                # Padrão: O que está ativo (pendente, aceita, a caminho)
                query = {
                    'doador_id': user_id,
                    'status': {'$nin': ['recebida', 'concluida']} # Exclui finalizadas da lista principal
                }

        elif role == 'receptor':
            if status == 'finalizadas':
                # Histórico: O que já recebeu
                query = {
                    'receptor_id': user_id,
                    'status': {'$in': ['recebida', 'concluida']}
                }
            else:
                # Padrão: Pendentes (geral) ou Aceitas por ele (mas não entregues)
                query['$or'] = [
                    {'status': 'pendente'},
                    {'receptor_id': user_id, 'status': {'$nin': ['recebida', 'concluida']}}
                ]

        elif role == 'motorista':
            query['$or'] = [
                {'status': 'aceita'}, 
                {'motorista_id': user_id}
            ]
        
        # Se vier status específico na URL (exceto o 'finalizadas' que tratamos acima)
        if status and status != 'finalizadas':
            query['status'] = status

        doacoes = Doacao.find_all(query)
        return [d.model_dump(mode='json') for d in doacoes], None
    except Exception as e:
        print(f"Erro busca: {e}")
        traceback.print_exc()
        return None, str(e)

def aceitar_doacao(id_doacao, id_receptor):
    try:
        doacao = Doacao.find_by_id(id_doacao)
        if not doacao: return None, "Doação não encontrada."
        if doacao.status != 'pendente': return None, "Não está mais disponível."
            
        dados = {"status": "aceita", "receptor_id": id_receptor}
        
        if Doacao.update(id_doacao, dados):
            return {"mensagem": "Doação aceita! Aguardando motorista."}, None
        return None, "Erro ao atualizar."
    except Exception as e:
        return None, str(e)

def get_doacao(id):
    try:
        doacao = Doacao.find_by_id(id)
        if not doacao: return None, "Não encontrada."
        # Correção V2
        return doacao.model_dump(mode='json'), None
    except Exception as e:
        return None, str(e)

def update_doacao(id, data):
    if Doacao.update(id, data): return {"mensagem": "Atualizado"}, None
    return None, "Erro"

def delete_doacao(id):
    if Doacao.delete(id): return {"mensagem": "Deletado"}, None
    return None, "Erro"

def atribuir_motorista(id, data):
    return None, "Não implementado ainda"