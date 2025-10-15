from models.model_estoque import Estoque
from pydantic import ValidationError

def adicionar_item_ao_estoque(data):
    """
    Função inteligente: Se o item já existe para o receptor, incrementa a quantidade.
    Senão, cria um novo item no estoque.
    Esta função será chamada pela controller de doação.
    """
    try:
        item_existente = Estoque.find_one_by_details(
            receptor_id=data['receptor_id'],
            alimento=data['alimento'],
            unidade=data['unidade']
        )

        if item_existente:
            Estoque.increment_quantity(item_existente.id, data['quantidade'])
            return {"mensagem": f"Estoque do item '{data['alimento']}' atualizado."}, None
        else:
            novo_item = Estoque(**data)
            novo_item.save()
            return novo_item.dict(), None

    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)


def listar_estoque_por_receptor(receptor_id):
    """Retorna todos os itens de estoque de um receptor específico."""
    try:
        itens = Estoque.find_by_receptor_id(receptor_id)
        return [item.dict() for item in itens], None
    except Exception as e:
        return None, str(e)


def ajustar_quantidade_item(item_id, data):
    """Permite um ajuste manual da quantidade de um item no estoque."""
    try:
        quantidade = float(data['quantidade'])
        if quantidade < 0:
            return None, "Quantidade não pode ser negativa."
        
        if Estoque.update(item_id, {"quantidade": quantidade}):
            return {"mensagem": "Quantidade ajustada com sucesso."}, None
        else:
            return None, "Item de estoque não encontrado ou quantidade inalterada."
    except (ValueError, KeyError):
        return None, "Dados inválidos. Forneça uma 'quantidade' numérica."
    except Exception as e:
        return None, str(e)

def get_item_por_id(item_id):
    """Busca um único item de estoque pelo seu ID."""
    item = Estoque.find_by_id(item_id)
    if item:
        return item.dict(), None
    return None, "Item de estoque não encontrado."