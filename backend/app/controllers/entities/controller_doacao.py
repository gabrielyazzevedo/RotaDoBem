from app.models.entities.model_doacao import Doacao
from pydantic import ValidationError
from app.models.entities.model_usuarioUnificado import Motorista
from app.controllers.entities import controller_estoque
from flask_jwt_extended import get_jwt_identity

def create_doacao(data, id_doador):
    try:
        if not data.get('receptor_id'):
            return None, "O campo 'receptor_id' é obrigatório para criar uma doação."
        
        data['doador_id'] = id_doador
        
        nova_doacao = Doacao(**data)
        nova_doacao.save()
        return nova_doacao.dict(), None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)

def get_all_doacoes(claims, status=None):
    """
    Busca todas as doações, filtradas por role e status.
    """
    try:
        query = {} # Começa com uma query vazia
        role = claims.get('role')
        user_id = claims.get('sub') # 'sub' é o 'identity' (o ID do usuário)

        if status:
            query['status'] = status
        
        # Filtra por usuário
        if role == 'admin':
            pass # Admin vê tudo, não adiciona filtro
        elif role == 'doador':
            query['doador_id'] = user_id
        elif role == 'receptor':
            query['receptor_id'] = user_id
        elif role == 'motorista':
            query['motorista_id'] = user_id
        

        doacoes = Doacao.find_all(query) 
        return [doacao.dict() for doacao in doacoes], None
    except Exception as e:
        return None, str(e)

def get_doacao(id):
    id_usuario_logado = get_jwt_identity()
    doacao = Doacao.find_by_id(id)
    
    if not doacao:
        return None, "Doação não encontrada."
    
    if doacao.doador_id != id_usuario_logado:
        return None, "Não autorizado"
        
    return doacao.dict(), None

def update_doacao(id, data):
    id_usuario_logado = get_jwt_identity()
    doacao_atual = Doacao.find_by_id(id)

    if not doacao_atual:
        return None, "Doação não encontrada."

    if doacao_atual.doador_id != id_usuario_logado:
        return None, "Não autorizado"

    success = Doacao.update(id, data)
    if not success:
        return None, "Dados inalterados ou erro ao atualizar a doação."

    novo_status = data.get("status")
    if novo_status == 'recebida' and doacao_atual.status != 'recebida':
        print(f"INFO: Gatilho de estoque ativado para doação {id}.")
        
        dados_para_estoque = {
            "receptor_id": doacao_atual.receptor_id,
            "alimento": doacao_atual.alimento,
            "quantidade": doacao_atual.quantidade,
            "unidade": doacao_atual.unidade,
            "local": "Área de Recebimento" 
        }

        _, erro_estoque = controller_estoque.adicionar_item_ao_estoque(dados_para_estoque)

        if erro_estoque:
            print(f"AVISO: Doação {id} foi atualizada para 'recebida', mas falhou ao dar entrada no estoque: {erro_estoque}")
            return {"mensagem": "Doação atualizada, mas houve um erro ao registrar no estoque."}, None

    return {"mensagem": "Doação atualizada com sucesso."}, None

def delete_doacao(id):
    id_usuario_logado = get_jwt_identity()
    doacao_para_deletar = Doacao.find_by_id(id)

    if not doacao_para_deletar:
        return None, "Doação não encontrada."

    if doacao_para_deletar.doador_id != id_usuario_logado:
        return None, "Não autorizado"

    if Doacao.delete(id):
        return {"mensagem": "Doação deletada com sucesso."}, None
    
    return None, "Erro ao deletar a doação."

def atribuir_motorista(doacao_id, data):
    motorista_id = data.get('motorista_id')
    if not motorista_id:
        return None, "ID do motorista é obrigatório."
    
    if not Doacao.find_by_id(doacao_id):
        return None, "Doação não encontrada."
    if not Motorista.find_by_id(motorista_id):
        return None, "Motorista não encontrado."

    dados_para_atualizar = {
        "motorista_id": motorista_id,
        "status": "a caminho"
    }
    
    if Doacao.update(doacao_id, dados_para_atualizar):
        return {"mensagem": f"Doação {doacao_id} atribuída ao motorista {motorista_id} com sucesso."}, None
    
    return None, "Erro ao atribuir motorista."