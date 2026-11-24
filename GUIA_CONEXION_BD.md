# Conexión segura a PostgreSQL — Vigía SOS

Esta guía explica cómo conectarte a la base **sin borrar ni dañar datos**.

---

## 1. Datos de conexión

La configuración **no se escribe a mano en el código**: se lee desde `.env`.

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `5432` |
| Base de datos | `vigia_sos` |
| Usuario | `postgres` |
| Contraseña | la que está en `DB_PASSWORD` de `.env` |
| SSL | `prefer` |

Archivos related:

- `.env` — valores reales locales.
- `.env.example` — plantilla sin secretos.
- `db_manager.py` — único punto de conexión (`DB_CONFIG` y `get_connection()`).
- `api_server.py` — expone `/api/status`, `/api/login`, `/api/register`, `/api/sos`.

---

## 2. Forma segura desde la app (recomendada)

No necesitas hacer nada especial: la app Kivy y la API ya se conectan solas.

```powershell
# API (puerto 5000)
.\run_api.bat

# App móvil KivyMD
.\run_mobile.bat
```

Al arrancar verás un mensaje como:

```text
Conexion a PostgreSQL 'vigia_sos' exitosa.
```

Eso confirma que está usando la BD correcta. **No ejecutes el reset** para conectar.

---

## 3. Forma segura desde Python

Usa siempre `db_manager`, nunca `psycopg2.connect()` con credenciales copiadas:

```powershell
.\.venv\Scripts\python.exe -c "import db_manager; print(db_manager.test_db_connection())"
```

Para una consulta de solo lectura:

```python
import db_manager

conn = db_manager.get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users;")
        print("Usuarios:", cur.fetchone()[0])
finally:
    conn.close()
```

Si necesitas asegurarte de que las tablas existen sin borrar nada:

```powershell
.\.venv\Scripts\python.exe -c "import db_manager; print(db_manager.ensure_schema())"
```

`ensure_schema()` ejecuta el DDL con `CREATE TABLE IF NOT EXISTS` y `CREATE TYPE ... EXCEPTION WHEN duplicate_object`: **crea lo que falta y respeta lo que ya existe**.

---

## 4. Conexión visual (pgAdmin 4 / DBeaver)

En tu equipo no encontré pgAdmin ni DBeaver en el PATH, así que te dejé abierto el proyecto en **Visual Studio Code** con esta guía y los archivos de conexión.

Si instalas pgAdmin 4 o DBeaver, crea una conexión con:

```text
Host:     localhost
Puerto:   5432
BD:       vigia_sos
Usuario:  postgres
Password: <DB_PASSWORD de .env>
SSL:      Prefer / Disable
```

Consultas seguras para verificar sin modificar nada:

```sql
SELECT current_database(), current_user, version();

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT COUNT(*) AS usuarios FROM users;
SELECT COUNT(*) AS alertas_sos FROM sos_alerts;
```

---

## 5. Backup antes de cualquier cambio importante

Si tienes las herramientas de PostgreSQL instaladas:

```powershell
pg_dump -h localhost -p 5432 -U postgres -Fc -d vigia_sos -f backup_vigia_sos.backup
```

Restauración (solo si realmente la necesitas):

```powershell
pg_restore -h localhost -p 5432 -U postgres -d vigia_sos backup_vigia_sos.backup
```

---

## 6. Qué NO hacer

- No ejecutes `python database/reset_database.py`: **borra y recrea** la base.
- No ejecutes `database/vigia_seeds.sql`: inserta datos de prueba.
- No cambies `DB_NAME` en `.env` a una base que no exista.
- No uses `DROP TABLE`, `TRUNCATE` ni `DELETE` desde el cliente visual.
- No edites credenciales directamente en `db_manager.py`; usa `.env`.

---

## 7. Estado actual de la BD

Tras la última verificación:

```text
13 tablas, todas vacías
users = 0
cameras = 0
zones = 0
incidents = 0
sos_alerts = 0
```

La tabla `sos_alerts` registra cada pulsación del botón SOS aunque la BD esté recién creada y no tenga cámaras ni categorías.
