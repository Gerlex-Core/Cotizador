"""
PDF Editor API Router - Handles merging and manipulation of PDF pages.
"""

import os
import tempfile
import base64
from typing import List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import fitz  # PyMuPDF

router = APIRouter(prefix="/api/pdf", tags=["PDF Editor"])

class PdfPageConfig(BaseModel):
    doc_id: str
    page_index: int
    rotation: int

class MergePdfPayload(BaseModel):
    docs: Dict[str, str]  # doc_id -> base64 string
    pages: List[PdfPageConfig]

def cleanup_file(path: str):
    """Background cleanup for temporary PDF file."""
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass

@router.post("/merge")
def merge_pdfs(payload: MergePdfPayload, background_tasks: BackgroundTasks):
    if not payload.pages:
        raise HTTPException(status_code=400, detail="No hay páginas seleccionadas para procesar.")
    if not payload.docs:
        raise HTTPException(status_code=400, detail="No se enviaron documentos válidos.")

    temp_dir = tempfile.gettempdir()
    merged_pdf_path = os.path.join(temp_dir, f"merged_pages_{os.urandom(4).hex()}.pdf")

    opened_docs = {}
    merged_doc = None

    try:
        # Load all referenced source documents
        for doc_id, base64_str in payload.docs.items():
            try:
                pdf_bytes = base64.b64decode(base64_str)
                opened_docs[doc_id] = fitz.open(stream=pdf_bytes, filetype="pdf")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error al decodificar el documento {doc_id}.")

        merged_doc = fitz.open()

        # Insert pages in the requested order and apply rotation
        for idx, page_config in enumerate(payload.pages):
            if page_config.doc_id not in opened_docs:
                raise HTTPException(status_code=400, detail=f"El documento referenciado {page_config.doc_id} no existe.")
            
            src_doc = opened_docs[page_config.doc_id]
            
            if page_config.page_index < 0 or page_config.page_index >= len(src_doc):
                raise HTTPException(status_code=400, detail=f"Índice de página {page_config.page_index} fuera de rango para el documento {page_config.doc_id}.")
            
            # Insert just this page
            merged_doc.insert_pdf(src_doc, from_page=page_config.page_index, to_page=page_config.page_index)
            
            # Get the newly inserted page
            new_page = merged_doc[-1]
            
            # PyMuPDF 'rotation' gets absolute rotation.
            # We want to add the user's delta rotation (config.rotation)
            final_rotation = (new_page.rotation + page_config.rotation) % 360
            new_page.set_rotation(final_rotation)

        merged_doc.save(merged_pdf_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar el PDF: {str(e)}")
    finally:
        # Always close all documents
        if merged_doc:
            merged_doc.close()
        for doc in opened_docs.values():
            doc.close()

    background_tasks.add_task(cleanup_file, merged_pdf_path)

    return FileResponse(
        path=merged_pdf_path,
        media_type="application/pdf",
        filename="Documentos_Editados.pdf"
    )
