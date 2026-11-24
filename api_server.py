"""
=============================================================================
API REST LIGERA - SERVIDOR BACKEND PARA VERSIÓN WEB / VIGÍA SOS
=============================================================================
Ejecuta un servidor HTTP local en el puerto 5000 sin dependencias externas
adicionales para permitir el inicio de sesión y registro desde index.html.
"""

import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import db_manager

PORT = int(os.getenv('API_PORT', '5000'))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class VigiaRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Habilitar CORS para peticiones desde navegador
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/login':
            self._handle_login()
        elif self.path == '/api/register':
            self._handle_register()
        elif self.path == '/api/sos':
            self._handle_sos()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/api/cameras':
            self._send_json(200, {"cameras": db_manager.get_cameras_list()})
        elif self.path == '/api/status':
            ok, msg = db_manager.test_db_connection()
            self._send_json(200, {"database_connected": ok, "message": msg})
        else:
            # Servir archivos estáticos Web
            super().do_GET()

    def _send_json(self, status_code, data):
        payload = json.dumps(data, default=str).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_body_json(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len).decode('utf-8')
        return json.loads(body)

    def _handle_login(self):
        try:
            body = self._read_body_json()
            email = body.get('email') or body.get('identifier', '')
            password = body.get('password') or body.get('pin', '')

            success, message, user = db_manager.login_user(email, password)
            self._send_json(200 if success else 400, {
                "success": success,
                "message": message,
                "user": user
            })
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_register(self):
        try:
            body = self._read_body_json()
            name = body.get('name', '').strip()
            email = body.get('email') or body.get('identifier', '')
            phone = body.get('phone', '').strip()
            password = body.get('password') or body.get('pin', '')

            success, message, user = db_manager.register_user(name, email, phone, password)
            self._send_json(200 if success else 400, {
                "success": success,
                "message": message,
                "user": user
            })
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_sos(self):
        try:
            body = self._read_body_json()
            user_id = body.get('user_id')
            recorded = db_manager.record_sos_alert(user_id)
            message = (
                "Alerta SOS registrada en base de datos." if recorded else
                "Alerta SOS activada; configura cámaras y categorías para persistirla."
            )
            self._send_json(200, {
                "success": True,
                "recorded": recorded,
                "message": message
            })
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})


def run(port=PORT):
    try:
        db_manager.ensure_schema()
        ok, msg = db_manager.test_db_connection()
        print(f"[BD] {msg}")
        if not ok:
            print("[BD] La API arrancará, pero las rutas con base de datos fallarán.")
    except Exception as e:
        print(f"[BD ERROR] No se pudo preparar el esquema: {e}")

    server_address = ('', port)
    httpd = HTTPServer(server_address, VigiaRequestHandler)
    print(f"============================================================")
    print(f" Servidor API Vigía SOS iniciado en http://localhost:{port}")
    print(f" Base de Datos: PostgreSQL '{db_manager.DB_CONFIG['dbname']}' "
          f"({db_manager.DB_CONFIG['host']}:{db_manager.DB_CONFIG['port']})")
    print(f"============================================================")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
