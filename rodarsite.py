import os
import subprocess
import sys
import webbrowser
from pathlib import Path
import socket


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
    python_exe = str(Path('.venv') / 'Scripts' / 'python.exe' if os.name == 'nt' else Path('.venv') / 'bin' / 'python')
    print("\nIniciando o backend (Flask API)...\n")
    return subprocess.Popen([python_exe, 'backend/run.py'])


def open_frontend():
    print("\nAcesse o site pelo navegador:\n")
    print("   → http://localhost:5000/")
    for ip in get_local_ips():
        if not ip.startswith('127.'):
            print(f"   → http://{ip}:5000/")
    print("\nSe não abrir automaticamente, copie e cole um destes no seu navegador!")
    webbrowser.open_new_tab('http://localhost:5000/')


def main():
    backend_proc = start_backend()
    open_frontend()
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print('\nEncerrando aplicação!')
        backend_proc.terminate()

if __name__ == '__main__':
    main()
