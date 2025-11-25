# -*- coding: utf-8 -*-
from app.models.entities.model_usuarioUnificado import Doador, Receptor, Motorista
from pydantic import ValidationError
import traceback

def register_user(data):
    """
    Cria um novo usuário (Doador, Receptor ou Motorista) 
    com base no 'role' e nos dados complexos fornecidos.
    """
    
    # 1. Validação básica de senha
    if data.get('senha') != data.get('confirmar_senha'):
        return None, "Senhas não coincidem.", 400

    role = data.get('role')
    
    model_map = {
        "doador": Doador,
        "receptor": Receptor,
        "motorista": Motorista
    }
    
    UserClass = model_map.get(role)
    
    if not UserClass:
        return None, f"Tipo de usuário '{role}' é inválido.", 400
        
    try:
        # 2. Criação do Objeto (Pydantic valida os tipos aqui)
        # Se houver campos extras no JSON que não existem no modelo, o Pydantic ignora ou alerta
        new_user = UserClass(**data)
        
        # 3. Salvar no Banco (Criptografia de senha acontece aqui dentro)
        new_user.save()
        
        # 4. Retorno Seguro (A CORREÇÃO PRINCIPAL)
        # Usamos model_dump(mode='json') para garantir que IDs e Datas virem strings
        # Removemos a senha do retorno por segurança
        user_dict = new_user.model_dump(mode='json', exclude={'senha'})
        
        return user_dict, None, 201 

    except ValidationError as e:
        # Erros de validação do Pydantic (ex: CPF inválido, campo faltando)
        # Convertemos para string para o frontend conseguir ler
        return None, str(e), 422 
        
    except ValueError as e:
        # Erros de regra de negócio (ex: Email duplicado)
        return None, str(e), 400 
        
    except Exception as e:
        # Erros genéricos (Crash do servidor)
        print(f"❌ Erro no Registro: {e}")
        traceback.print_exc() # Imprime o erro real no terminal para debug
        return None, "Erro interno ao criar usuário. Tente novamente.", 500