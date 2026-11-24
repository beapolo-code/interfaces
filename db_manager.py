"""
=============================================================================
GESTOR DE BASE DE DATOS POSTGRESQL - SISTEMA VIGÍA / SEGURIDAD SOS
=============================================================================
Maneja la conexión y operaciones de usuarios, autenticación y cámaras.

La configuración se lee desde .env (ver .env.example). Para recrear la base
de datos desde cero ejecuta: python database/reset_database.py
"""

import hashlib
import os
import traceback
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

try:  # python-dotenv es opcional en ejecuciones muy simples
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
if load_dotenv is not None:
    # Se cargan ambos archivos para que la copia móvil use la misma configuración.
    load_dotenv(BASE_DIR / '.env')
    load_dotenv(BASE_DIR.parent / '.env')

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'vigia_sos'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
}


def get_connection():
    """Obtiene una conexión activa a la base de datos PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def get_schema_path() -> Path:
    """Devuelve la ruta al DDL, tanto desde la raíz como desde mobile/."""
    candidates = (
        BASE_DIR / 'database' / 'vigia_schema.sql',
        BASE_DIR.parent / 'database' / 'vigia_schema.sql',
    )
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError('No se encontró database/vigia_schema.sql')


def ensure_schema():
    """Crea/actualiza las tablas de forma idempotente sin insertar datos de prueba."""
    schema_sql = get_schema_path().read_text(encoding='utf-8')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    return True


def hash_pin(pin: str) -> str:
    """Genera hash SHA-256 para la contraseña o PIN numérico."""
    return hashlib.sha256(pin.strip().encode('utf-8')).hexdigest()


def test_db_connection():
    """Verifica si la base de datos está accesible."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return True, f"Conexion a PostgreSQL '{DB_CONFIG['dbname']}' exitosa."
    except Exception as e:
        return False, f"Error al conectar a PostgreSQL: {e}"


def register_user(name: str, email: str, phone: str = None, password: str = None, pin: str = None):
    """
    Registra un nuevo usuario con campos separados de Correo y Contraseña.
    Soporta argumentos flexibles (name, email, phone, password).
    """
    name = (name or '').strip()
    email = (email or '').strip()
    phone = (phone or '').strip() or None
    pwd = (password or pin or '').strip()

    if not name:
        return False, "Por favor ingresa tu nombre completo.", None
    if not email:
        return False, "Por favor ingresa tu correo electrónico.", None
    if not pwd:
        return False, "Por favor ingresa una contraseña.", None

    # Normalizar email si el usuario ingresó solo teléfono en email
    if '@' not in email:
        if not phone:
            phone = email
        email = f"{phone}@vigia.local"

    email = email.lower()
    pwd_hashed = hash_pin(pwd)

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Comprobar si ya existe por email o teléfono
                cur.execute(
                    """
                    SELECT id FROM users
                    WHERE (LOWER(email) = LOWER(%s)) OR (phone IS NOT NULL AND phone = %s)
                    LIMIT 1;
                    """,
                    (email, phone if phone else '')
                )
                existing = cur.fetchone()
                if existing:
                    return False, "Ya existe una cuenta con este correo electrónico o teléfono.", None

                # Insertar usuario con rol 'viewer'
                cur.execute(
                    """
                    INSERT INTO users (name, email, phone, password_hash, role, is_active)
                    VALUES (%s, %s, %s, %s, 'viewer', TRUE)
                    RETURNING id, name, email, phone, role, is_active, created_at;
                    """,
                    (name, email, phone, pwd_hashed)
                )
                new_user = cur.fetchone()
                conn.commit()
                return True, f"¡Cuenta creada exitosamente para {name}!", dict(new_user)
    except Exception as e:
        return False, f"Error en base de datos al registrar: {e}", None


def login_user(email: str, password: str):
    """Valida credenciales con campos separados de Correo Electrónico y Contraseña."""
    email = (email or '').strip()
    pwd = (password or '').strip()

    if not email:
        return False, "Por favor ingresa tu correo electrónico.", None
    if not pwd:
        return False, "Por favor ingresa tu contraseña.", None

    pwd_hashed = hash_pin(pwd)

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, name, email, phone, password_hash, role, is_active, created_at
                    FROM users
                    WHERE (LOWER(email) = LOWER(%s))
                       OR (phone = %s)
                       OR (email = %s)
                    LIMIT 1;
                    """,
                    (email, email, f"{email}@vigia.local")
                )
                user = cur.fetchone()

                if not user:
                    return False, "Correo o usuario no encontrado. Crea una cuenta primero.", None
                if not user.get('is_active', True):
                    return False, "Tu cuenta se encuentra inactiva o suspendida.", None

                stored_hash = user.get('password_hash', '')
                # Verifica hash SHA-256 o texto plano por compatibilidad
                if stored_hash != pwd_hashed and stored_hash != pwd:
                    return False, "Contraseña incorrecta. Inténtalo de nuevo.", None

                return True, f"¡Bienvenido de nuevo, {user['name']}!", dict(user)
    except Exception as e:
        return False, f"Error de conexión a la base de datos: {e}", None


def get_cameras_list():
    """Obtiene el listado de cámaras activas desde la base de datos."""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT c.id, c.name, c.source_type, c.source, c.fps, c.status,
                           COALESCE(z.name, 'General') as zone_name
                    FROM cameras c
                    LEFT JOIN zones z ON c.zone_id = z.id
                    WHERE c.is_active = TRUE
                    ORDER BY c.id;
                    """
                )
                return cur.fetchall()
    except Exception:
        return []


def get_emergency_contacts():
    """Obtiene los contactos de emergencia activos desde la base de datos."""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, name, type::text AS contact_type, phone, email,
                           receives_email, is_active
                    FROM emergency_contacts
                    WHERE is_active = TRUE
                    ORDER BY id;
                    """
                )
                return [dict(row) for row in cur.fetchall()]
    except Exception:
        traceback.print_exc()
        return []


def add_emergency_contact(name: str, contact_type: str, phone: str,
                          email: str = None, receives_email: bool = False):
    """Guarda un nuevo contacto de emergencia y devuelve (éxito, mensaje)."""
    name = (name or '').strip()
    phone = (phone or '').strip()
    email = (email or '').strip() or None
    contact_type = (contact_type or 'other').strip().lower()

    if not name:
        return False, "Ingresa el nombre del contacto."
    if not phone:
        return False, "Ingresa el teléfono del contacto."

    valid_types = {'police', 'firefighter', 'medical', 'other'}
    if contact_type not in valid_types:
        contact_type = 'other'

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO emergency_contacts
                        (name, type, phone, email, receives_email, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                    RETURNING id;
                    """,
                    (name, contact_type, phone, email, bool(receives_email))
                )
                conn.commit()
        return True, "Contacto de emergencia guardado correctamente."
    except Exception as e:
        return False, f"No se pudo guardar el contacto: {e}"


def record_sos_alert(user_id: int = None, source: str = 'mobile'):
    """Registra una alerta SOS.

    Toda pulsación del botón SOS persiste en ``sos_alerts``. Si además ya
    existen una cámara y la categoría SOS_PANIC, se crea el incidente
    correspondiente para mantener la integración con el resto del esquema.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sos_alerts (user_id, source)
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (user_id or None, source or 'mobile')
                )
                alert_id = cur.fetchone()[0]

                cur.execute(
                    "SELECT id FROM incident_categories WHERE code = 'SOS_PANIC' LIMIT 1;"
                )
                cat = cur.fetchone()
                cat_id = cat[0] if cat else None

                cur.execute("SELECT id FROM cameras LIMIT 1;")
                cam = cur.fetchone()
                cam_id = cam[0] if cam else None

                if cam_id and cat_id:
                    cur.execute(
                        """
                        INSERT INTO incidents
                            (camera_id, category_id, confidence, alarm_active)
                        VALUES (%s, %s, 1.0, TRUE)
                        RETURNING id;
                        """,
                        (cam_id, cat_id)
                    )
                conn.commit()
                return alert_id is not None
    except Exception as e:
        print(f"[Error registrando SOS en BD]: {e}")
        return False
