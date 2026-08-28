import os
import subprocess
import shutil
import glob
import json
import sys
import re
from rich.console import Console

console = Console()

def get_tauri_version():
    conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tauri-app', 'src-tauri', 'tauri.conf.json'))
    if os.path.exists(conf_path):
        try:
            with open(conf_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        except Exception:
            pass
    return '1.0.0'

def get_upload_url():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    ip = ""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                conf = json.load(f)
                ip = conf.get("backend_ip", "")
        except Exception:
            pass
            
    if not ip:
        console.print("[yellow]No hay servidor configurado para subir la App.[/yellow]")
        ip = input("Introduce la IP o Dominio del Servidor Backend (ej. http://157.173.102.129:8000): ").strip()
        if not ip.startswith("http"):
            ip = "http://" + ip
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({"backend_ip": ip}, f, indent=4)
            
    return ip

def upload_apk_to_store(apk_path, version, app_id="cotizador", app_name="Cotizador Pro", description="", icon_path=None):
    if not icon_path or not os.path.exists(icon_path):
        # Default icon if none provided
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tauri-app', 'icons', '128x128.png'))
        
    base_url = get_upload_url()
    upload_url = f"{base_url.rstrip('/')}/api/store/upload"
    
    console.print(f"[cyan]Subiendo {app_name} V{version} a la Tienda Web ({upload_url})...[/cyan]")
    
    try:
        import requests
    except ImportError:
        console.print("[cyan]Instalando requests...[/cyan]")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests
        
    try:
        files = {
            'apk_file': (os.path.basename(apk_path), open(apk_path, 'rb'), 'application/vnd.android.package-archive'),
        }
        if os.path.exists(icon_path):
            files['icon_file'] = ('icon.png', open(icon_path, 'rb'), 'image/png')
            
        data = {
            'app_id': app_id,
            'app_name': app_name,
            'description': description,
            'version': version
        }
        response = requests.post(upload_url, files=files, data=data)
        if response.status_code == 200:
            console.print("[green]¡APK subido y publicado en la tienda exitosamente![/green]")
        else:
            console.print(f"[red]Error del servidor al subir APK: {response.text}[/red]")
    except Exception as e:
        console.print(f"[red]Error de red al subir APK: {e}[/red]")

def manual_apk_upload():
    console.print("\n[bold blue]--- Subir APK Manualmente ---[/bold blue]")
    apk_path = input("Ruta del archivo APK: ").strip()
    
    # Remove quotes if dragged in windows terminal
    if apk_path.startswith('"') and apk_path.endswith('"'):
        apk_path = apk_path[1:-1]
        
    if not os.path.exists(apk_path):
        console.print("[red]El archivo no existe.[/red]")
        return
        
    filename = os.path.basename(apk_path)
    
    # Parse Nombre-V1.2.3.apk
    match = re.match(r"^(.+?)-V([\d\.]+)\.apk$", filename, re.IGNORECASE)
    if not match:
        console.print(f"[red]El nombre del archivo '{filename}' no cumple el formato requerido: NombreApp-V1.2.3.apk[/red]")
        return
        
    app_id = match.group(1).lower().replace(" ", "-")
    app_name = match.group(1)
    version = match.group(2)
    
    console.print(f"[green]App detectada: {app_name} | Versión: {version}[/green]")
    
    description = input("Descripción de la App (Opcional): ").strip()
    icon_path = input("Ruta del icono PNG (Opcional): ").strip()
    if icon_path.startswith('"') and icon_path.endswith('"'):
        icon_path = icon_path[1:-1]
        
    upload_apk_to_store(apk_path, version, app_id, app_name, description, icon_path)

def build_frontend():
    console.print("[cyan]Compilando Frontend (React)...[/cyan]")
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend-react'))
    if not os.path.exists(cwd):
        console.print("[red]No se encontro la carpeta frontend-react[/red]")
        return
        
    try:
        if not os.path.exists(os.path.join(cwd, "node_modules")):
            console.print("[yellow]Falta node_modules. Instalando dependencias (npm install)...[/yellow]")
            subprocess.run(["npm", "install"], cwd=cwd, check=True, shell=(os.name=='nt'))
            
        subprocess.run(["npm", "run", "build"], cwd=cwd, check=True, shell=(os.name=='nt'))
        console.print("[green]Frontend compilado exitosamente.[/green]")
    except subprocess.CalledProcessError as e:
        console.print("[yellow]Fallo la compilacion, intentando reparar dependencias (npm install)...[/yellow]")
        try:
            subprocess.run(["npm", "install"], cwd=cwd, check=True, shell=(os.name=='nt'))
            subprocess.run(["npm", "run", "build"], cwd=cwd, check=True, shell=(os.name=='nt'))
            console.print("[green]Frontend compilado exitosamente.[/green]")
        except subprocess.CalledProcessError as e2:
            console.print(f"[red]Error critico compilando frontend: {e2}[/red]")
            console.print("[yellow]Intenta ejecutar 'npm install' manualmente en la carpeta frontend-react.[/yellow]")

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
        
        if target == "android":
            # Copy APK to media/release (for local fallback)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            release_dir = os.path.join(base_dir, "media", "release")
            os.makedirs(release_dir, exist_ok=True)
            
            apk_path = os.path.join(cwd, "src-tauri", "gen", "android", "app", "build", "outputs", "apk", "universal", "release", "app-universal-release.apk")
            if not os.path.exists(apk_path):
                apk_search = glob.glob(os.path.join(cwd, "src-tauri", "gen", "android", "app", "build", "outputs", "apk", "**", "*.apk"), recursive=True)
                if apk_search:
                    apk_path = apk_search[0]
            
            if os.path.exists(apk_path):
                dest_path = os.path.join(release_dir, "cotizador-app.apk")
                shutil.copy2(apk_path, dest_path)
                console.print(f"[green]APK respaldado localmente en: {dest_path}[/green]")
                
                # Upload to store
                version = get_tauri_version()
                upload_apk_to_store(apk_path, version, app_id="cotizador", app_name="Cotizador Pro", description="App oficial de Cotizador Pro para dispositivos móviles.")
            else:
                console.print("[yellow]Advertencia: No se encontro el archivo APK compilado en las rutas esperadas.[/yellow]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error compilando Tauri: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo de Compilacion (Build) ---[/bold blue]")
        console.print("1. Compilar Frontend Web (Vite/React)")
        console.print("2. Compilar App Escritorio (Tauri Windows/PC)")
        console.print("3. Compilar App Movil (Android APK)")
        console.print("4. Compilar Todo (Web + PC + Android)")
        console.print("5. Subir APK manualmente a la Tienda")
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
        elif choice == '5':
            manual_apk_upload()
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
