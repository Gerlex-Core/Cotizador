import os
import shutil
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from src.db.database import save_store_app, save_store_app_version, get_store_apps_with_versions

router = APIRouter(
    prefix="/api/store",
    tags=["Store"]
)

STORE_RELEASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "media", "release"))

@router.post("/upload")
async def upload_app(
    app_id: str = Form(...),
    app_name: str = Form(...),
    description: str = Form(""),
    version: str = Form(...),
    apk_file: UploadFile = File(...),
    icon_file: UploadFile = File(None)
):
    app_dir = os.path.join(STORE_RELEASE_PATH, app_id)
    os.makedirs(app_dir, exist_ok=True)
    
    apk_path = os.path.join(app_dir, f"{app_id}-V{version}.apk")
    
    icon_filename = f"icon-{app_id}.png"
    icon_path = os.path.join(app_dir, icon_filename)
    
    # Save APK
    with open(apk_path, "wb") as f:
        f.write(await apk_file.read())
        
    # Save Icon if provided, else keep existing or use fallback later
    if icon_file:
        with open(icon_path, "wb") as f:
            f.write(await icon_file.read())
            
    icon_url = f"/release/{app_id}/{icon_filename}" if os.path.exists(icon_path) else ""
    apk_url = f"/release/{app_id}/{app_id}-V{version}.apk"
    size_bytes = os.path.getsize(apk_path)
    
    # Save to SQLite
    save_store_app(app_id, app_name, description, icon_url)
    save_store_app_version(app_id, version, apk_url, size_bytes)
    
    return {"message": f"App {app_name} V{version} publicada exitosamente"}

@router.get("/apps")
async def list_apps():
    apps = get_store_apps_with_versions()
    return {"apps": list(apps.values())}
