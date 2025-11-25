import sys
import os
from datetime import date, timedelta, datetime, time

# --- 1. CORREÇÃO DE IMPORTAÇÃO (Obrigatório para funcionar na raiz) ---
# Adiciona a pasta 'backend' ao caminho do Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config.database import connect_db
# Importa os modelos já atualizados com a criptografia correta e Pydantic V2
from app.models.entities.model_usuarioUnificado import Doador, Endereco, ResponsavelLegal, RoleEnum, Receptor
from app.models.entities.model_doacao import Doacao

def popular_completo():
    print("\n🔌 Conectando ao MongoDB...")
    try:
        db = connect_db()
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return

    # --- 2. LIMPEZA (O segredo para não ter erros de dados antigos) ---
    print("\n🧹 Limpando dados antigos e incompatíveis...")
    colecoes = ['usuarios', 'doacoes', 'rotas', 'estoque', 'admins', 'motoristas', 'doadores', 'receptores']
    for col in colecoes:
        db[col].drop()
    print("✨ Banco limpo com sucesso!")

    # --- 3. CRIAÇÃO DE DADOS NOVOS (Já criptografados corretamente) ---
    print("\n🏗️  Criando usuários...")

    # Criar DOADOR
    doador = Doador(
        nome="Restaurante Sabor Caseiro",
        email="restaurante@teste.com",
        senha="123", # O model novo vai criptografar isso automaticamente ao salvar
        role=RoleEnum.DOADOR,
        telefones=["(11) 99999-9999"],
        cnpj="12.345.678/0001-00",
        horario_disponibilidade="08h as 18h",
        declaracao_anvisa=True,
        frequencia_doacao="diaria",
        endereco=Endereco(logradouro="Rua Augusta", numero="100", bairro="Centro", cidade="São Paulo", estado="SP", cep="01001-000"),
        responsavel_legal=ResponsavelLegal(nome_completo="Jose Silva", cpf="111.111.111-11", cargo="Dono")
    )
    doador.save()
    print(f"   ✅ Doador criado: {doador.email} (Senha: 123)")

    # Criar RECEPTOR
    receptor = Receptor(
        nome="Orfanato Raio de Luz",
        email="orfanato@teste.com",
        senha="123",
        role=RoleEnum.RECEPTOR,
        telefones=["(11) 98888-8888"],
        cnpj="98.765.432/0001-99",
        horario_disponibilidade="24h",
        declaracao_anvisa=True,
        alvara_sanitario=True,
        numero_beneficiarios=50,
        capacidade_armazenamento="Grande",
        endereco=Endereco(logradouro="Rua da Paz", numero="50", bairro="Liberdade", cidade="São Paulo", estado="SP", cep="01002-000"),
        responsavel_legal=ResponsavelLegal(nome_completo="Maria Souza", cpf="222.222.222-22", cargo="Diretora")
    )
    receptor.save()
    print(f"   ✅ Receptor criado: {receptor.email} (Senha: 123)")

    # --- 4. CRIAÇÃO DE DOAÇÕES ---
    print("\n📦 Criando doações...")
    
    # Data de validade futura (Corrigida para datetime)
    validade_futura = datetime.combine(date.today() + timedelta(days=30), time.min)
    
    itens = [
        {"alimento": "Marmitas Congeladas", "unidade": "unidades", "qtd": 10.0},
        {"alimento": "Saco de Arroz 5kg", "unidade": "pacotes", "qtd": 5.0},
        {"alimento": "Feijão Carioca", "unidade": "kg", "qtd": 20.0},
    ]

    for item in itens:
        doacao = Doacao(
            doador_id=str(doador.id),
            alimento=item['alimento'],
            quantidade=item['qtd'],
            unidade=item['unidade'],
            validade=validade_futura,
            status="pendente"
        )
        doacao.save()
        print(f"   + {item['alimento']} adicionado.")

    print("\n🚀 TUDO PRONTO! O banco foi resetado e populado.")

if __name__ == "__main__":
    popular_completo()