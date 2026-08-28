"""
Catalog API Router - Provides versatile product & combo catalog for fast quotation building.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

class CatalogItem(BaseModel):
    id: str = ""
    category: str = "General"
    description: str = ""
    brand: str = ""
    sku: str = ""
    unit: str = "unidad (u)"
    price: float = 0.0
    warranty: str = "1 Año"
    image_path: str = ""

class ComboItem(BaseModel):
    id: str = ""
    name: str = ""
    category: str = "General"
    description: str = ""
    products: List[Dict[str, Any]] = Field(default_factory=list)

# In-memory versatile catalog store with default presets
DEFAULT_CATALOG_ITEMS: List[Dict[str, Any]] = [
    # CCTV & Videovigilancia
    {"id": "cctv-01", "category": "CCTV", "description": "Cámara Domo IP 4MP IR 30m PoE Exterior", "brand": "Dahua", "sku": "IPC-HDBW2431E", "unit": "unidad (u)", "price": 380.0, "warranty": "2 Años"},
    {"id": "cctv-02", "category": "CCTV", "description": "Cámara Bullet IP 4MP IR 50m Lente Varifocal", "brand": "Hikvision", "sku": "DS-2CD2643G0-IZS", "unit": "unidad (u)", "price": 620.0, "warranty": "2 Años"},
    {"id": "cctv-03", "category": "CCTV", "description": "NVR 8 Canales 4K PoE 80Mbps H.265+", "brand": "Dahua", "sku": "NVR4108HS-8P-4KS2", "unit": "unidad (u)", "price": 950.0, "warranty": "2 Años"},
    {"id": "cctv-04", "category": "CCTV", "description": "Disco Duro 2TB Surveillance Purple / SkyHawk", "brand": "Western Digital", "sku": "WD20PURZ", "unit": "unidad (u)", "price": 520.0, "warranty": "3 Años"},
    {"id": "cctv-05", "category": "CCTV", "description": "Caja de Conexión / Registro Estanca 100x100mm", "brand": "Generico", "sku": "CJ-EST-100", "unit": "unidad (u)", "price": 18.0, "warranty": "1 Año"},

    # Redes & Fibra Óptica
    {"id": "net-01", "category": "Redes", "description": "Bobina Cable UTP Cat6 100% Cobre 305m Exterior", "brand": "Dixon", "sku": "UTP-CAT6-EXT", "unit": "caja (caja)", "price": 880.0, "warranty": "5 Años"},
    {"id": "net-02", "category": "Redes", "description": "Switch PoE 16 Puertos Gigas + 2 SFP Unmanaged", "brand": "TP-Link", "sku": "TL-SG1016PE", "unit": "unidad (u)", "price": 1150.0, "warranty": "2 Años"},
    {"id": "net-03", "category": "Redes", "description": "Access Point Wi-Fi 6 Dual Band Gigabit Mesh", "brand": "Ubiquiti", "sku": "U6-PLUS", "unit": "unidad (u)", "price": 920.0, "warranty": "1 Año"},
    {"id": "net-04", "category": "Redes", "description": "Patch Panel Cat6 24 Puertos 1U Rack 19\"", "brand": "Panduit", "sku": "CPP24WBL", "unit": "unidad (u)", "price": 240.0, "warranty": "2 Años"},
    {"id": "net-05", "category": "Redes", "description": "Punto de Red UTP Cat6 (Jacks, Roseta, Latiguillo, Certificación)", "brand": "Varios", "sku": "PTR-CAT6", "unit": "unidad (u)", "price": 65.0, "warranty": "1 Año"},

    # Racks & Energía
    {"id": "pwr-01", "category": "Energía", "description": "Gabinete Rack de Pared 9U 19\" con Puerta de Vidrio", "brand": "Quest", "sku": "RK-PAR-9U", "unit": "unidad (u)", "price": 450.0, "warranty": "2 Años"},
    {"id": "pwr-02", "category": "Energía", "description": "UPS Online 1000VA / 900W Doble Conversión Torre/Rack", "brand": "APC", "sku": "SRV1KI", "unit": "unidad (u)", "price": 1850.0, "warranty": "2 Años"},
    {"id": "pwr-03", "category": "Energía", "description": "PDU Organizador de Energía 8 Tomas 10A con Switch Rack", "brand": "Tripp Lite", "sku": "PDU1215", "unit": "unidad (u)", "price": 180.0, "warranty": "1 Año"},

    # Control de Acceso & Alarmas
    {"id": "acc-01", "category": "Seguridad", "description": "Terminal Biométrico Control de Asistencia / Acceso Huella/Rostro", "brand": "ZKTeco", "sku": "MB20-VL", "unit": "unidad (u)", "price": 720.0, "warranty": "1 Año"},
    {"id": "acc-02", "category": "Seguridad", "description": "Chapa Electromagnética 600lbs con Soporte ZL", "brand": "Yli", "sku": "YM-280LED", "unit": "unidad (u)", "price": 280.0, "warranty": "1 Año"},
    {"id": "acc-03", "category": "Seguridad", "description": "Kit Alarma Inalámbrica Inteligente Wi-Fi / 4G con Sirena y Sensores", "brand": "Ajax", "sku": "HUB2-KIT", "unit": "unidad (u)", "price": 1450.0, "warranty": "2 Años"},

    # Domótica & Servicios
    {"id": "dom-01", "category": "Domótica", "description": "Interruptor Inteligente Wi-Fi Touch 3 Canales", "brand": "Sonoff", "sku": "TX-T3-3C", "unit": "unidad (u)", "price": 130.0, "warranty": "1 Año"},
    {"id": "srv-01", "category": "Servicios", "description": "Servicio Técnico Mano de Obra Instalación y Cableado por Punto", "brand": "Servicio", "sku": "MO-INST-PT", "unit": "unidad (u)", "price": 50.0, "warranty": "6 Meses"},
    {"id": "srv-02", "category": "Servicios", "description": "Mantenimiento Preventivo General Sistemas de Seguridad y Red", "brand": "Servicio", "sku": "MANT-PREV", "unit": "Mantenimiento", "price": 350.0, "warranty": "N/A"},
]

DEFAULT_COMBOS: List[Dict[str, Any]] = [
    {
        "id": "combo-cctv-4",
        "name": "Kit CCTV 4 Cámaras IP 4MP Full HD",
        "category": "CCTV",
        "description": "Sistema completo de videovigilancia IP con NVR, disco duro 2TB y accesorios estancos.",
        "products": [
            {"description": "NVR 8 Canales 4K PoE 80Mbps H.265+", "quantity": 1, "unit": "unidad (u)", "price": 950.0, "brand": "Dahua", "sku": "NVR4108HS-8P-4KS2"},
            {"description": "Cámara Domo IP 4MP IR 30m PoE Exterior", "quantity": 4, "unit": "unidad (u)", "price": 380.0, "brand": "Dahua", "sku": "IPC-HDBW2431E"},
            {"description": "Disco Duro 2TB Surveillance Purple", "quantity": 1, "unit": "unidad (u)", "price": 520.0, "brand": "Western Digital", "sku": "WD20PURZ"},
            {"description": "Caja de Conexión / Registro Estanca 100x100mm", "quantity": 4, "unit": "unidad (u)", "price": 18.0, "brand": "Generico", "sku": "CJ-EST-100"},
            {"description": "Servicio Técnico Mano de Obra Instalación y Cableado por Punto", "quantity": 4, "unit": "unidad (u)", "price": 50.0, "brand": "Servicio", "sku": "MO-INST-PT"}
        ]
    },
    {
        "id": "combo-red-pyme",
        "name": "Combo Red PYME 8 Puntos UTP Cat6 + Switch PoE",
        "category": "Redes",
        "description": "Cableado estructurado de red completo con gabinete de pared, switch gigabit y certificación.",
        "products": [
            {"description": "Switch PoE 16 Puertos Gigas + 2 SFP Unmanaged", "quantity": 1, "unit": "unidad (u)", "price": 1150.0, "brand": "TP-Link", "sku": "TL-SG1016PE"},
            {"description": "Gabinete Rack de Pared 9U 19\" con Puerta de Vidrio", "quantity": 1, "unit": "unidad (u)", "price": 450.0, "brand": "Quest", "sku": "RK-PAR-9U"},
            {"description": "Patch Panel Cat6 24 Puertos 1U Rack 19\"", "quantity": 1, "unit": "unidad (u)", "price": 240.0, "brand": "Panduit", "sku": "CPP24WBL"},
            {"description": "Punto de Red UTP Cat6 (Jacks, Roseta, Latiguillo, Certificación)", "quantity": 8, "unit": "unidad (u)", "price": 65.0, "brand": "Varios", "sku": "PTR-CAT6"}
        ]
    },
    {
        "id": "combo-acceso-biometrico",
        "name": "Combo Control de Acceso Biométrico + Chapa Magnética",
        "category": "Seguridad",
        "description": "Kit de control de acceso para puerta principal con lector biométrico, chapa electromagnética y botón de salida.",
        "products": [
            {"description": "Terminal Biométrico Control de Asistencia / Acceso Huella/Rostro", "quantity": 1, "unit": "unidad (u)", "price": 720.0, "brand": "ZKTeco", "sku": "MB20-VL"},
            {"description": "Chapa Electromagnética 600lbs con Soporte ZL", "quantity": 1, "unit": "unidad (u)", "price": 280.0, "brand": "Yli", "sku": "YM-280LED"},
            {"description": "Fuente de Poder 12V 5A con Respaldo de Batería", "quantity": 1, "unit": "unidad (u)", "price": 210.0, "brand": "Seco-Larm", "sku": "PS-12V5A"},
            {"description": "Servicio Técnico Mano de Obra Instalación y Cableado por Punto", "quantity": 1, "unit": "unidad (u)", "price": 150.0, "brand": "Servicio", "sku": "MO-INST-ACC"}
        ]
    }
]

_catalog_items = list(DEFAULT_CATALOG_ITEMS)
_catalog_combos = list(DEFAULT_COMBOS)

@router.get("/items")
def get_catalog_items() -> List[Dict[str, Any]]:
    """Retrieve all catalog items."""
    return _catalog_items

@router.post("/items")
def add_catalog_item(item: CatalogItem) -> Dict[str, Any]:
    """Add a new item to the catalog."""
    item_dict = item.dict()
    if not item_dict["id"]:
        item_dict["id"] = f"cust-{len(_catalog_items) + 1}"
    _catalog_items.append(item_dict)
    return {"status": "success", "item": item_dict}

@router.get("/combos")
def get_catalog_combos() -> List[Dict[str, Any]]:
    """Retrieve all preset combos/kits."""
    return _catalog_combos

@router.post("/combos")
def add_catalog_combo(combo: ComboItem) -> Dict[str, Any]:
    """Add a new combo kit to the catalog."""
    combo_dict = combo.dict()
    if not combo_dict["id"]:
        combo_dict["id"] = f"combo-cust-{len(_catalog_combos) + 1}"
    _catalog_combos.append(combo_dict)
    return {"status": "success", "combo": combo_dict}
