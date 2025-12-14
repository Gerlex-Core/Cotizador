"""
Cotizador Pro - Professional Quotation System
Main entry point for the application.
"""

import sys
import os

# Add src to path for package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QGuiApplication

from src.views.main_window import MainWindow
from src.logic.config.config_manager import get_config


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Cotizador Pro")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("Cotizador")
    
    # Enable high DPI scaling

    
    # Load config and apply default font
    config = get_config()
    font_size = max(8, config.tamaño_fuente)  # Ensure valid font size
    default_font = QFont(config.fuente, font_size)
    app.setFont(default_font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
