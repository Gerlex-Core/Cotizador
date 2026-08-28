import os
import sys
from rich.console import Console
from rich.table import Table

# Add root directory to sys path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.database import init_db, list_quotations_from_db, get_connection

console = Console()

def run_migrations():
    """Inicializa o actualiza la base de datos."""
    console.print("[cyan]Iniciando migraciones de Base de Datos...[/cyan]")
    try:
        init_db()
        console.print("[green]Migraciones completadas exitosamente.[/green]")
    except Exception as e:
        console.print(f"[red]Error en migraciones: {e}[/red]")

def view_data():
    """Muestra los datos actuales de cotizaciones."""
    console.print("[cyan]Obteniendo registros...[/cyan]")
    try:
        rows = list_quotations_from_db()
        if not rows:
            console.print("[yellow]La base de datos está vacía.[/yellow]")
            return

        table = Table(title="Cotizaciones Recientes")
        table.add_column("Número", style="cyan", no_wrap=True)
        table.add_column("Cliente", style="magenta")
        table.add_column("Fecha", justify="right", style="green")
        table.add_column("Total", justify="right", style="yellow")

        for row in rows[:20]: # Show last 20
            table.add_row(
                row.get("quotation_number", "N/A"),
                row.get("client_name", "N/A"),
                row.get("date", "N/A"),
                f"${row.get('total', 0):.2f}"
            )
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error al leer la base de datos: {e}[/red]")

def menu():
    while True:
        console.print("\n[bold blue]--- Modulo Base de Datos ---[/bold blue]")
        console.print("1. Ejecutar Migraciones (init_db)")
        console.print("2. Ver Cotizaciones (Tabla)")
        console.print("0. Volver")
        
        choice = input("Opcion: ")
        if choice == '1':
            run_migrations()
        elif choice == '2':
            view_data()
        elif choice == '0':
            break
        else:
            console.print("[red]Opcion invalida.[/red]")
