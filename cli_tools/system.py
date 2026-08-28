import os
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

SERVICE_TEMPLATE = """[Unit]
Description=Cotizador Pro Backend Service
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}
ExecStart={python_path} -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""

def generate_service():
    """Genera archivo de systemd cotizador.service"""
    if os.name != 'posix':
        console.print("[yellow]Advertencia: Generación de servicios Linux en Windows. Solo se creará el archivo localmente.[/yellow]")
    
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    user = os.environ.get("USER", "root")
    python_path = os.path.join(cwd, "venv", "bin", "python")
    
    if os.name == 'nt':
        python_path = os.path.join(cwd, "venv", "Scripts", "python.exe")

    service_content = SERVICE_TEMPLATE.format(user=user, cwd=cwd, python_path=python_path)
    
    output_path = os.path.join(cwd, "cotizador.service")
    with open(output_path, "w") as f:
        f.write(service_content)
        
    console.print(Panel(f"Archivo de servicio generado en:\n{output_path}\n\nPara instalar en Linux:\nsudo cp cotizador.service /etc/systemd/system/\nsudo systemctl daemon-reload\nsudo systemctl enable cotizador\nsudo systemctl start cotizador", title="Servicio Generado", border_style="green"))

def run_systemctl(command):
    if os.name != 'posix':
        console.print("[red]Este comando solo funciona en sistemas Linux con systemd.[/red]")
        return
        
    try:
        subprocess.run(["sudo", "systemctl", command, "cotizador"], check=True)
        console.print(f"[green]Comando '{command}' ejecutado exitosamente.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error al ejecutar systemctl: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo Sistema (Servicios Linux) ---[/bold blue]")
        console.print("1. Generar cotizador.service")
        console.print("2. Iniciar Servicio (start)")
        console.print("3. Detener Servicio (stop)")
        console.print("4. Reiniciar Servicio (restart)")
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
