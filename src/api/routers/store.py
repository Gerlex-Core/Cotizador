import os
import shutil
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Header
from typing import Optional
from src.db.database import save_store_app, save_store_app_version, get_store_apps_with_versions, toggle_store_app_like, record_store_app_download, get_all_store_categories, get_or_create_store_category
from src.api.auth_utils import get_current_admin

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
    category: str = Form("General"),
    developer: str = Form(""),
    release_date: str = Form(""),
    website: str = Form(""),
    tags: str = Form(""),
    content_rating: str = Form("Todos"),
    version: str = Form(...),
    package_file: UploadFile = File(...),
    app_icon_file: UploadFile = File(None),
    version_icon_file: UploadFile = File(None),
    admin: dict = Depends(get_current_admin)
):
    app_dir = os.path.join(STORE_RELEASE_PATH, app_id)
    os.makedirs(app_dir, exist_ok=True)
    
    ext = os.path.splitext(package_file.filename)[1].lower()
    if ext not in [".apk", ".zip"]:
        ext = ".apk"
        
    package_filename = f"{app_id}-V{version}{ext}"
    package_path = os.path.join(app_dir, package_filename)
    
    app_icon_filename = f"icon-{app_id}.png"
    app_icon_path = os.path.join(app_dir, app_icon_filename)
    
    version_icon_filename = f"icon-{app_id}-V{version}.png"
    version_icon_path = os.path.join(app_dir, version_icon_filename)
    
    # Save Package
    with open(package_path, "wb") as f:
        f.write(await package_file.read())
        
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
    package_url = f"/release/{app_id}/{package_filename}"
    size_bytes = os.path.getsize(package_path)
    
    # Save to SQLite
    cat_id = get_or_create_store_category(category)
    save_store_app(app_id, app_name, app_description, app_icon_url, cat_id, developer, release_date, website, tags, content_rating)
    save_store_app_version(app_id, version, package_url, size_bytes, version_description, version_icon_url)
    
    return {"message": f"App {app_name} V{version} publicada exitosamente"}

@router.get("/categories")
async def list_categories():
    return {"categories": get_all_store_categories()}

@router.get("/apps")
async def list_apps(x_device_id: Optional[str] = Header(None)):
    apps = get_store_apps_with_versions(x_device_id)
    return {"apps": list(apps.values())}

@router.post("/{app_id}/like")
async def like_app(app_id: str, x_device_id: Optional[str] = Header(None)):
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing X-Device-ID header")
    action = toggle_store_app_like(app_id, x_device_id)
    return {"status": "success", "message": f"App {action}", "action": action}

@router.post("/{app_id}/download")
async def download_app(app_id: str, x_device_id: Optional[str] = Header(None)):
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing X-Device-ID header")
    success = record_store_app_download(app_id, x_device_id)
    return {"status": "success", "message": "Download tracked" if success else "Download already tracked for this device", "tracked": success}
