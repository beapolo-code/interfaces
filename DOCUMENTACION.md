# 🛡️ DOCUMENTACIÓN INTEGRAL — SISTEMA VIGÍA / SEGURIDAD SOS

> Arquitectura unificada Móvil (KivyMD) y Web (HTML5/CSS3/JS) conectada a **PostgreSQL 18** bajo **Material Design 3** (tema oscuro).

---

## 1. 📐 Arquitectura General del Sistema

```text
[ Capa de Presentación ]
  ├── 📱 App Móvil KivyMD (main.py / mobile/main.py)
  ├── 💻 Panel Web Escritorio (web/index.html)
  └── 📱 Web Móvil Shell (index.html)
          │
          ▼
[ Capa de Backend & Lógica ]
  ├── ⚙️ db_manager.py (Conexión PostgreSQL, SHA-256 y SOS)
  └── 🚀 api_server.py (API REST en http://localhost:5000)
          │
          ▼
[ Capa de Persistencia ]
  └── 🐘 PostgreSQL 18 (BD: vigia_sos en localhost:5432)
```

La versión web usa CSS y JavaScript **incluidos en cada `index.html`**; `styles.css` y `app.js` se mantienen sincronizados como referencia/legado.

---

## 2. 🗄️ Base de Datos Limpia

* **Motor:** PostgreSQL 18
* **Base de datos:** `vigia_sos` (la documentación anterior usaba `Diseño de Interfaz`, que no existía)
* **Host / Puerto:** `localhost:5432`
* **Usuario:** `postgres`
* **Contraseña local:** `12345`, tomada del `.env.development` de otro proyecto existente en el equipo. La documentación anterior indicaba `1234`, que falla en la autenticación actual.
* **Configuración real:** `.env` (ignorado por Git). Plantilla: `.env.example`.

Variables:

```dotenv
APP_ENV=development
API_PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vigia_sos
DB_USER=postgres
DB_PASSWORD=12345
DB_SSLMODE=prefer
```

### Recreación desde cero

```powershell
python database/reset_database.py
```

El script:

1. Termina conexiones activas a `vigia_sos`.
2. Borra y vuelve a crear la BD con codificación UTF-8.
3. Aplica únicamente `database/vigia_schema.sql`.
4. **No aplica** `database/vigia_seeds.sql`.

Resultado verificado: 13 tablas (`cameras`, `emergency_contacts`, `evidence`, `incident_categories`, `incidents`, `notifications`, `protocols`, `sirens`, `sos_alerts`, `terms_acceptances`, `terms_and_conditions`, `users`, `zones`) y todas vacías.

> Como no hay seeds, no existe el usuario admin anterior (`admin@vigia.local`). Registra un usuario desde la interfaz o mediante `POST /api/register`.

---

## 3. 🔐 Autenticación con campos separados

### Iniciar Sesión (Login)
* **Campo 1:** Correo Electrónico
* **Campo 2:** Contraseña
* **Botón:** `INICIAR SESIÓN`

### Crear Cuenta (Registro)
* **Campo 1:** Nombre Completo
* **Campo 2:** Teléfono Móvil
* **Campo 3:** Correo Electrónico
* **Campo 4:** Contraseña de seguridad
* **Botón:** `CREAR MI CUENTA SOS`

`db_manager.py` usa `python-dotenv` para leer `.env` y aplica hash SHA-256 a la contraseña.

---

## 4. 🎨 Paleta Material Design 3

Tokens M3 oscuros aplicados en las 3 vistas web y en KivyMD:

| Token M3 | Valor | On-* | Valor |
|---|---|---|---|
| Primary | `#FFB4AB` | On Primary | `#690005` |
| Primary Container | `#93000A` | On Primary Container | `#FFDAD6` |
| Secondary | `#A7EEFF` | On Secondary | `#00363F` |
| Secondary Container | `#00505C` | On Secondary Container | `#CFF5FF` |
| Tertiary | `#AECBFF` | On Tertiary | `#002B56` |
| Tertiary Container | `#00427A` | On Tertiary Container | `#D7E3FF` |
| Background | `#0B1020` | On Background | `#E4E7F2` |
| Surface | `#121A2E` | On Surface | `#E4E7F2` |
| Surface Variant | `#1E2942` | On Surface Variant | `#B9C5E3` |
| Error | `#FFB4AB` | On Error | `#690005` |
| Error Container | `#93000A` | On Error Container | `#FFDAD6` |
| SOS | `#C11E38` | On SOS | `#FFFFFF` |

Contrastes comprobados: Primary/On Primary `7.72:1`, Secondary/On Secondary `10.2:1`, SOS/On SOS `5.98:1`, Background/On Background `15.34:1`.

Los alias antiguos (`--bg-main`, `--bg-input-nav`, `--bg-card`, `--border-input`, `--text-primary`, `--text-secondary`, `--accent-cyan`, `--btn-primary`, `--btn-primary-hover`, `--zone-alert`, `--sos-red`, `--action-blue`, `--glow-sos`) apuntan a los tokens M3. En KivyMD se exponen como propiedades `md3_*` y se conservan los alias usados por el KV.

---

## 5. 🚨 Botón de Alerta en Sidebar / Drawer y Móvil

### Escritorio (`web/index.html`)
* Botón dedicado `#nav-alert` con clase `.nav-link--alert` dentro de `<aside class="sidebar">`.
* `min-height: 48px`, `overflow: visible`, `z-index` explícito y focus ring M3.
* Se eliminó `.nav-link` del grupo con `overflow: hidden`.
* Acción: `onclick="triggerSidebarSOS()"` → `switchView('home')` + `fireSOS()`.
* El overlay usa `z-index: 300`, por encima del Sidebar (`z-index: 20`).

### Móvil web (`index.html`)
* El antiguo `<div class="nav-item">` de SOS se cambió a `<button type="button" class="nav-item nav-item--alert" id="nav-sos">`.
* Área táctil mínima `48x48px`, `overflow: visible`, `z-index` y focus ring.
* Acción: `onclick="triggerMobileSOS()"` → navega a `home-screen` + `fireSOS()`.
* El overlay (`z-index: 200`) se muestra por encima de la bottom-nav (`z-index: 100`).

### API y feedback
`fireSOS()` abre el overlay, muestra un toast y envía:

```http
POST http://localhost:5000/api/sos
Content-Type: application/json

{ "user_id": <id del usuario autenticado|null> }
```

`api_server.py` responde con `success`, `recorded` y un mensaje. Toda alerta se persiste en `sos_alerts` (tabla independiente de cámaras/categorías), por lo que `recorded` es `true` incluso en una BD recién creada. Si además existen cámara y categoría `SOS_PANIC`, se crea también el `incidents` asociado.

### KivyMD 2.0.0 (`main.py` y `mobile/main.py`)
* Widgets migrados: `MDButton` + `MDButtonText`, `MDNavigationBar` + `MDNavigationItem`, `MDNavigationDrawer`, `MDDivider`, `MDSnackbarText` y `MDTextField` con `MDTextFieldHintText`/`MDTextFieldLeadingIcon`.
* Se eliminaron las clases 1.x `MDFillRoundFlatButton`, `MDBottomNavigation`, `MDSeparator` y las tipografías `H5/H6/Caption`, sustituidas por estilos M3 (`Display`, `Headline`, `Title`, `Body`, `Label`).
* El drawer (`MDNavigationDrawer`) contiene un item **Alerta SOS** siempre visible, además del botón SOS de la cabecera, la pestaña `nav_sos` y la acción SOS de la `MDTopAppBar` de cámaras.
* `self.theme_cls.theme_style = "Dark"` y `self.theme_cls.primary_palette = "Pink"` fijan el esquema M3; los alias `app.*` son los mismos tokens de la web.

### KivyMD (`main.py` / `mobile/main.py`)
* Pestaña `nav_sos` con botón de `140dp` y `on_release: app.activate_sos_overlay()`.
* `activate_sos_overlay()` activa `sos_alert_active`, intenta registrar el SOS si hay usuario y muestra un snackbar.
* Overlay a pantalla completa con `opacity`, `size_hint` y `pos_hint` sincronizados con `sos_alert_active`.

---

## 6. 🎬 Animaciones y estados de interacción

Se conservan las microinteracciones existentes:

* **Reposo:** respiración suave del botón SOS y baliza de cámaras en vivo.
* **Hover / Focus:** elevación ligera y halo con `--md-sys-color-secondary`; focus rings de 3px.
* **Active:** compresión táctil y ripple material.
* **Acción:** anillo SVG progresivo de 3s, overlay con ondas de radar, toast y (en Kivy) snackbar.
* **Validación:** sacudida elástica del campo inválido.

---

## 7. 🚀 Scripts y comandos

| Archivo / comando | Uso |
|---|---|
| `python database/reset_database.py` | Recrea `vigia_sos` vacía, solo DDL |
| `python api_server.py` / `run_api.bat` | Inicia la API en `:5000` |
| `web/index.html` | Panel web de escritorio |
| `index.html` | Shell web móvil |
| `python main.py` / `run_mobile.bat` | App KivyMD |
| `python -m py_compile ...` | Verificación sintáctica Python |
| `node --check app.js` | Verificación sintáctica JS |

Rutas de la API:

* `GET /api/status`
* `GET /api/cameras`
* `POST /api/register`
* `POST /api/login`
* `POST /api/sos`
