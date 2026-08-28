from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from ..auth_utils import get_current_admin
from ...db.database import get_connection, init_db, update_store_app_details

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class StoreAppUpdate(BaseModel):
    name: str
    description: str

@router.get("/users")
def get_all_users(admin: dict = Depends(get_current_admin)) -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC;")
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]

@router.put("/store-apps/{app_id}")
def update_store_app(app_id: str, payload: StoreAppUpdate, admin: dict = Depends(get_current_admin)):
    success = update_store_app_details(app_id, payload.name, payload.description)
    if not success:
        raise HTTPException(status_code=404, detail="Store App not found")
    return {"status": "success", "message": "Store app updated correctly"}
