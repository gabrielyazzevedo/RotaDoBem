# -*- coding: utf-8 -*-
"""
Rota do Bem - Executar Aplicação
"""
import os
import sys
import subprocess

def main():
    """Executa a aplicação backend"""
    print("=" * 50)
    print("    Rota do Bem - Iniciando Aplicação")
    print("=" * 50)
    
    # Ativar ambiente virtual e executar backend
    venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
    backend_script = os.path.join('backend', 'run.py')
    
    if not os.path.exists(venv_python):
        print("❌ Ambiente virtual não encontrado!")
        print("Execute: python -m venv .venv")
        return
    
    if not os.path.exists(backend_script):
        print("❌ Script do backend não encontrado!")
        return
    
    print("Iniciando servidor backend...")
    print("Acesse: http://localhost:5000/api")
    print("Pressione Ctrl+C para parar")
    print("-" * 50)
    
    try:
        subprocess.run([venv_python, backend_script], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == '__main__':
    main()
