import os
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

BACKEND_SERVICE = """[Unit]
Description=Cotizador Pro Backend Service
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}
ExecStart={python_path} -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""

FRONTEND_SERVICE = """[Unit]
Description=Cotizador Pro Frontend Service
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/frontend-react
ExecStart=/usr/bin/env npx serve -s dist -l 5173
Restart=always

[Install]
WantedBy=multi-user.target
"""

def generate_service():
    """Genera e instala archivos de systemd para backend y frontend"""
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    user = os.environ.get("USER", "root")
    python_path = os.path.join(cwd, "venv", "bin", "python")
    
    if os.name == 'nt':
        python_path = os.path.join(cwd, "venv", "Scripts", "python.exe")

    back_content = BACKEND_SERVICE.format(user=user, cwd=cwd, python_path=python_path)
    front_content = FRONTEND_SERVICE.format(user=user, cwd=cwd)
    
    back_path = os.path.join(cwd, "cotizador-backend.service")
    front_path = os.path.join(cwd, "cotizador-frontend.service")
    
    with open(back_path, "w") as f:
        f.write(back_content)
    with open(front_path, "w") as f:
        f.write(front_content)
        
    if os.name == 'posix':
        console.print("[cyan]Instalando servicios automáticamente en Linux...[/cyan]")
        try:
            subprocess.run(["sudo", "cp", back_path, "/etc/systemd/system/"], check=True)
            subprocess.run(["sudo", "cp", front_path, "/etc/systemd/system/"], check=True)
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "cotizador-backend"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "cotizador-frontend"], check=True)
            console.print("[green]Servicios (backend y frontend) instalados y habilitados exitosamente.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error al instalar servicios. Asegúrate de tener permisos sudo: {e}[/red]")
    else:
        console.print(Panel(f"Estás en Windows.\nSe han generado los archivos localmente:\n- {back_path}\n- {front_path}\n\nEn Linux este proceso será 100% automático.", title="Servicios Generados", border_style="yellow"))

def run_systemctl(command):
    if os.name != 'posix':
        console.print("[red]Este comando solo funciona de forma automatizada en sistemas Linux con systemd.[/red]")
        return
        
    try:
        subprocess.run(["sudo", "systemctl", command, "cotizador-backend", "cotizador-frontend"], check=True)
        console.print(f"[green]Comando '{command}' ejecutado exitosamente para backend y frontend.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error al ejecutar systemctl: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo Sistema (Servicios Linux) ---[/bold blue]")
        console.print("1. Generar e Instalar Servicios (Backend y Frontend)")
        console.print("2. Iniciar Servicios (start)")
        console.print("3. Detener Servicios (stop)")
        console.print("4. Reiniciar Servicios (restart)")
        console.print("5. Ver Estado (status)")
        console.print("0. Volver")
        
        choice = input("Opcion: ")
        if choice == '1':
            generate_service()
        elif choice == '2':
            run_systemctl("start")
        elif choice == '3':
            run_systemctl("stop")
        elif choice == '4':
            run_systemctl("restart")
        elif choice == '5':
            run_systemctl("status")
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
