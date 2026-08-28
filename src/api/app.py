"""
FastAPI Main Application Initialization.
Mounts modular UI views in web/UI/views, components, layouts, themes, and js.
Includes Themes REST API Router.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .routers.quotations import router as quotations_router
from .routers.companies import router as companies_router
from .routers.config import router as config_router
from .routers.history import router as history_router
from .routers.themes import router as themes_router
from .routers.catalog import router as catalog_router
from .routers.digicorp import router as digicorp_router
from .routers.bcb import router as bcb_router
from .routers.pdf_editor import router as pdf_editor_router
from .routers.store import router as store_router

app = FastAPI(
    title="Cotizador Pro API",
    description="Mini Servidor de Cotizaciones Modular y Ligero",
    version="3.5.0"
)

# No-Cache Middleware for instant UI updates during development/runs
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# Enable CORS for local/network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(quotations_router)
app.include_router(companies_router)
app.include_router(config_router)
app.include_router(history_router)
app.include_router(themes_router)
app.include_router(catalog_router)
app.include_router(digicorp_router)
app.include_router(bcb_router)
app.include_router(pdf_editor_router)
app.include_router(store_router)

# --- STATIC FILES (REMOVED) ---
# Se elimina el montaje de web/UI y la renderizacion de HTML 
# a peticion del usuario para evitar duplicados con el frontend React/Tauri.

# Expose media/release for APK downloads
release_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "media", "release"))
os.makedirs(release_dir, exist_ok=True)
app.mount("/release", StaticFiles(directory=release_dir), name="release")
@app.get("/")
def read_root():
    """Servidor Backend de la API."""
    return {"message": "Cotizador Pro API Activa", "version": "3.5.0"}
