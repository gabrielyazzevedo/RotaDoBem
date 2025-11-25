import os
import subprocess
import sys
import webbrowser
from pathlib import Path
import socket
import time

def get_local_ips():
    ips = []
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        ips.append(local_ip)
    except:
        pass
    try:
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
    except:
        pass
    return ips

def start_backend():
    # Tenta encontrar o Python do ambiente virtual
    if os.name == 'nt': # Windows
        python_exe = Path('.venv') / 'Scripts' / 'python.exe'
    else: # Linux/Mac
        python_exe = Path('.venv') / 'bin' / 'python'
    
    # Fallback se não achar o venv, usa o python do sistema
    if not python_exe.exists():
        python_exe = sys.executable

    script_path = os.path.join('backend', 'run.py')
    
    if not os.path.exists(script_path):
        print(f"ERRO: O arquivo '{script_path}' não foi encontrado!")
        print("Verifique se você está na pasta correta 'RotaDoBem'.")
        return None

    print(f"\nIniciando o backend usando: {python_exe}")
    print(f"Executando script: {script_path}\n")
    
    return subprocess.Popen([str(python_exe), script_path])

def open_frontend():
    print("\nAguardando servidor iniciar...")
    time.sleep(3) 
    print("\nAcesse o site pelo navegador:\n")
    print("   → http://localhost:5000/")
    for ip in get_local_ips():
        if not ip.startswith('127.'):
            print(f"   → http://{ip}:5000/")
    
    webbrowser.open('http://localhost:5000/')

def main():
    backend_proc = start_backend()
    if not backend_proc:
        input("Pressione ENTER para sair...")
        return

    open_frontend()
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print('\nEncerrando aplicação!')
        backend_proc.terminate()

if __name__ == '__main__':
    main()