"""
SQLite Database Storage Manager for Cotizador Pro.
Stores quotations, products, companies, system settings, and units in media/data/cotizador.db.
Runs migrations engine automatically.
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional
from .migrations import run_migrations

DB_DIR = os.path.join("media", "data")
DB_PATH = os.path.join(DB_DIR, "cotizador.db")


def get_connection():
    """Get connection to SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and run migrations."""
    conn = get_connection()
    try:
        run_migrations(conn)
    finally:
        conn.close()


def get_units_grouped_from_db() -> Dict[str, List[str]]:
    """Retrieve all measurement units grouped by category from SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, name FROM units ORDER BY category ASC, id ASC;")
    rows = cursor.fetchall()
    conn.close()

    grouped = {}
    for r in rows:
        cat = r["category"]
        name = r["name"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(name)
    return grouped


def list_all_units_from_db() -> List[Dict[str, Any]]:
    """List all units from DB as dictionary records."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, code, name, is_custom FROM units ORDER BY category ASC, id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_unit_to_db(category: str, code: str, name: str) -> bool:
    """Add custom unit to SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO units (category, code, name, is_custom)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(name) DO UPDATE SET category=excluded.category, code=excluded.code;
        """, (category.lower(), code, name))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def save_quotation_to_db(payload: Dict[str, Any]) -> int:
    """Save or update quotation record in SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    q_num = payload.get("quotation_number", "COT-001")
    doc_type = payload.get("document_type", "Cotizacion")
    date = payload.get("date", "")
    validity = payload.get("validity", 15)
    company = payload.get("company_name", "")
    client = payload.get("client", {})
    client_name = client.get("name", "")
    client_contact = client.get("contact", "")
    client_address = client.get("address", "")

    products = payload.get("products", [])
    subtotal = sum(p.get("quantity", 0) * p.get("price", 0) for p in products)
    
    disc_percent = payload.get("discount_percent", 0) if payload.get("apply_discount") else 0
    disc_amount = subtotal * (disc_percent / 100.0)
    after_disc = subtotal - disc_amount
    
    iva_percent = payload.get("iva_percent", 13) if payload.get("apply_iva") else 0
    iva_amount = after_disc * (iva_percent / 100.0)
    shipping_amount = payload.get("shipping", 0) if payload.get("enable_shipping") else 0
    total = after_disc + iva_amount + shipping_amount

    paid_amount = payload.get("paid_amount", 0) if payload.get("apply_payment") else 0
    saldo_amount = max(0.0, total - paid_amount) if payload.get("apply_payment") else 0

    cursor.execute("""
    INSERT INTO quotations (
        quotation_number, document_type, date, validity, company_name,
        client_name, client_contact, client_address, subtotal, discount_amount,
        iva_amount, shipping_amount, total, paid_amount, saldo_amount,
        terms_data_json, products_json, full_payload_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(quotation_number) DO UPDATE SET
        document_type=excluded.document_type,
        date=excluded.date,
        validity=excluded.validity,
        company_name=excluded.company_name,
        client_name=excluded.client_name,
        client_contact=excluded.client_contact,
        client_address=excluded.client_address,
        subtotal=excluded.subtotal,
        discount_amount=excluded.discount_amount,
        iva_amount=excluded.iva_amount,
        shipping_amount=excluded.shipping_amount,
        total=excluded.total,
        paid_amount=excluded.paid_amount,
        saldo_amount=excluded.saldo_amount,
        terms_data_json=excluded.terms_data_json,
        products_json=excluded.products_json,
        full_payload_json=excluded.full_payload_json;
    """, (
        q_num, doc_type, date, validity, company,
        client_name, client_contact, client_address, subtotal, disc_amount,
        iva_amount, shipping_amount, total, paid_amount, saldo_amount,
        json.dumps(payload.get("terms_data", {})),
        json.dumps(products),
        json.dumps(payload)
    ))

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def list_quotations_from_db() -> List[Dict[str, Any]]:
    """Get list of stored quotations."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quotation_number, document_type, date, client_name, company_name, total, paid_amount, saldo_amount, created_at FROM quotations ORDER BY created_at DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_quotation_from_db(q_num: str) -> Optional[Dict[str, Any]]:
    """Get full quotation payload by number."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotations WHERE quotation_number = ?;", (q_num,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    if row["full_payload_json"]:
        return json.loads(row["full_payload_json"])
        
    # Legacy fallback for older records
    return {
        "quotation_number": row["quotation_number"],
        "document_type": row["document_type"],
        "date": row["date"],
        "client": {
            "name": row["client_name"] or "",
            "contact": row["client_contact"] or "",
            "address": row["client_address"] or ""
        },
        "products": json.loads(row["products_json"]) if row.get("products_json") else [],
        "total": row["total"]
    }


def save_company_to_db(comp_dict: Dict[str, Any]):
    """Save or update company profile in SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    name = comp_dict.get("nombre") or comp_dict.get("name") or "Empresa"
    
    cursor.execute("""
    INSERT INTO companies (name, nit, address, phone, email, city, is_default, full_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
        nit=excluded.nit,
        address=excluded.address,
        phone=excluded.phone,
        email=excluded.email,
        city=excluded.city,
        is_default=excluded.is_default,
        full_json=excluded.full_json;
    """, (
        name,
        comp_dict.get("nit", ""),
        comp_dict.get("direccion", ""),
        comp_dict.get("telefono", ""),
        comp_dict.get("correo", ""),
        comp_dict.get("ciudad", ""),
        1 if comp_dict.get("es_predeterminada") else 0,
        json.dumps(comp_dict)
    ))
    conn.commit()
    conn.close()


def list_companies_from_db() -> List[Dict[str, Any]]:
    """List all companies stored in SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_json FROM companies ORDER BY is_default DESC, name ASC;")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        if r["full_json"]:
            try:
                result.append(json.loads(r["full_json"]))
            except Exception:
                pass
    return result


def delete_company_from_db(name: str):
    """Delete company from SQLite DB."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE name = ?;", (name,))
    conn.commit()
    conn.close()


def save_system_config_to_db(config_dict: Dict[str, Any]):
    """Store configuration values into SQLite settings table."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    for k, v in config_dict.items():
        cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP;
        """, (str(k), str(v)))
    conn.commit()
    conn.close()


def load_system_config_from_db() -> Dict[str, str]:
    """Retrieve all configuration settings stored in SQLite."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings;")
    rows = cursor.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def save_store_app(app_id: str, name: str, description: str, icon_url: str):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO store_apps (id, name, description, icon_url)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name=excluded.name,
        description=excluded.description,
        icon_url=excluded.icon_url,
        updated_at=CURRENT_TIMESTAMP;
    """, (app_id, name, description, icon_url))
    conn.commit()
    conn.close()

def save_store_app_version(app_id: str, version: str, apk_url: str, size_bytes: int):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO store_app_versions (app_id, version, apk_url, size_bytes)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(app_id, version) DO UPDATE SET
        apk_url=excluded.apk_url,
        size_bytes=excluded.size_bytes,
        published_at=CURRENT_TIMESTAMP;
    """, (app_id, version, apk_url, size_bytes))
    conn.commit()
    conn.close()

def get_store_apps_with_versions() -> Dict[str, Any]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM store_apps;")
    apps_rows = cursor.fetchall()
    
    result = {}
    for app_r in apps_rows:
        app_id = app_r["id"]
        cursor.execute("SELECT version, apk_url, size_bytes, published_at FROM store_app_versions WHERE app_id = ? ORDER BY published_at DESC;", (app_id,))
        versions_rows = cursor.fetchall()
        
        versions = [dict(v) for v in versions_rows]
        
        result[app_id] = {
            "id": app_id,
            "name": app_r["name"],
            "description": app_r["description"],
            "icon_url": app_r["icon_url"],
            "created_at": app_r["created_at"],
            "latest_version": versions[0]["version"] if versions else "1.0.0",
            "versions": versions
        }
        
    conn.close()
    return result
