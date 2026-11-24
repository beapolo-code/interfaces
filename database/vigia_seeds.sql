-- =============================================================================
-- DATOS INICIALES (SEEDS) PARA BASE DE DATOS: VIGÍA / DISEÑO DE INTERFAZ
-- Conforme 100% a los ENUMs creados en PostgreSQL
-- =============================================================================

-- 1. Zonas iniciales
INSERT INTO zones (name, description, is_active) VALUES
('Entrada Principal', 'Acceso peatonal y vehicular principal', TRUE),
('Garaje vehicular', 'Zona de estacionamiento y patio interno', TRUE),
('Patio Trasero', 'Perímetro posterior del edificio', TRUE)
ON CONFLICT DO NOTHING;

-- 2. Categorías de incidentes
INSERT INTO incident_categories (code, name, severity_level, confidence_threshold, persistence_ms, is_active) VALUES
('INTRUSION', 'Intrusión no autorizada', 'critical', 0.80, 1500, TRUE),
('SOS_PANIC', 'Alerta Botón SOS', 'critical', 0.99, 0, TRUE),
('MOTION_NIGHT', 'Movimiento sospechoso nocturno', 'medium', 0.70, 2000, TRUE),
('LOITERING', 'Merodeo prolongado', 'low', 0.65, 5000, TRUE)
ON CONFLICT DO NOTHING;

-- 3. Protocolos de emergencia
INSERT INTO protocols (category_id, title, steps, is_active)
SELECT id, 'Protocolo Botón SOS', '1. Disparar sirena acústica.\n2. Notificar patrulla y central de emergencias.\n3. Transmitir coordenadas GPS y activar cámaras.', TRUE
FROM incident_categories WHERE code = 'SOS_PANIC'
LIMIT 1;

-- 4. Contactos de emergencia (contact_type: police, firefighter, medical, other)
INSERT INTO emergency_contacts (name, type, phone, email, receives_email, is_active) VALUES
('Central de Policía', 'police', '123', 'emergencias@policia.gob', TRUE, TRUE),
('Cuerpo de Bomberos', 'firefighter', '119', 'alarmas@bomberos.gob', TRUE, TRUE),
('Servicio Médico de Urgencia', 'medical', '911', 'medico@salud.gob', TRUE, TRUE),
('Seguridad Turno Central', 'other', '+593987654321', 'seguridad@vigia.local', TRUE, TRUE)
ON CONFLICT DO NOTHING;

-- 5. Cámaras iniciales (video_source_type: rtsp, webcam, file, other; connection_status: connected, disconnected, error, inactive)
INSERT INTO cameras (zone_id, name, source_type, source, fps, captures_audio, status, is_active)
SELECT z.id, 'Cámara Entrada Principal', 'rtsp'::video_source_type, 'rtsp://192.168.1.100:554/stream1', 30, TRUE, 'connected'::connection_status, TRUE
FROM zones z WHERE z.name = 'Entrada Principal' LIMIT 1;

INSERT INTO cameras (zone_id, name, source_type, source, fps, captures_audio, status, is_active)
SELECT z.id, 'Garaje vehicular', 'rtsp'::video_source_type, 'rtsp://192.168.1.101:554/stream1', 30, FALSE, 'connected'::connection_status, TRUE
FROM zones z WHERE z.name = 'Garaje vehicular' LIMIT 1;

INSERT INTO cameras (zone_id, name, source_type, source, fps, captures_audio, status, is_active)
SELECT z.id, 'Patio posterior', 'rtsp'::video_source_type, 'rtsp://192.168.1.102:554/stream1', 24, FALSE, 'disconnected'::connection_status, TRUE
FROM zones z WHERE z.name = 'Patio Trasero' LIMIT 1;

-- 6. Sirenas disuasorias (hardware_connection_type: serial, bluetooth, network, usb, other)
INSERT INTO sirens (zone_id, name, connection_type, port, bluetooth_address, status, is_active)
SELECT z.id, 'Sirena Perimetral Garaje', 'network'::hardware_connection_type, '8080', NULL, 'connected'::connection_status, TRUE
FROM zones z WHERE z.name = 'Garaje vehicular' LIMIT 1;

-- 7. Términos y condiciones
INSERT INTO terms_and_conditions (version, title, content, is_current) VALUES
('v1.0', 'Términos de Servicio y Privacidad Vigía SOS', 'El uso de esta plataforma de seguridad y botón de pánico SOS se rige bajo las políticas de protección de datos personales y monitoreo en tiempo real.', TRUE)
ON CONFLICT DO NOTHING;

-- 8. Usuario Administrador por defecto
INSERT INTO users (name, email, phone, password_hash, role, is_active) VALUES
('Administrador Vigía', 'admin@vigia.local', '0990000000', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'admin'::user_role, TRUE)
ON CONFLICT (email) DO NOTHING;
