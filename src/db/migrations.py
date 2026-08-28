"""
Database Migrations and Seeders Engine.
Manages database schema versions and executes data seeders.
"""

import sqlite3
from typing import Dict, Any, List
from .seeders import SEED_UNITS


def run_migrations(conn: sqlite3.Connection):
    """Run all schema migrations and initial seeders."""
    cursor = conn.cursor()

    # Schema Version table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check applied migrations
    cursor.execute("SELECT MAX(version) FROM schema_migrations;")
    row = cursor.fetchone()
    current_version = row[0] if row and row[0] is not None else 0

    # Migration 1: Base Tables (quotations, companies, settings)
    if current_version < 1:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_number TEXT UNIQUE NOT NULL,
            document_type TEXT DEFAULT 'Cotizacion',
            date TEXT,
            validity INTEGER DEFAULT 15,
            company_name TEXT,
            client_name TEXT,
            client_contact TEXT,
            client_address TEXT,
            subtotal REAL DEFAULT 0.0,
            discount_amount REAL DEFAULT 0.0,
            iva_amount REAL DEFAULT 0.0,
            shipping_amount REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            paid_amount REAL DEFAULT 0.0,
            saldo_amount REAL DEFAULT 0.0,
            terms_data_json TEXT,
            products_json TEXT,
            full_payload_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            nit TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            city TEXT,
            logo_path TEXT,
            signature_path TEXT,
            is_default INTEGER DEFAULT 0,
            full_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (1);")
        conn.commit()

    # Migration 2: Units Table & Seeders
    if current_version < 2:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT UNIQUE NOT NULL,
            is_custom INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        for u in SEED_UNITS:
            cursor.execute("""
            INSERT INTO units (category, code, name, is_custom)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(name) DO UPDATE SET category=excluded.category, code=excluded.code;
            """, (u["category"], u["code"], u["name"]))

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (2);")
        conn.commit()

    # Migration 3: Ensure companies columns (full_json, created_at)
    if current_version < 3:
        cursor.execute("PRAGMA table_info(companies);")
        cols = [r[1] for r in cursor.fetchall()]
        if "full_json" not in cols:
            try:
                cursor.execute("ALTER TABLE companies ADD COLUMN full_json TEXT;")
            except Exception:
                pass
        if "created_at" not in cols:
            try:
                cursor.execute("ALTER TABLE companies ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            except Exception:
                pass

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (3);")
        conn.commit()

    # Migration 4: App Store Tables
    if current_version < 4:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_apps (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_app_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT NOT NULL,
            version TEXT NOT NULL,
            apk_url TEXT NOT NULL,
            size_bytes INTEGER DEFAULT 0,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(app_id) REFERENCES store_apps(id) ON DELETE CASCADE,
            UNIQUE(app_id, version)
        );
        """)
        
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (4);")
        conn.commit()

    conn.commit()
