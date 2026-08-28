from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid

from ..auth_utils import (
    verify_password, get_password_hash, create_access_token,
    verify_master_key, get_current_user
)
from ...db.database import get_connection, init_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterPayload(BaseModel):
    username: str
    password: str
    master_key: str
    role: str = "user"

class LoginPayload(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_user(payload: RegisterPayload) -> Dict[str, Any]:
    verify_master_key(payload.master_key)
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (payload.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(uuid.uuid4())
    hashed_pw = get_password_hash(payload.password)
    
    cursor.execute("""
        INSERT INTO users (id, username, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, (user_id, payload.username, hashed_pw, payload.role))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": f"User {payload.username} created successfully"}


@router.post("/login")
def login_user(payload: LoginPayload) -> Dict[str, Any]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (payload.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (current_user["id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return dict(user)
