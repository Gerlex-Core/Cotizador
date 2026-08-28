"""
Cotizador Pro - Mini Servidor Web Modular
Primary entry point for the application.
"""

import sys
import os

# Ensure src is on Python PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import main

if __name__ == "__main__":
    main()
