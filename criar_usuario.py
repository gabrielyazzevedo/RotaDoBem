# criar_usuario.py

from app import app, db 
from models.user import User  # <-- AJUSTE AQUI: importe seu modelo de usuário
from flask_bcrypt import Bcrypt # Ou a biblioteca de hash que você usa

# Inicializa o Bcrypt com o app
bcrypt = Bcrypt(app)

# Use o app_context para interagir com a aplicação
with app.app_context():
    # --- Dados do novo usuário ---
    email_novo = "teste@email.com"
    senha_nova_texto_puro = "senha123"
    # Adicione outros campos se forem obrigatórios no seu modelo
    # nome_novo = "Usuario de Teste"
    # papel_novo = "doador" # ou "admin", dependendo do seu sistema

    # Verifica se o usuário já existe
    usuario_existente = User.query.filter_by(email=email_novo).first()

    if usuario_existente:
        print(f"O usuário com o email '{email_novo}' já existe.")
    else:
        # Criptografa a senha
        senha_hash = bcrypt.generate_password_hash(senha_nova_texto_puro).decode('utf-8')

        # Cria a nova instância do usuário
        novo_usuario = User(
            email=email_novo, 
            senha=senha_hash
            # Certifique-se de incluir outros campos obrigatórios
            # nome=nome_novo,
            # role=papel_novo
        )

        # Adiciona e salva no banco de dados
        db.session.add(novo_usuario)
        db.session.commit()

        print(f"Usuário '{email_novo}' criado com sucesso!")