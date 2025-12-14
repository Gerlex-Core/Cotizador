"""
Unit Converter - Handles unit measurements and conversions.
Refactored from medidas.py for cleaner architecture.
"""

import os
import json
from typing import Dict, List, Optional


# Paths
# Paths
CONFIG_DATA_DIR = os.path.join("media", "data", "units")
UNITS_FILE = os.path.join(CONFIG_DATA_DIR, "units.json")
LEGACY_UNITS_FILE = os.path.join("medidas.json")


# Default units data
DEFAULT_UNITS = {
    "cantidad": {
        "unidad (u)": {"abreviacion": "u", "factor": 1.0},
        "cada uno (c/u)": {"abreviacion": "c/u", "factor": 1.0},
        "paquete (pqt)": {"abreviacion": "pqt", "factor": 1.0},
        "docena (dz)": {"abreviacion": "dz", "factor": 12.0},
        "centena (ct)": {"abreviacion": "ct", "factor": 100.0},
        "millar (mll)": {"abreviacion": "mll", "factor": 1000.0},
        "caja (caja)": {"abreviacion": "caja", "factor": 1.0},
        "bulto (bulto)": {"abreviacion": "bulto", "factor": 1.0}
    },
    "longitud": {
        "metros (m)": {"abreviacion": "m", "factor": 1.0},
        "kilómetros (km)": {"abreviacion": "km", "factor": 0.001},
        "centímetros (cm)": {"abreviacion": "cm", "factor": 100.0},
        "milímetros (mm)": {"abreviacion": "mm", "factor": 1000.0},
        "pulgadas (in)": {"abreviacion": "in", "factor": 39.3701},
        "pies (ft)": {"abreviacion": "ft", "factor": 3.28084}
    },
    "peso": {
        "gramos (g)": {"abreviacion": "g", "factor": 1.0},
        "kilogramos (kg)": {"abreviacion": "kg", "factor": 0.001},
        "toneladas (t)": {"abreviacion": "t", "factor": 0.000001},
        "libras (lb)": {"abreviacion": "lb", "factor": 0.00220462},
        "onzas (oz)": {"abreviacion": "oz", "factor": 0.035274}
    },
    "volumen": {
        "litros (L)": {"abreviacion": "L", "factor": 1.0},
        "mililitros (mL)": {"abreviacion": "mL", "factor": 1000.0},
        "metros cúbicos (m³)": {"abreviacion": "m³", "factor": 0.001},
        "galones (gal)": {"abreviacion": "gal", "factor": 0.264172}
    },
    "tiempo": {
        "segundos (s)": {"abreviacion": "s", "factor": 1.0},
        "minutos (min)": {"abreviacion": "min", "factor": 0.0166667},
        "horas (h)": {"abreviacion": "h", "factor": 0.000277778},
        "días (d)": {"abreviacion": "d", "factor": 0.0000115741}
    },
    "envio": {
        "Envío Local": {"abreviacion": "local", "factor": 1.0},
        "Delivery": {"abreviacion": "delivery", "factor": 1.0},
        "Encomienda": {"abreviacion": "encomienda", "factor": 1.0},
        "Express/Urgente": {"abreviacion": "express", "factor": 1.0},
        "Pickup (Retiro)": {"abreviacion": "pickup", "factor": 1.0},
        "Courier Nacional": {"abreviacion": "courier", "factor": 1.0},
        "Courier Internacional": {"abreviacion": "intl", "factor": 1.0},
        "Flete": {"abreviacion": "flete", "factor": 1.0},
        "Transporte Especializado": {"abreviacion": "especial", "factor": 1.0}
    },
    "servicio": {
        "Instalación": {"abreviacion": "inst", "factor": 1.0},
        "Hora de Soporte": {"abreviacion": "hr/sop", "factor": 1.0},
        "Día de Trabajo": {"abreviacion": "día", "factor": 1.0},
        "Sesión": {"abreviacion": "sesión", "factor": 1.0},
        "Capacitación": {"abreviacion": "cap", "factor": 1.0},
        "Mantenimiento": {"abreviacion": "mant", "factor": 1.0},
        "Consultoría": {"abreviacion": "cons", "factor": 1.0}
    }
}



class UnitConverter:
    """
    Handles unit conversions and provides unit information.
    """
    
    _instance = None
    _data: Dict = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize by loading or creating units data."""
        os.makedirs(CONFIG_DATA_DIR, exist_ok=True)
        
        # Try to load from new location first
        if os.path.exists(UNITS_FILE):
            self._load_data(UNITS_FILE)
        elif os.path.exists(LEGACY_UNITS_FILE):
            # Migrate from legacy location
            self._load_data(LEGACY_UNITS_FILE)
            self._save_data(UNITS_FILE)
        else:
            # Create default
            self._data = DEFAULT_UNITS.copy()
            self._save_data(UNITS_FILE)
    
    def _load_data(self, path: str):
        """Load units data from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except Exception as e:
            print(f"Error loading units: {e}")
            self._data = DEFAULT_UNITS.copy()
    
    def _save_data(self, path: str):
        """Save units data to JSON file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving units: {e}")
    
    def get_categories(self) -> List[str]:
        """Get all unit categories."""
        return list(self._data.keys())
    
    def get_units(self, category: str) -> List[str]:
        """Get all units in a category."""
        if category not in self._data:
            return []
        return list(self._data[category].keys())
    
    def get_abbreviation(self, category: str, unit: str) -> Optional[str]:
        """Get the abbreviation for a unit."""
        if category in self._data and unit in self._data[category]:
            return self._data[category][unit].get("abreviacion")
        return None
    
    def get_factor(self, category: str, unit: str) -> Optional[float]:
        """Get the conversion factor for a unit."""
        if category in self._data and unit in self._data[category]:
            return self._data[category][unit].get("factor")
        return None
    
    def convert(self, value: float, from_unit: str, to_unit: str, 
                category: str) -> Optional[float]:
        """
        Convert a value from one unit to another within the same category.
        """
        if category not in self._data:
            return None
        
        if from_unit not in self._data[category] or to_unit not in self._data[category]:
            return None
        
        from_factor = self._data[category][from_unit]["factor"]
        to_factor = self._data[category][to_unit]["factor"]
        
        # Convert to base unit, then to target unit
        return (value / from_factor) * to_factor
    
    def get_all_units_grouped(self) -> Dict[str, List[str]]:
        """
        Get all units grouped by category.
        Useful for populating combo boxes.
        """
        return {
            category: list(units.keys())
            for category, units in self._data.items()
        }
    
    def find_unit_category(self, unit: str) -> Optional[str]:
        """Find which category a unit belongs to."""
        for category, units in self._data.items():
            if unit in units:
                return category
        return None


# Singleton accessor
def get_unit_converter() -> UnitConverter:
    """Get the singleton UnitConverter instance."""
    return UnitConverter()


# Legacy compatibility class
class Medidas:
    """Legacy compatibility class for medidas.py."""
    
    FILE_PATH = LEGACY_UNITS_FILE
    
    @classmethod
    def cargar_datos(cls):
        """Load unit data."""
        converter = get_unit_converter()
        return converter._data
    
    @classmethod
    def obtener_categorias(cls) -> List[str]:
        """Get all categories."""
        return get_unit_converter().get_categories()
    
    @classmethod
    def obtener_unidades(cls, categoria: str) -> List[str]:
        """Get units for a category."""
        return get_unit_converter().get_units(categoria)
    
    @classmethod
    def obtener_abreviacion(cls, unidad: str, categoria: str) -> Optional[str]:
        """Get abbreviation for a unit."""
        return get_unit_converter().get_abbreviation(categoria, unidad)
    
    @classmethod
    def convertir(cls, cantidad: float, de_unidad: str, 
                  a_unidad: str, categoria: str) -> Optional[float]:
        """Convert between units."""
        return get_unit_converter().convert(cantidad, de_unidad, a_unidad, categoria)
