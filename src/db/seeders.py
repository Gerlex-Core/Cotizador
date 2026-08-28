"""
Comprehensive Seeders Module for SQLite Database.
Populates extensive measurement units, standard terms, and default companies.
"""

from typing import List, Dict, Any

SEED_UNITS: List[Dict[str, str]] = [
    # Unidades Contables & Embalaje
    {"category": "unidades", "code": "u", "name": "unidad (u)"},
    {"category": "unidades", "code": "pz", "name": "pieza (pz)"},
    {"category": "unidades", "code": "cj", "name": "caja (cj)"},
    {"category": "unidades", "code": "pq", "name": "paquete (pq)"},
    {"category": "unidades", "code": "jg", "name": "juego (jg)"},
    {"category": "unidades", "code": "doc", "name": "docena (doc)"},
    {"category": "unidades", "code": "cto", "name": "ciento (cto)"},
    {"category": "unidades", "code": "mil", "name": "millar (mil)"},
    {"category": "unidades", "code": "plt", "name": "pallet (plt)"},
    {"category": "unidades", "code": "tmb", "name": "tambor (tmb)"},
    {"category": "unidades", "code": "bls", "name": "bolsa (bls)"},
    {"category": "unidades", "code": "rll", "name": "rollo (rll)"},
    {"category": "unidades", "code": "fdo", "name": "fardo (fdo)"},
    {"category": "unidades", "code": "kit", "name": "kit (kit)"},
    {"category": "unidades", "code": "par", "name": "par (par)"},
    {"category": "unidades", "code": "lote", "name": "lote (lt)"},

    # Longitud & Distancia
    {"category": "longitud", "code": "m", "name": "metro (m)"},
    {"category": "longitud", "code": "cm", "name": "centímetro (cm)"},
    {"category": "longitud", "code": "mm", "name": "milímetro (mm)"},
    {"category": "longitud", "code": "km", "name": "kilómetro (km)"},
    {"category": "longitud", "code": "in", "name": "pulgada (in)"},
    {"category": "longitud", "code": "ft", "name": "pie (ft)"},
    {"category": "longitud", "code": "yd", "name": "yarda (yd)"},

    # Superficie & Área
    {"category": "superficie", "code": "m²", "name": "metro cuadrado (m²)"},
    {"category": "superficie", "code": "cm²", "name": "centímetro cuadrado (cm²)"},
    {"category": "superficie", "code": "ha", "name": "hectárea (ha)"},
    {"category": "superficie", "code": "ft²", "name": "pie cuadrado (ft²)"},
    {"category": "superficie", "code": "in²", "name": "pulgada cuadrada (in²)"},

    # Volumen & Capacidad
    {"category": "volumen", "code": "m³", "name": "metro cúbico (m³)"},
    {"category": "volumen", "code": "cm³", "name": "centímetro cúbico (cm³)"},
    {"category": "volumen", "code": "L", "name": "litro (L)"},
    {"category": "volumen", "code": "mL", "name": "mililitro (mL)"},
    {"category": "volumen", "code": "gal", "name": "galón (gal)"},
    {"category": "volumen", "code": "bbl", "name": "barril (bbl)"},

    # Peso & Masa
    {"category": "peso", "code": "kg", "name": "kilogramo (kg)"},
    {"category": "peso", "code": "g", "name": "gramo (g)"},
    {"category": "peso", "code": "mg", "name": "miligramo (mg)"},
    {"category": "peso", "code": "t", "name": "tonelada métrica (t)"},
    {"category": "peso", "code": "lb", "name": "libra (lb)"},
    {"category": "peso", "code": "oz", "name": "onza (oz)"},
    {"category": "peso", "code": "qq", "name": "quintal (qq)"},

    # Tiempo & Duración
    {"category": "tiempo", "code": "s", "name": "segundo (s)"},
    {"category": "tiempo", "code": "min", "name": "minuto (min)"},
    {"category": "tiempo", "code": "h", "name": "hora (h)"},
    {"category": "tiempo", "code": "d", "name": "día (d)"},
    {"category": "tiempo", "code": "sem", "name": "semana (sem)"},
    {"category": "tiempo", "code": "mes", "name": "mes (mes)"},
    {"category": "tiempo", "code": "año", "name": "año (año)"},

    # Servicios & Tecnología
    {"category": "servicios", "code": "srv", "name": "servicio (srv)"},
    {"category": "servicios", "code": "glb", "name": "global (glb)"},
    {"category": "servicios", "code": "lic", "name": "licencia (lic)"},
    {"category": "servicios", "code": "hh", "name": "hora hombre (hh)"},
    {"category": "servicios", "code": "jnl", "name": "jornal (jnl)"},
    {"category": "servicios", "code": "vst", "name": "visita técnica (vst)"},
    {"category": "servicios", "code": "proj", "name": "proyecto (proj)"},
    {"category": "servicios", "code": "MB", "name": "megabyte (MB)"},
    {"category": "servicios", "code": "GB", "name": "gigabyte (GB)"},
    {"category": "servicios", "code": "TB", "name": "terabyte (TB)"},

    # Energía & Electricidad
    {"category": "energia", "code": "W", "name": "vatio (W)"},
    {"category": "energia", "code": "kW", "name": "kilovatio (kW)"},
    {"category": "energia", "code": "kWh", "name": "kilovatio-hora (kWh)"},
    {"category": "energia", "code": "A", "name": "amperio (A)"},
    {"category": "energia", "code": "V", "name": "voltio (V)"}
]
