# 🛡️ SEGURIDAD SOS — Sistema Unificado Material Design 3 (5 Vistas)

> Frontend web y app móvil sincronizados visual y funcionalmente, conectados a **PostgreSQL 18** y construidos con tokens **Material Design 3** (tema oscuro).

Este proyecto contiene dos plataformas:

1. **Versión Web:** HTML5 + CSS3 con tokens MD3 y JavaScript Vanilla. Incluye panel de escritorio con Sidebar y shell móvil con bottom-navigation.
2. **Versión Móvil:** Python con **Kivy** y **KivyMD 2.0.0**, `MDScreenManager`, `MDNavigationBar`, `MDNavigationDrawer` y soporte táctil.

---

## 📱 Las 5 Vistas Principales

1. **Iniciar Sesión:** Correo electrónico y contraseña.
2. **Crear Cuenta:** Nombre, teléfono, correo y contraseña.
3. **Inicio (Alerta SOS):** Saludo, botón central SOS con pulsado sostenido de 3 segundos y anillo de progreso, acceso directo a cámaras y botón de alerta inmediata.
4. **Mis Cámaras:** Grilla de monitoreo con chips (*Todas*, *En línea*, *Grabando*) y relojes sincronizados.
5. **Mi Perfil:** Datos del usuario, estado GPS y cierre de sesión.

---

## 🎨 Paleta Material Design 3 (tema oscuro)

| Token | Valor | Uso |
|---|---|---|
| `Primary` / `On Primary` | `#FFB4AB` / `#690005` | Acciones principales y estado activo |
| `Secondary` / `On Secondary` | `#A7EEFF` / `#00363F` | Acentos, focus rings y cyan de interfaz |
| `Tertiary` / `On Tertiary` | `#AECBFF` / `#002B56` | Acciones secundarias |
| `Background` / `On Background` | `#0B1020` / `#E4E7F2` | Fondo general |
| `Surface` / `On Surface` | `#121A2E` / `#E4E7F2` | Contenedores y tarjetas |
| `Surface Variant` / `On Surface Variant` | `#1E2942` / `#B9C5E3` | Inputs, Sidebar y bottom-nav |
| `Error` / `On Error` | `#FFB4AB` / `#690005` | Validaciones y zonas de alerta |
| `SOS` / `On SOS` | `#C11E38` / `#FFFFFF` | Botón de pánico (contraste 5.98:1) |

Los nombres anteriores (`--bg-main`, `--btn-primary`, `--accent-cyan`, etc.) se conservan como alias de los tokens M3 para no romper componentes existentes.

### Botón de alerta
* **Escritorio:** botón `Disparar alerta SOS` en el Sidebar (`#nav-alert`), siempre visible, con `min-height: 48px`, `overflow: visible`, foco accesible y llamada directa a `triggerSidebarSOS()`.
* **Móvil web:** botón `SOS` en la navegación inferior (`#nav-sos`), área táctil mínima de `48x48px`, sin recorte por `overflow` y con `onclick="triggerMobileSOS()"`.
* Ambas acciones abren el overlay de emergencia, muestran un toast y envían `POST /api/sos`.
* En KivyMD 2.0.0 el botón de la pestaña `nav_sos` tiene `140dp` de alto y llama a `app.activate_sos_overlay()`.
* El `MDNavigationDrawer` incluye siempre un item **Alerta SOS** (icono `warning`, color Error) que cierra el drawer, navega a `nav_sos` y dispara la alerta; también hay un botón SOS visible en la cabecera y en la `MDTopAppBar` de cámaras.

---

## 🗄️ Base de datos

* Motor: **PostgreSQL 18**
* Base de datos: **`vigia_sos`** (no se usa la antigua `Diseño de Interfaz`)
* Configuración: archivos `.env` / `.env.example` (ver `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE`)
* La contraseña local se tomó de un `.env.development` existente en otro proyecto del equipo (`postgres` / `12345`). En `.env.example` se deja un marcador de posición.
* La base se recrea **limpia**: solo DDL (`database/vigia_schema.sql`), 13 tablas vacías (incluye `sos_alerts`), sin ejecutar `vigia_seeds.sql`.

```powershell
python database/reset_database.py
```

---

## 📁 Estructura del Proyecto

```text
DISE-O-DE-INTERFAZ-main/
├── web/
│   ├── index.html            # Panel web de escritorio (Sidebar + SOS)
│   ├── styles.css            # Tokens MD3 sincronizados
│   └── app.js                # Controlador legado (no enlazado por index.html)
├── mobile/
│   ├── main.py               # App KivyMD en tamaño móvil (414x896)
│   ├── db_manager.py         # Acceso PostgreSQL por entorno
│   ├── requirements.txt      # Dependencias
│   └── run.bat               # Lanzador Windows móvil
├── database/
│   ├── vigia_schema.sql      # DDL de las 13 tablas (incluye sos_alerts)
│   ├── vigia_seeds.sql       # Seeds NO aplicados en la BD limpia
│   └── reset_database.py     # Recrea la BD desde cero sin datos de prueba
├── .env                      # Configuración local (ignorada por Git)
├── .env.example              # Plantilla de configuración
├── api_server.py             # API REST en :5000
├── db_manager.py             # Conexión, auth y registro de SOS
├── index.html                # Shell web móvil (bottom-nav + SOS)
├── styles.css                # Tokens MD3 sincronizados
├── main.py                   # App KivyMD en tamaño escritorio/web (1280x800)
├── run_api.bat               # Lanzador de la API
├── run_desktop.bat           # Lanzador KivyMD escritorio/web
└── run_mobile.bat            # Lanzador KivyMD móvil
```

---

## 🚀 Instrucciones de Ejecución

### 1. Base de datos y API

```powershell
pip install -r requirements.txt
python database/reset_database.py
python api_server.py
```

La API quedará en `http://localhost:5000` con rutas:

* `GET /api/status`
* `GET /api/cameras`
* `POST /api/register`
* `POST /api/login`
* `POST /api/sos`

### 2. Versión Web

Con la API en marcha, abre:

* Panel de escritorio: `web/index.html`
* Shell móvil: `index.html`

Registra un usuario desde **Crear Cuenta** e inicia sesión. La BD está vacía, por lo que no existe el usuario admin de las versiones anteriores.

### 3. Versión KivyMD (dos tamaños)

```powershell
pip install -r requirements.txt

# Escritorio/web: 1280x800
python main.py
# o: run_desktop.bat

# Móvil: 414x896
python mobile/main.py
# o: run_mobile.bat
```

También puedes forzar el tamaño con `python main.py --mobile` o `python mobile/main.py --desktop`, o cambiarlo en caliente con **F9**. La variable de entorno `VIGIA_VIEW=desktop|mobile` también funciona.

---

## ✅ Verificación rápida

```powershell
python -m py_compile db_manager.py api_server.py main.py mobile/db_manager.py mobile/main.py database/reset_database.py
node --check app.js
node --check web/app.js
```

Para probar la API sin navegador:

```powershell
curl http://localhost:5000/api/status
curl http://localhost:5000/api/cameras
```
