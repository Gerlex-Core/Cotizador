import os
import json
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/store",
    tags=["Store"]
)

STORE_REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "media", "release", "store_registry.json"))

def get_store_registry():
    if os.path.exists(STORE_REGISTRY_PATH):
        try:
            with open(STORE_REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"apps": []}

def save_store_registry(data):
    os.makedirs(os.path.dirname(STORE_REGISTRY_PATH), exist_ok=True)
    with open(STORE_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@router.post("/upload")
async def upload_app(
    version: str = Form(...),
    apk_file: UploadFile = File(...),
    icon_file: UploadFile = File(...)
):
    base_dir = os.path.dirname(STORE_REGISTRY_PATH)
    os.makedirs(base_dir, exist_ok=True)
    
    apk_path = os.path.join(base_dir, f"cotizador-app-{version}.apk")
    icon_path = os.path.join(base_dir, f"icon-{version}.png")
    
    # Save APK
    with open(apk_path, "wb") as f:
        f.write(await apk_file.read())
        
    # Save Icon
    with open(icon_path, "wb") as f:
        f.write(await icon_file.read())
        
    # Update registry
    registry = get_store_registry()
    
    app_entry = {
        "id": f"cotizador-{version}",
        "name": "Cotizador Pro",
        "version": version,
        "date": datetime.now().isoformat(),
        "apk_url": f"/release/cotizador-app-{version}.apk",
        "icon_url": f"/release/icon-{version}.png",
        "size_bytes": os.path.getsize(apk_path)
    }
    
    # Remove older entry of same version if exists
    registry["apps"] = [app for app in registry["apps"] if app.get("version") != version]
    registry["apps"].append(app_entry)
    
    # Sort by date descending (newest first)
    registry["apps"].sort(key=lambda x: x["date"], reverse=True)
    
    save_store_registry(registry)
    
    return {"message": "App publicada en la tienda exitosamente", "app": app_entry}

@router.get("/apps")
async def list_apps():
    return get_store_registry()
