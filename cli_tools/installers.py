import os
import subprocess
from rich.console import Console

console = Console()

def install_backend():
    console.print("[cyan]Instalando dependencias de Backend (Python)...[/cyan]")
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    req_file = os.path.join(cwd, "requirements.txt")
    if not os.path.exists(req_file):
        console.print("[red]No se encontro requirements.txt[/red]")
        return
        
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
        console.print("[green]Dependencias de backend instaladas.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error instalando backend: {e}[/red]")
    except NameError:
        import sys
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)

def install_frontend():
    console.print("[cyan]Instalando dependencias de Frontend (React)...[/cyan]")
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend-react'))
    if not os.path.exists(cwd):
        console.print("[red]No se encontro la carpeta frontend-react[/red]")
        return
        
    try:
        # Use shell=True on Windows for npm
        subprocess.run(["npm", "install"], cwd=cwd, check=True, shell=(os.name=='nt'))
        console.print("[green]Dependencias de frontend instaladas.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error instalando frontend: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo Instaladores ---[/bold blue]")
        console.print("1. Instalar Backend (pip)")
        console.print("2. Instalar Frontend (npm)")
        console.print("3. Instalar Todo")
        console.print("0. Volver")
        
        choice = input("Opcion: ")
        if choice == '1':
            install_backend()
        elif choice == '2':
            install_frontend()
        elif choice == '3':
            install_backend()
            install_frontend()
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
