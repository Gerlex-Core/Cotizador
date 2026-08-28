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

    # Migration 5: Version-specific descriptions and icons
    if current_version < 5:
        cursor.execute("PRAGMA table_info(store_app_versions);")
        cols = [r[1] for r in cursor.fetchall()]
        if "description" not in cols:
            try:
                cursor.execute("ALTER TABLE store_app_versions ADD COLUMN description TEXT;")
            except Exception:
                pass
        if "icon_url" not in cols:
            try:
                cursor.execute("ALTER TABLE store_app_versions ADD COLUMN icon_url TEXT;")
            except Exception:
                pass

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (5);")
        conn.commit()

    # Migration 6: Users Auth & Store Metrics
    if current_version < 6:
        # Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Add user_id to quotations
        cursor.execute("PRAGMA table_info(quotations);")
        cols = [r[1] for r in cursor.fetchall()]
        if "user_id" not in cols:
            try: cursor.execute("ALTER TABLE quotations ADD COLUMN user_id TEXT;")
            except Exception: pass

        # Add user_id to companies
        cursor.execute("PRAGMA table_info(companies);")
        cols = [r[1] for r in cursor.fetchall()]
        if "user_id" not in cols:
            try: cursor.execute("ALTER TABLE companies ADD COLUMN user_id TEXT;")
            except Exception: pass

        # Add metrics to store_apps
        cursor.execute("PRAGMA table_info(store_apps);")
        cols = [r[1] for r in cursor.fetchall()]
        if "downloads" not in cols:
            try: cursor.execute("ALTER TABLE store_apps ADD COLUMN downloads INTEGER DEFAULT 0;")
            except Exception: pass
        if "likes" not in cols:
            try: cursor.execute("ALTER TABLE store_apps ADD COLUMN likes INTEGER DEFAULT 0;")
            except Exception: pass

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (6);")
        conn.commit()

    # Migration 7: Store App Unique Interactions (device_id)
    if current_version < 7:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_app_interactions (
            app_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (app_id, device_id, interaction_type),
            FOREIGN KEY(app_id) REFERENCES store_apps(id) ON DELETE CASCADE
        );
        """)
        
        # Populate likes and downloads from old raw integers into default device 'legacy_users' if they are > 0
        cursor.execute("SELECT id, downloads, likes FROM store_apps;")
        apps = cursor.fetchall()
        for app in apps:
            app_id, dl_count, like_count = app[0], app[1], app[2]
            for i in range(dl_count):
                cursor.execute("INSERT OR IGNORE INTO store_app_interactions (app_id, device_id, interaction_type) VALUES (?, ?, 'download');", (app_id, f"legacy_dl_{i}"))
            for i in range(like_count):
                cursor.execute("INSERT OR IGNORE INTO store_app_interactions (app_id, device_id, interaction_type) VALUES (?, ?, 'like');", (app_id, f"legacy_like_{i}"))
                
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (7);")
        conn.commit()

    # Migration 8: Store Categories
    if current_version < 8:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """)
        categories = [
            "General", "Juegos", "Entretenimiento", "Educación", "Finanzas", 
            "Productividad", "Social", "Salud y Bienestar", "Herramientas", 
            "Estilo de Vida", "Compras", "Deportes", "Noticias", "Fotografía", "Viajes",
            "Música y Audio", "Personalización", "Mapas y Navegación", "Negocios"
        ]
        for cat in categories:
            cursor.execute("INSERT OR IGNORE INTO store_categories (name) VALUES (?);", (cat,))
            
        cursor.execute("PRAGMA table_info(store_apps);")
        cols = [r[1] for r in cursor.fetchall()]
        if "category_id" not in cols:
            try: 
                cursor.execute("ALTER TABLE store_apps ADD COLUMN category_id INTEGER DEFAULT 1 REFERENCES store_categories(id);")
            except Exception: 
                pass

        cursor.execute("INSERT INTO schema_migrations (version) VALUES (8);")
        conn.commit()

    # Migration 9: Extra App Metadata
    if current_version < 9:
        cursor.execute("PRAGMA table_info(store_apps);")
        cols = [r[1] for r in cursor.fetchall()]
        
        new_columns = [
            ("developer", "TEXT"),
            ("release_date", "TEXT"),
            ("website", "TEXT"),
            ("tags", "TEXT"),
            ("content_rating", "TEXT")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in cols:
                try: 
                    cursor.execute(f"ALTER TABLE store_apps ADD COLUMN {col_name} {col_type};")
                except Exception: 
                    pass
                    
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (9);")
        conn.commit()

    conn.commit()
