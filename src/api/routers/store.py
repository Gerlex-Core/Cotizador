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
    app_description: str = Form(""),
    version_description: str = Form(""),
    version: str = Form(...),
    apk_file: UploadFile = File(...),
    app_icon_file: UploadFile = File(None),
    version_icon_file: UploadFile = File(None)
):
    app_dir = os.path.join(STORE_RELEASE_PATH, app_id)
    os.makedirs(app_dir, exist_ok=True)
    
    apk_path = os.path.join(app_dir, f"{app_id}-V{version}.apk")
    
    app_icon_filename = f"icon-{app_id}.png"
    app_icon_path = os.path.join(app_dir, app_icon_filename)
    
    version_icon_filename = f"icon-{app_id}-V{version}.png"
    version_icon_path = os.path.join(app_dir, version_icon_filename)
    
    # Save APK
    with open(apk_path, "wb") as f:
        f.write(await apk_file.read())
        
    # Save App Icon if provided
    if app_icon_file:
        with open(app_icon_path, "wb") as f:
            f.write(await app_icon_file.read())
            
    # Save Version Icon if provided
    if version_icon_file:
        with open(version_icon_path, "wb") as f:
            f.write(await version_icon_file.read())
            
    app_icon_url = f"/release/{app_id}/{app_icon_filename}" if os.path.exists(app_icon_path) else ""
    version_icon_url = f"/release/{app_id}/{version_icon_filename}" if os.path.exists(version_icon_path) else ""
    apk_url = f"/release/{app_id}/{app_id}-V{version}.apk"
    size_bytes = os.path.getsize(apk_path)
    
    # Save to SQLite
    save_store_app(app_id, app_name, app_description, app_icon_url)
    save_store_app_version(app_id, version, apk_url, size_bytes, version_description, version_icon_url)
    
    return {"message": f"App {app_name} V{version} publicada exitosamente"}

@router.get("/apps")
async def list_apps():
    apps = get_store_apps_with_versions()
    return {"apps": list(apps.values())}
