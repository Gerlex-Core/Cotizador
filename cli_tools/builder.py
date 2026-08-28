import os
import subprocess
from rich.console import Console

console = Console()

def build_frontend():
    console.print("[cyan]Compilando Frontend (React)...[/cyan]")
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend-react'))
    if not os.path.exists(cwd):
        console.print("[red]No se encontro la carpeta frontend-react[/red]")
        return
        
    try:
        subprocess.run(["npm", "run", "build"], cwd=cwd, check=True, shell=(os.name=='nt'))
        console.print("[green]Frontend compilado exitosamente.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error compilando frontend: {e}[/red]")

def build_tauri(target="desktop"):
    if target == "android":
        console.print("[cyan]Compilando App Movil (Android APK)...[/cyan]")
        cmd = ["npm", "run", "tauri", "android", "build"]
    else:
        console.print("[cyan]Compilando App Escritorio (Tauri PC)...[/cyan]")
        cmd = ["npm", "run", "tauri", "build"]

    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tauri-app'))
    if not os.path.exists(cwd):
        console.print("[red]No se encontro la carpeta tauri-app[/red]")
        return
        
    try:
        subprocess.run(cmd, cwd=cwd, check=True, shell=(os.name=='nt'))
        console.print("[green]Aplicacion nativa compilada exitosamente.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error compilando Tauri: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo de Compilacion (Build) ---[/bold blue]")
        console.print("1. Compilar Frontend Web (Vite/React)")
        console.print("2. Compilar App Escritorio (Tauri Windows/PC)")
        console.print("3. Compilar App Movil (Android APK)")
        console.print("4. Compilar Todo (Web + PC + Android)")
        console.print("0. Volver")
        
        choice = input("Opcion: ")
        if choice == '1':
            build_frontend()
        elif choice == '2':
            build_tauri(target="desktop")
        elif choice == '3':
            build_tauri(target="android")
        elif choice == '4':
            build_frontend()
            build_tauri(target="desktop")
            build_tauri(target="android")
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
