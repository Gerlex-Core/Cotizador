"""
Config API Router - Manages system options, PDF margins, watermark settings, and units from SQLite DB.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...logic.config.config_manager import get_config
from ...db.database import save_system_config_to_db, load_system_config_from_db, get_units_grouped_from_db, add_unit_to_db

router = APIRouter(prefix="/api/config", tags=["Config"])


class ConfigPayload(BaseModel):
    idioma: str = "es"
    moneda: str = "Bolivianos (Bs)"
    tema: str = "Oscuro"
    fuente: str = "Arial"
    tamaño_fuente: int = 14
    validez_dias: int = 30
    mostrar_terminos: bool = True
    mostrar_firma: bool = True
    prepared_by: str = ""
    signature_path: str = ""
    margin_top: int = 40
    margin_bottom: int = 40
    margin_left: int = 40
    margin_right: int = 40
    watermark_enabled: bool = False
    watermark_text: str = ""
    watermark_opacity: int = 15
    watermark_image_path: str = ""


class NewUnitPayload(BaseModel):
    category: str
    code: str
    name: str


@router.get("")
def get_app_config() -> Dict[str, Any]:
    """Get all application settings and measurement units from SQLite DB."""
    config = get_config()
    db_settings = load_system_config_from_db()
    units_catalog = get_units_grouped_from_db()

    return {
        "config": {
            "idioma": config.idioma,
            "moneda": db_settings.get("moneda", config.moneda),
            "tema": config.tema,
            "fuente": db_settings.get("fuente", config.fuente),
            "tamaño_fuente": config.tamaño_fuente,
            "validez_dias": config.validez_dias,
            "mostrar_terminos": config.mostrar_terminos,
            "mostrar_firma": config.mostrar_firma,
            "prepared_by": db_settings.get("prepared_by", config.prepared_by),
            "signature_path": config.signature_path,
            "margin_top": config.pdf_margin_top,
            "margin_bottom": config.pdf_margin_bottom,
            "margin_left": config.pdf_margin_left,
            "margin_right": config.pdf_margin_right,
            "watermark_enabled": config.watermark_enabled,
            "watermark_text": config.watermark_text,
            "watermark_opacity": config.watermark_opacity,
            "watermark_image_path": config.watermark_image_path
        },
        "units": units_catalog
    }


@router.post("")
def update_app_config(payload: ConfigPayload) -> Dict[str, Any]:
    """Save application settings into settings.conf and SQLite DB."""
    config = get_config()

    config.idioma = payload.idioma
    config.moneda = payload.moneda
    config.tema = payload.tema
    config.fuente = payload.fuente
    config.tamaño_fuente = payload.tamaño_fuente
    config.validez_dias = payload.validez_dias
    config.mostrar_terminos = payload.mostrar_terminos
    config.mostrar_firma = payload.mostrar_firma

    config.prepared_by = payload.prepared_by
    config.signature_path = payload.signature_path

    config.pdf_margin_top = payload.margin_top
    config.pdf_margin_bottom = payload.margin_bottom
    config.pdf_margin_left = payload.margin_left
    config.pdf_margin_right = payload.margin_right

    config.watermark_enabled = payload.watermark_enabled
    config.watermark_text = payload.watermark_text
    config.watermark_opacity = payload.watermark_opacity
    config.watermark_image_path = payload.watermark_image_path

    config.save()
    save_system_config_to_db(payload.dict())

    return {"status": "success", "message": "Configuración guardada en SQLite y archivo .conf correctamente."}


@router.post("/units")
def create_custom_unit(payload: NewUnitPayload) -> Dict[str, Any]:
    """Create custom measurement unit in SQLite database."""
    if add_unit_to_db(payload.category, payload.code, payload.name):
        return {"status": "success", "message": f"Unidad '{payload.name}' agregada a la base de datos."}
    else:
        raise HTTPException(status_code=400, detail="No se pudo agregar la unidad a la base de datos.")
