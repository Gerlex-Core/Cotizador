import os
import json
import glob
import requests
from rich.console import Console

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_files(folder_path, app_name, version):
    apk_files = glob.glob(os.path.join(folder_path, "*.apk"))
    
    # Busca imagenes (png, jpg, jpeg)
    all_images = glob.glob(os.path.join(folder_path, "*.png")) + \
                 glob.glob(os.path.join(folder_path, "*.jpg")) + \
                 glob.glob(os.path.join(folder_path, "*.jpeg")) + \
                 glob.glob(os.path.join(folder_path, "*.svg"))
                 
    # Busca json
    all_jsons = glob.glob(os.path.join(folder_path, "*.json"))
    
    def find_all_matches(files, app, ver):
        specific = None
        general = None
        specific_name = f"{app}-V{ver}".lower()
        for f in files:
            if specific_name in os.path.basename(f).lower():
                specific = f
            elif app.lower() in os.path.basename(f).lower():
                if not general:
                    general = f
        if not specific and not general and files:
            general = files[0]
        return specific, general

    spec_img, gen_img = find_all_matches(all_images, app_name, version)
    spec_json, gen_json = find_all_matches(all_jsons, app_name, version)

    return {
        "apk": apk_files[0] if apk_files else None,
        "app_image": gen_img,
        "version_image": spec_img,
        "app_json": gen_json,
        "version_json": spec_json
    }

def process_upload():
    console.print("[bold cyan]=== SUBIR APP A LA TIENDA ===[/bold cyan]")
    console.print("El formato de la carpeta debe ser: [bold green]NombreApp-V1.0.0[/bold green]")
    folder_path = input("Ingresa la ruta completa de la carpeta: ").strip()
    
    if not os.path.isdir(folder_path):
        console.print("[red]Error: La carpeta no existe.[/red]")
        input("Presiona Enter para volver...")
        return
        
    folder_name = os.path.basename(os.path.normpath(folder_path))
    
    if "-V" not in folder_name:
        console.print("[red]Error: El nombre de la carpeta no tiene el formato NombreApp-V#.#.#[/red]")
        input("Presiona Enter para volver...")
        return
        
    app_id = folder_name.split("-V")[0].strip().lower().replace(" ", "_")
    app_name = folder_name.split("-V")[0].strip()
    version = folder_name.split("-V")[1].strip()
    
    console.print(f"[yellow]Analizando...[/yellow]")
    console.print(f"App ID: {app_id}")
    console.print(f"Nombre: {app_name}")
    console.print(f"Versión: {version}")
    
    files = get_files(folder_path, app_name, version)
    
    if not files["apk"]:
        console.print("[red]Error: No se encontró ningún archivo .apk en la carpeta.[/red]")
        input("Presiona Enter para volver...")
        return
        
    app_description = ""
    if files["app_json"]:
        try:
            with open(files["app_json"], "r", encoding="utf-8") as f:
                data = json.load(f)
                app_description = data.get("description", "") or data.get("descripcion", "")
            console.print(f"[green]Metadatos generales cargados desde {os.path.basename(files['app_json'])}[/green]")
        except Exception as e:
            pass
            
    version_description = ""
    if files["version_json"]:
        try:
            with open(files["version_json"], "r", encoding="utf-8") as f:
                data = json.load(f)
                version_description = data.get("description", "") or data.get("descripcion", "")
            console.print(f"[green]Metadatos específicos cargados desde {os.path.basename(files['version_json'])}[/green]")
        except Exception as e:
            pass

    api_url = input("URL de la API (ej. http://127.0.0.1:8000 o http://tu-dominio.com) [http://127.0.0.1:8000]: ").strip()
    if not api_url:
        api_url = "http://127.0.0.1:8000"
        
    endpoint = f"{api_url}/api/store/upload"
    
    console.print(f"\n[cyan]Subiendo a {endpoint}...[/cyan]")
    
    try:
        with open(files["apk"], "rb") as apk_file:
            files_payload = {
                "apk_file": (os.path.basename(files["apk"]), apk_file, "application/vnd.android.package-archive")
            }
            
            app_icon_file = None
            if files["app_image"]:
                app_icon_file = open(files["app_image"], "rb")
                files_payload["app_icon_file"] = (os.path.basename(files["app_image"]), app_icon_file, "image/jpeg" if files["app_image"].endswith("jpg") else "image/png")
                
            version_icon_file = None
            if files["version_image"]:
                version_icon_file = open(files["version_image"], "rb")
                files_payload["version_icon_file"] = (os.path.basename(files["version_image"]), version_icon_file, "image/jpeg" if files["version_image"].endswith("jpg") else "image/png")

            data_payload = {
                "app_id": app_id,
                "app_name": app_name,
                "app_description": app_description,
                "version_description": version_description,
                "version": version
            }
            
            response = requests.post(endpoint, data=data_payload, files=files_payload)
            
            if app_icon_file: app_icon_file.close()
            if version_icon_file: version_icon_file.close()
                
            if response.status_code == 200:
                console.print(f"[bold green]¡Éxito! {response.json().get('message', '')}[/bold green]")
            else:
                console.print(f"[red]Error del servidor HTTP {response.status_code}: {response.text}[/red]")
                
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error de conexión: {e}[/red]")
        console.print("[yellow]Asegúrate de que la API de Cotizador Pro esté ejecutándose.[/yellow]")
        
    input("\nPresiona Enter para continuar...")

def menu():
    while True:
        clear_screen()
        console.print("[bold cyan]=== TIENDA DE APPS ===[/bold cyan]")
        console.print("1. Subir paquete de App (Carpeta local)")
        console.print("0. Volver")
        
        choice = input("Selecciona una opcion: ")
        
        if choice == '1':
            process_upload()
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
            input("Presiona Enter para continuar...")
