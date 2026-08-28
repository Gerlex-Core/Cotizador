"""
Cotizador Pro - Mini Servidor Web Launcher (FastAPI + Uvicorn)
Runs local web server listening on 0.0.0.0:8000 and opens browser automatically.
"""

import sys
import os
import time
import threading
import webbrowser
import uvicorn

# Ensure src is on Python PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.app import app

import socket

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def open_browser():
    """Wait for server startup and log URLs."""
    time.sleep(1.5)
    ip = get_ip_address()
    print(f"\n🚀 Cotizador Pro Backend Activo (Modo API)!")
    print(f"🌐 Acceso local (React/Tauri) apunta a: http://localhost:8000")
    print(f"📡 Acceso en red local apunta a: http://{ip}:8000\n")
    # No abrimos el navegador automáticamente aquí para evitar confusión con el frontend React
    # webbrowser.open(url)


def main():
    """Start uvicorn server listening on 0.0.0.0:8000."""
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
