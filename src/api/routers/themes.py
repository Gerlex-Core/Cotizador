"""
Themes API Router - Serves and manages JSON themes dynamically.
"""

import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/themes", tags=["Themes"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
THEMES_DIR = os.path.join(BASE_DIR, "media", "themes")


class CustomThemePayload(BaseModel):
    name: str
    description: str = ""
    is_dark: bool = True
    colors: Dict[str, Any]
    shapes: Dict[str, Any] = {}
    typography: Dict[str, Any] = {}


def ensure_themes_dir():
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR, exist_ok=True)


@router.get("")
def list_available_themes() -> List[Dict[str, Any]]:
    """List all available JSON themes."""
    ensure_themes_dir()
    themes = []
    
    for filename in os.listdir(THEMES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(THEMES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    themes.append({
                        "id": filename.replace(".json", ""),
                        "filename": filename,
                        "name": data.get("name", filename),
                        "description": data.get("description", ""),
                        "is_dark": data.get("is_dark", True)
                    })
            except Exception:
                pass
                
    return themes


@router.get("/{theme_id}")
def get_theme_content(theme_id: str) -> Dict[str, Any]:
    """Get complete JSON content of a specific theme."""
    ensure_themes_dir()
    filename = f"{theme_id}.json" if not theme_id.endswith(".json") else theme_id
    filepath = os.path.join(THEMES_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Tema no encontrado")
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo archivo de tema: {str(e)}")


@router.post("")
def create_custom_theme(payload: CustomThemePayload) -> Dict[str, Any]:
    """Save or update a custom JSON theme."""
    ensure_themes_dir()
    safe_id = "".join([c for c in payload.name.lower().replace(" ", "_") if c.isalnum() or c == '_']) or "custom_theme"
    filepath = os.path.join(THEMES_DIR, f"{safe_id}.json")
    
    data = payload.dict()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return {"status": "success", "message": f"Tema '{payload.name}' guardado correctamente.", "theme_id": safe_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando tema: {str(e)}")
