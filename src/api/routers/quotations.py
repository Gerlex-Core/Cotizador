"""
Quotations API Router - Handles calculations, PDF generation, .cotz files, and SQLite DB.
"""

import os
import tempfile
import re
import html
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ...export.pdf_generator import generar_pdf
from ...logic.company.company_logic import get_company_logic
from ...logic.config.config_manager import get_config
from ...logic.file.cotz_manager import get_cotz_manager
from ...logic.history.history_manager import HistoryManager
from ...db.database import save_quotation_to_db, list_quotations_from_db, get_quotation_from_db
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/quotations", tags=["Quotations"])
history_manager = HistoryManager()


def strip_html_tags(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    if "<" not in text and ">" not in text:
        return text.strip()
    text = re.sub(r'<head[^>]*>[\s\S]*?</head>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|li|tr)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join([line for line in lines if line])


class ProductItem(BaseModel):
    description: str = ""
    quantity: float = 1.0
    unit: str = "unidad (u)"
    price: float = 0.0
    brand: str = ""
    sku: str = ""
    discount_percent: float = 0.0
    item_warranty: str = ""
    image_path: str = ""


class QuotationPayload(BaseModel):
    document_type: str = "Cotización"
    quotation_number: str = "COT-001"
    company_name: str = ""
    date: str = ""
    purchase_date: str = ""
    validity: int = 15
    currency: str = "Bolivianos (Bs)"
    exchange_rate: float = 12.02
    show_exchange_rate: bool = True
    show_dual_currency: bool = True
    show_volatility_warning: bool = True
    client: Dict[str, str] = Field(default_factory=dict)
    products: List[ProductItem] = Field(default_factory=list)
    apply_discount: bool = False
    discount_percent: float = 0.0
    apply_iva: bool = True
    iva_percent: float = 13.0
    enable_shipping: bool = False
    shipping: float = 0.0
    shipping_type: str = "Envío Local"
    apply_payment: bool = False
    paid_amount: float = 0.0
    notes: str = ""
    bank_details: str = ""
    installation_terms: str = ""
    include_summary: bool = True
    include_details: bool = True
    include_bank_details: bool = True
    include_installation: bool = True
    include_warranty: bool = True
    include_signature: bool = True
    cover_page_enabled: bool = False
    cover_style: str = "corporate_modern"
    cover_subtitle: str = ""
    project_name: str = ""
    project_location: str = ""
    watermark_text: str = ""
    accent_color: str = "#10B981"
    cover_page_data: Dict[str, Any] = Field(default_factory=dict)
    terms_data: Dict[str, Any] = Field(default_factory=dict)
    work_calculator_data: Dict[str, Any] = Field(default_factory=dict)
    payment_milestones: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/calculate")
def calculate_quotation(payload: QuotationPayload, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Calculate subtotal, discount, IVA, shipping, total, paid, and saldo with item discounts and exchange rate."""
    subtotal = 0.0
    for p in payload.products:
        item_raw = p.quantity * p.price
        item_disc = item_raw * (p.discount_percent / 100.0) if p.discount_percent > 0 else 0.0
        subtotal += (item_raw - item_disc)
    
    discount_amount = 0.0
    if payload.apply_discount:
        discount_amount = subtotal * (payload.discount_percent / 100.0)
        
    after_discount = subtotal - discount_amount
    
    iva_amount = 0.0
    if payload.apply_iva:
        iva_amount = after_discount * (payload.iva_percent / 100.0)
        
    shipping_amount = payload.shipping if payload.enable_shipping else 0.0
    
    total = after_discount + iva_amount + shipping_amount
    
    paid_amount = payload.paid_amount if payload.apply_payment else 0.0
    saldo_amount = max(0.0, total - paid_amount) if payload.apply_payment else 0.0

    tc = payload.exchange_rate if payload.exchange_rate > 0 else 12.02
    is_bs = "Bolivianos" in payload.currency or "Bs" in payload.currency
    
    total_converted = total / tc if is_bs else total * tc
    currency_converted = "USD" if is_bs else "Bs"
    
    return {
        "subtotal": round(subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "iva_amount": round(iva_amount, 2),
        "shipping_amount": round(shipping_amount, 2),
        "total": round(total, 2),
        "paid_amount": round(paid_amount, 2),
        "saldo_amount": round(saldo_amount, 2),
        "exchange_rate": tc,
        "total_converted": round(total_converted, 2),
        "currency_converted": currency_converted
    }


def cleanup_file(path: str):
    """Background cleanup for temporary PDF file."""
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass


@router.post("/pdf")
def generate_quotation_pdf(payload: QuotationPayload, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Generate PDF document and return it for download/preview."""
    company_logic = get_company_logic()
    config = get_config()
    
    company_name = payload.company_name or "Empresa Demo"
    company_data = company_logic.get_company_dict(company_name)
    
    # Format products list: [[desc_with_brand_sku, qty, unit, price, amount]]
    products_formatted = []
    subtotal = 0.0
    for p in payload.products:
        item_raw = p.quantity * p.price
        item_disc = item_raw * (p.discount_percent / 100.0) if p.discount_percent > 0 else 0.0
        item_total = item_raw - item_disc
        subtotal += item_total
        
        desc = p.description
        extras = []
        if p.brand:
            extras.append(f"Marca: {p.brand}")
        if p.sku:
            extras.append(f"Código: {p.sku}")
        if p.item_warranty:
            extras.append(f"Garantía: {p.item_warranty}")
        if p.discount_percent > 0:
            extras.append(f"Desc: {p.discount_percent}%")
        if extras:
            desc += f"\n({', '.join(extras)})"
            
        products_formatted.append([
            desc,
            str(p.quantity),
            p.unit,
            f"{p.price:.2f}",
            f"{item_total:.2f}"
        ])
    
    discount_amount = subtotal * (payload.discount_percent / 100.0) if payload.apply_discount else 0.0
    after_discount = subtotal - discount_amount
    iva_amount = after_discount * (payload.iva_percent / 100.0) if payload.apply_iva else 0.0
    shipping_amount = payload.shipping if payload.enable_shipping else 0.0
    total = after_discount + iva_amount + shipping_amount
    
    paid_amount = payload.paid_amount if payload.apply_payment else 0.0
    saldo_amount = max(0.0, total - paid_amount) if payload.apply_payment else 0.0
    
    temp_dir = tempfile.gettempdir()
    safe_num = "".join([c for c in payload.quotation_number if c.isalnum() or c in ('-', '_')]) or "cotizacion"
    pdf_filename = f"{safe_num}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    client_dict = {
        "name": payload.client.get("name", ""),
        "contact": payload.client.get("contact", ""),
        "address": payload.client.get("address", "")
    }
    
    cover_data = None
    if payload.cover_page_enabled:
        cover_data = payload.cover_page_data.copy() if payload.cover_page_data else {}
        cover_data["enabled"] = True
        cover_data["cover_style"] = payload.cover_style
        cover_data["cover_subtitle"] = payload.cover_subtitle
        cover_data["project_name"] = payload.project_name
        cover_data["project_location"] = payload.project_location
        cover_data["watermark_text"] = payload.watermark_text
        cover_data["accent_color"] = payload.accent_color
        
    prepared_by = config.prepared_by if payload.include_signature else ""
    signature_image = None
    if payload.include_signature and config.signature_path and os.path.exists(config.signature_path):
        signature_image = config.signature_path

    # Save to SQLite DB automatically on PDF generation
    try:
        save_quotation_to_db(payload.dict(), current_user["id"])
    except Exception as db_err:
        print("[DB WARNING]", db_err)

    bank_details_clean = strip_html_tags(payload.bank_details) if payload.include_bank_details else ""
    installation_terms_clean = strip_html_tags(payload.installation_terms) if payload.include_installation else ""

    terms_data_clean = (payload.terms_data or {}).copy()
    if not payload.include_warranty:
        terms_data_clean.pop("warranty_covers", None)
        terms_data_clean.pop("warranty_excludes", None)
    else:
        if "warranty_covers" in terms_data_clean:
            terms_data_clean["warranty_covers"] = strip_html_tags(terms_data_clean["warranty_covers"])
        if "warranty_excludes" in terms_data_clean:
            terms_data_clean["warranty_excludes"] = strip_html_tags(terms_data_clean["warranty_excludes"])

    moneda_display = payload.currency

    try:
        generar_pdf(
            file_path=pdf_path,
            empresa=company_name,
            datos_empresa=company_data,
            productos=products_formatted,
            total=total,
            moneda=moneda_display,
            fecha=payload.date,
            purchase_date=payload.purchase_date,
            exchange_rate=payload.exchange_rate,
            show_exchange_rate=payload.show_exchange_rate,
            show_dual_currency=payload.show_dual_currency,
            show_volatility_warning=payload.show_volatility_warning,
            validez_dias=payload.validity,
            cliente=client_dict,
            numero_cotizacion=payload.quotation_number,
            document_type=payload.document_type,
            shipping=shipping_amount,
            cover_page_data=cover_data,
            estimated_days=int(payload.terms_data.get("estimated_days", 7)),
            shipping_type=payload.shipping_type if payload.enable_shipping else "Sin envío",
            payment_method=str(payload.terms_data.get("payment_method", "Contado")),
            bank_details=bank_details_clean,
            installation_terms=installation_terms_clean,
            payment_type=str(payload.terms_data.get("payment_type", "Efectivo")),
            apply_iva=payload.apply_iva,
            apply_payment=payload.apply_payment,
            paid_amount=paid_amount,
            saldo_amount=saldo_amount,
            include_details=payload.include_details,
            terms_data=terms_data_clean,
            prepared_by=prepared_by,
            signature_image=signature_image,
            mostrar_firma=payload.include_signature,
            mostrar_terminos=payload.include_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")
        
    background_tasks.add_task(cleanup_file, pdf_path)
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_filename
    )


@router.post("/save")
def save_quotation_file(payload: QuotationPayload, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Save quotation to SQLite DB and .cotz package file."""
    cotz_mgr = get_cotz_manager()
    temp_dir = tempfile.gettempdir()
    filename = f"{payload.quotation_number}.cotz"
    filepath = os.path.join(temp_dir, filename)
    
    data_dict = payload.dict()
    data_dict["total"] = sum(p.quantity * p.price for p in payload.products)
    
    # Save to SQLite DB
    save_quotation_to_db(data_dict, current_user["id"])

    if cotz_mgr.save_quotation(filepath, data_dict):
        history_manager.add_to_history(filepath, {
            "client": payload.client.get("name", ""),
            "total": str(data_dict["total"]),
            "doc_type": payload.document_type,
            "items_count": len(payload.products)
        })
        return {"status": "success", "file_path": filepath, "filename": filename}
    else:
        raise HTTPException(status_code=500, detail="Error guardando archivo .cotz")


@router.get("/db/list")
def get_db_quotations_list(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List stored quotations from SQLite database."""
    return list_quotations_from_db(current_user["id"])


@router.get("/db/load/{q_num}")
def load_quotation_by_number(q_num: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Load stored quotation payload from SQLite DB by number."""
    data = get_quotation_from_db(q_num, current_user["id"])
    if not data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada en la base de datos.")
    return data


@router.post("/upload")
async def upload_cotz_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and read a .cotz package file."""
    cotz_mgr = get_cotz_manager()
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    data = cotz_mgr.load_quotation(temp_path)
    if not data:
        raise HTTPException(status_code=400, detail="El archivo subido no es una cotización .cotz válida.")
        
    return data
