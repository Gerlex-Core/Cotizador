"""
Configuration Manager for handling .conf files and settings.
Uses Python's configparser for .conf file format.
"""

import os
import configparser
import json
from typing import Any, Dict, Optional


# Base paths

CONFIG_DIR = os.path.join("media", "config")
COMPANY_DIR = os.path.join("media", "companies")
LEGACY_OPTIONS_FILE = os.path.join("media", "config", "options.json")

# Config files
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.conf")
COMPANIES_FILE = os.path.join(COMPANY_DIR, "companies.conf")


# Default configuration
DEFAULT_SETTINGS = {
    "General": {
        "idioma": "es",
        "moneda": "Bolivianos (Bs)"
    },
    "Appearance": {
        "tema": "Oscuro",
        "fuente": "Arial",
        "tamaño_fuente": "14"
    },
    "PDF": {
        "mostrar_terminos": "true",
        "validez_dias": "30",
        "mostrar_firma": "true",
        # Márgenes (en mm)
        "margin_top": "40",
        "margin_bottom": "40",
        "margin_left": "40",
        "margin_right": "40",
        # Marca de agua
        "watermark_enabled": "false",
        "watermark_text": "",
        "watermark_opacity": "15",
        "watermark_image_path": "",
        # Diseño
        "highlight_color": "#FFFF00"
    },
    "UserProfile": {
        "prepared_by": "",
        "signature_path": ""
    }
}


class ConfigManager:
    """
    Manages application configuration using .conf files.
    Provides migration from legacy JSON format.
    """
    
    _instance = None
    _config: configparser.ConfigParser = None
    
    def __new__(cls):
        """Singleton pattern to ensure one config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the configuration manager."""
        self._config = configparser.ConfigParser()
        
        # Ensure config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Check for migration from legacy format
        if os.path.exists(LEGACY_OPTIONS_FILE) and not os.path.exists(SETTINGS_FILE):
            self._migrate_from_json()
        elif os.path.exists(SETTINGS_FILE):
            self._load_config()
        else:
            self._create_default_config()
    
    def _migrate_from_json(self):
        """Migrate settings from legacy JSON format to .conf format."""
        try:
            with open(LEGACY_OPTIONS_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
            
            # Create new config with migrated values
            self._config.read_dict(DEFAULT_SETTINGS)
            
            # Map old keys to new structure
            if 'idioma' in legacy:
                self._config.set('General', 'idioma', legacy['idioma'])
            if 'moneda' in legacy:
                self._config.set('General', 'moneda', legacy['moneda'])
            if 'tema' in legacy:
                self._config.set('Appearance', 'tema', legacy['tema'])
            if 'fuente' in legacy:
                self._config.set('Appearance', 'fuente', legacy['fuente'])
            if 'tamaño_fuente' in legacy:
                self._config.set('Appearance', 'tamaño_fuente', str(legacy['tamaño_fuente']))
            
            self._save_config()
            print(f"✅ Migrated settings from {LEGACY_OPTIONS_FILE} to {SETTINGS_FILE}")
            
        except Exception as e:
            print(f"⚠️ Migration failed: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create configuration with default values."""
        self._config.read_dict(DEFAULT_SETTINGS)
        self._save_config()
    
    def _load_config(self):
        """Load configuration from file."""
        self._config.read(SETTINGS_FILE, encoding='utf-8')
        
        # Ensure all default sections exist
        for section, options in DEFAULT_SETTINGS.items():
            if not self._config.has_section(section):
                self._config.add_section(section)
            for key, value in options.items():
                if not self._config.has_option(section, key):
                    self._config.set(section, key, value)
    
    def _save_config(self):
        """Save configuration to file."""
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            self._config.write(f)
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get a configuration value."""
        return self._config.get(section, key, fallback=fallback)
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get a configuration value as integer."""
        return self._config.getint(section, key, fallback=fallback)
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a configuration value as boolean."""
        return self._config.getboolean(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: Any):
        """Set a configuration value."""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
    
    def save(self):
        """Save current configuration to file."""
        self._save_config()
    
    def get_all(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration as nested dictionary."""
        result = {}
        for section in self._config.sections():
            result[section] = dict(self._config.items(section))
        return result
    
    # Convenience properties for common settings
    @property
    def idioma(self) -> str:
        return self.get('General', 'idioma', 'es')
    
    @idioma.setter
    def idioma(self, value: str):
        self.set('General', 'idioma', value)
    
    @property
    def moneda(self) -> str:
        return self.get('General', 'moneda', 'Bolivianos (Bs)')
    
    @moneda.setter
    def moneda(self, value: str):
        self.set('General', 'moneda', value)
    
    @property
    def tema(self) -> str:
        return self.get('Appearance', 'tema', 'Oscuro')
    
    @tema.setter
    def tema(self, value: str):
        self.set('Appearance', 'tema', value)
    
    @property
    def fuente(self) -> str:
        return self.get('Appearance', 'fuente', 'Arial')
    
    @fuente.setter
    def fuente(self, value: str):
        self.set('Appearance', 'fuente', value)
    
    @property
    def tamaño_fuente(self) -> int:
        return self.get_int('Appearance', 'tamaño_fuente', 14)
    
    @tamaño_fuente.setter
    def tamaño_fuente(self, value: int):
        self.set('Appearance', 'tamaño_fuente', value)
    
    @property
    def mostrar_terminos(self) -> bool:
        return self.get_bool('PDF', 'mostrar_terminos', True)
    
    @property
    def validez_dias(self) -> int:
        return self.get_int('PDF', 'validez_dias', 30)
    
    @property
    def mostrar_firma(self) -> bool:
        return self.get_bool('PDF', 'mostrar_firma', True)
    
    # PDF Margins
    @property
    def pdf_margin_top(self) -> int:
        return self.get_int('PDF', 'margin_top', 40)
    
    @pdf_margin_top.setter
    def pdf_margin_top(self, value: int):
        self.set('PDF', 'margin_top', value)
    
    @property
    def pdf_margin_bottom(self) -> int:
        return self.get_int('PDF', 'margin_bottom', 40)
    
    @pdf_margin_bottom.setter
    def pdf_margin_bottom(self, value: int):
        self.set('PDF', 'margin_bottom', value)
    
    @property
    def pdf_margin_left(self) -> int:
        return self.get_int('PDF', 'margin_left', 40)
    
    @pdf_margin_left.setter
    def pdf_margin_left(self, value: int):
        self.set('PDF', 'margin_left', value)
    
    @property
    def pdf_margin_right(self) -> int:
        return self.get_int('PDF', 'margin_right', 40)
    
    @pdf_margin_right.setter
    def pdf_margin_right(self, value: int):
        self.set('PDF', 'margin_right', value)
    
    # Watermark
    @property
    def watermark_enabled(self) -> bool:
        return self.get_bool('PDF', 'watermark_enabled', False)
    
    @watermark_enabled.setter
    def watermark_enabled(self, value: bool):
        self.set('PDF', 'watermark_enabled', str(value).lower())
    
    @property
    def watermark_text(self) -> str:
        return self.get('PDF', 'watermark_text', '')
    
    @watermark_text.setter
    def watermark_text(self, value: str):
        self.set('PDF', 'watermark_text', value)
    
    @property
    def watermark_opacity(self) -> int:
        return self.get_int('PDF', 'watermark_opacity', 15)
    
    @watermark_opacity.setter
    def watermark_opacity(self, value: int):
        self.set('PDF', 'watermark_opacity', value)
    
    @property
    def watermark_image_path(self) -> str:
        return self.get('PDF', 'watermark_image_path', '')
    
    @watermark_image_path.setter
    def watermark_image_path(self, value: str):
        self.set('PDF', 'watermark_image_path', value)
    
    # PDF Design
    @property
    def highlight_color(self) -> str:
        return self.get('PDF', 'highlight_color', '#FFFF00')
    
    @highlight_color.setter
    def highlight_color(self, value: str):
        self.set('PDF', 'highlight_color', value)
    
    @property
    def prepared_by(self) -> str:
        return self.get('UserProfile', 'prepared_by', '')
    
    @prepared_by.setter
    def prepared_by(self, value: str):
        self.set('UserProfile', 'prepared_by', value)
    
    @property
    def signature_path(self) -> str:
        return self.get('UserProfile', 'signature_path', '')
    
    @signature_path.setter
    def signature_path(self, value: str):
        self.set('UserProfile', 'signature_path', value)
    
    def to_legacy_dict(self) -> dict:
        """Convert config to legacy dictionary format for compatibility."""
        return {
            "idioma": self.idioma,
            "moneda": self.moneda,
            "tema": self.tema,
            "fuente": self.fuente,
            "tamaño_fuente": self.tamaño_fuente
        }


# Singleton instance
def get_config() -> ConfigManager:
    """Get the singleton ConfigManager instance."""
    return ConfigManager()
