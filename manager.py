import os
import sys
from rich.console import Console

# Asegurar que el modulo local puede ser importado
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cli_tools import system, database, installers, builder

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear_screen()
        console.print("[bold blue]=== COTIZADOR PRO - DEVOPS MANAGER ===[/bold blue]")
        console.print("1. Sistema (Servicios Linux)")
        console.print("2. Base de Datos (Migraciones y Datos)")
        console.print("3. Instaladores (Dependencias)")
        console.print("4. Build (Compilar Frontend/Movil)")
        console.print("0. Salir")
        console.print("[bold blue]======================================[/bold blue]")
        
        choice = input("Selecciona una opcion: ")
        
        if choice == '1':
            clear_screen()
            system.menu()
        elif choice == '2':
            clear_screen()
            database.menu()
        elif choice == '3':
            clear_screen()
            installers.menu()
        elif choice == '4':
            clear_screen()
            builder.menu()
        elif choice == '0':
            console.print("[green]Saliendo...[/green]")
            break
        else:
            console.print("[red]Opcion invalida, intenta de nuevo.[/red]")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[green]Saliendo abruptamente...[/green]")
        sys.exit(0)
