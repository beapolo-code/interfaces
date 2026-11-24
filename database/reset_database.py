"""
=============================================================================
RECREACIÓN LIMPIA DE LA BASE DE DATOS - VIGÍA / SEGURIDAD SOS
=============================================================================
Borra (si existe) la base configurada en .env, la vuelve a crear con codificación
UTF-8 y aplica unicamente el DDL de database/vigia_schema.sql.

NO aplica vigia_seeds.sql: la base queda sin datos de prueba ni registros basura.
Uso:
    python database/reset_database.py
"""

import os
import re
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import db_manager  # noqa: E402  (import después de ajustar sys.path)

MAINTENANCE_DB = 'postgres'


def _admin_config():
    config = dict(db_manager.DB_CONFIG)
    config['dbname'] = os.getenv('MAINTENANCE_DB', MAINTENANCE_DB)
    return config


def reset() -> str:
    dbname = db_manager.DB_CONFIG['dbname']
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', dbname):
        raise ValueError(f"DB_NAME no es un identificador PostgreSQL válido: {dbname!r}")

    admin = psycopg2.connect(**_admin_config())
    admin.autocommit = True
    try:
        with admin.cursor() as cur:
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid();",
                (dbname,)
            )
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(dbname)))
            cur.execute(
                sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(sql.Identifier(dbname))
            )
        print(f"[OK] Base de datos '{dbname}' recreada desde cero.")
    finally:
        admin.close()

    db_manager.ensure_schema()
    print(f"[OK] Esquema aplicado: {db_manager.get_schema_path().name}")
    print("[OK] Sin seeds: la base no contiene datos de prueba.")
    return dbname


if __name__ == '__main__':
    try:
        reset()
    except Exception as exc:
        print(f"[ERROR] No se pudo recrear la base de datos: {exc}")
        sys.exit(1)
