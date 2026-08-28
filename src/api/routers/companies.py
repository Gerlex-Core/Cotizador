"""
Companies API Router - Full CRUD endpoints with persistent SQLite DB and .emp files.
"""

import os
import shutil
import tempfile
import json
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ...logic.company.company_logic import get_company_logic, Company
from ...db.database import save_company_to_db, list_companies_from_db, delete_company_from_db
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/companies", tags=["Companies"])


class CompanyPayload(BaseModel):
    nombre: str
    nit: str = ""
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    ciudad: str = ""
    logo: str = ""
    firma: str = ""
    es_predeterminada: bool = False


@router.get("")
def list_companies(current_user: dict = Depends(get_current_user)) -> List[str]:
    """Get list of all company names."""
    company_logic = get_company_logic()
    names = company_logic.get_company_names()
    # Combine with DB
    db_comps = list_companies_from_db(current_user["id"])
    for c in db_comps:
        n = c.get("nombre") or c.get("name")
        if n and n not in names:
            names.append(n)
    return names


@router.get("/details")
def list_companies_details(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """Get list of all companies with complete details from both SQLite DB and .emp storage."""
    company_logic = get_company_logic()
    names = company_logic.get_company_names()
    
    comp_map = {}
    for name in names:
        cdict = company_logic.get_company_dict(name)
        if cdict:
            cdict["nombre"] = cdict.get("name", name)
            comp_map[cdict["nombre"]] = cdict
            
    # Merge with SQLite DB records
    db_comps = list_companies_from_db(current_user["id"])
    for c in db_comps:
        n = c.get("nombre") or c.get("name")
        if n and n not in comp_map:
            c["nombre"] = n
            comp_map[n] = c

    return list(comp_map.values())


@router.get("/{name}")
def get_company_detail(name: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get specific company configuration dictionary."""
    company_logic = get_company_logic()
    company_dict = company_logic.get_company_dict(name)
    if not company_dict:
        # Fallback to SQLite DB
        db_comps = list_companies_from_db(current_user["id"])
        for c in db_comps:
            if c.get("nombre") == name or c.get("name") == name:
                return c
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    company_dict["nombre"] = company_dict.get("name", name)
    return company_dict


@router.post("")
def save_company(company: CompanyPayload, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Save or update a company profile in both .emp and SQLite DB."""
    company_logic = get_company_logic()
    comp_dict = company.dict()
    
    comp_obj = Company(
        name=company.nombre,
        direccion=company.direccion,
        telefono=company.telefono,
        correo=company.correo,
        nit=company.nit
    )
    
    # Save into .emp file
    company_logic.save_company(comp_obj)
    
    # Save into SQLite DB persistently
    save_company_to_db(comp_dict, current_user["id"])
    
    return {"status": "success", "message": f"Empresa '{company.nombre}' guardada en SQLite y archivo .emp correctamente."}


@router.post("/upload")
async def upload_company_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Upload and import an existing company file (.emp or .json)."""
    company_logic = get_company_logic()
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, file.filename)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
        
    if file.filename.endswith(".emp"):
        dest = os.path.join(company_logic.get_companies_directory(), file.filename)
        shutil.copyfile(filepath, dest)
        company_logic._load_all_companies()
        
        comp_name = file.filename.replace(".emp", "")
        cdict = company_logic.get_company_dict(comp_name) or {"nombre": comp_name}
        save_company_to_db(cdict, current_user["id"])
        
        return {"status": "success", "message": f"Empresa importada desde {file.filename}"}
    elif file.filename.endswith(".json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                company = Company(
                    name=data.get("name") or data.get("nombre") or "Empresa Importada",
                    direccion=data.get("direccion", ""),
                    telefono=data.get("telefono", ""),
                    correo=data.get("correo", ""),
                    nit=data.get("nit", "")
                )
                company_logic.save_company(company)
                save_company_to_db(data, current_user["id"])
                return {"status": "success", "message": f"Empresa '{company.name}' importada desde JSON."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error leyendo JSON: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Debe ser .emp o .json")


@router.get("/{name}/download")
def download_company_file(name: str, current_user: dict = Depends(get_current_user)):
    """Download company profile as .emp file."""
    company_logic = get_company_logic()
    filepath = company_logic._get_emp_path(name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo .emp no encontrado.")
    return FileResponse(filepath, media_type="application/zip", filename=os.path.basename(filepath))


@router.delete("/{name}")
def delete_company(name: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Delete a company profile from both .emp files and SQLite DB."""
    company_logic = get_company_logic()
    company_logic.delete_company(name)
    delete_company_from_db(name, current_user["id"])
    return {"status": "success", "message": f"Empresa '{name}' eliminada de la base de datos y archivos."}
