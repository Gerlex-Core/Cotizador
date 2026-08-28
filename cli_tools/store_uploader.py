import os
import json
import glob
import requests
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TaskProgressColumn
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_files(folder_path, app_name, version):
    package_files = glob.glob(os.path.join(folder_path, "*.apk")) + glob.glob(os.path.join(folder_path, "*.zip"))
    
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
        "package": package_files[0] if package_files else None,
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
    
    if not files["package"]:
        console.print("[red]Error: No se encontró ningún archivo .apk ni .zip en la carpeta.[/red]")
        input("Presiona Enter para volver...")
        return
        
    app_description = ""
    app_category = "General"
    app_developer = ""
    app_release_date = ""
    app_website = ""
    app_tags = ""
    app_content_rating = "Todos"

    if files["app_json"]:
        try:
            with open(files["app_json"], "r", encoding="utf-8") as f:
                data = json.load(f)
                app_description = data.get("description", "") or data.get("descripcion", "")
                app_category = data.get("category", "") or data.get("categoria", "") or "General"
                app_developer = data.get("developer", "") or data.get("desarrollador", "")
                app_release_date = data.get("release_date", "") or data.get("fecha_lanzamiento", "")
                app_website = data.get("website", "") or data.get("sitio_web", "")
                
                tags_data = data.get("tags", "") or data.get("etiquetas", "")
                app_tags = ", ".join(tags_data) if isinstance(tags_data, list) else tags_data
                
                app_content_rating = data.get("content_rating", "") or data.get("clasificacion", "") or "Todos"
                
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
        
    admin_token = input("Token de Administrador: ").strip()
    if not admin_token:
        console.print("[red]Error: El token de administrador es obligatorio para subir aplicaciones.[/red]")
        input("Presiona Enter para continuar...")
        return
        
    endpoint = f"{api_url}/api/store/upload"
    
    console.print(f"\n[cyan]Subiendo a {endpoint}...[/cyan]")
    
    try:
        opened_files = []
        mime_type = "application/zip" if files["package"].endswith(".zip") else "application/vnd.android.package-archive"
        
        fields = {
            "app_id": str(app_id),
            "app_name": str(app_name),
            "app_description": str(app_description),
            "version_description": str(version_description),
            "category": str(app_category),
            "developer": str(app_developer),
            "release_date": str(app_release_date),
            "website": str(app_website),
            "tags": str(app_tags),
            "content_rating": str(app_content_rating),
            "version": str(version)
        }
        
        pkg_file = open(files["package"], "rb")
        opened_files.append(pkg_file)
        fields["package_file"] = (os.path.basename(files["package"]), pkg_file, mime_type)
        
        if files["app_image"]:
            app_img = open(files["app_image"], "rb")
            opened_files.append(app_img)
            fields["app_icon_file"] = (os.path.basename(files["app_image"]), app_img, "image/jpeg" if files["app_image"].endswith("jpg") else "image/png")
            
        if files["version_image"]:
            ver_img = open(files["version_image"], "rb")
            opened_files.append(ver_img)
            fields["version_icon_file"] = (os.path.basename(files["version_image"]), ver_img, "image/jpeg" if files["version_image"].endswith("jpg") else "image/png")

        encoder = MultipartEncoder(fields=fields)
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Subiendo datos...", total=encoder.len)
            
            def callback(monitor):
                progress.update(task, completed=monitor.bytes_read)
                
            monitor = MultipartEncoderMonitor(encoder, callback)
            
            headers = {
                "Content-Type": monitor.content_type,
                "Authorization": f"Bearer {admin_token}"
            }
            
            response = requests.post(endpoint, data=monitor, headers=headers)
            
        for f in opened_files:
            f.close()
            
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
