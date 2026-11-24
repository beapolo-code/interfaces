-- =============================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS: VIGÍA / DISEÑO DE INTERFAZ
-- Compatible con PostgreSQL 12+ / pgAdmin 4
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. TIPOS PERSONALIZADOS (ENUMS)
-- -----------------------------------------------------------------------------

DO $$ BEGIN
    CREATE TYPE video_source_type AS ENUM ('rtsp', 'webcam', 'file', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE connection_status AS ENUM ('connected', 'disconnected', 'error', 'inactive');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE hardware_connection_type AS ENUM ('serial', 'bluetooth', 'network', 'usb', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE evidence_type AS ENUM ('image', 'video', 'audio', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE review_status AS ENUM ('pending', 'confirmed', 'rejected', 'reviewed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contact_type AS ENUM ('police', 'firefighter', 'medical', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'operator', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- -----------------------------------------------------------------------------
-- 2. MÓDULO: USERS & TERMS (Usuarios y Términos)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS terms_and_conditions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS terms_acceptances (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    terms_id INT NOT NULL REFERENCES terms_and_conditions(id) ON DELETE CASCADE,
    accepted BOOLEAN NOT NULL DEFAULT FALSE,
    accepted_at TIMESTAMPTZ,
    CONSTRAINT uq_user_terms UNIQUE (user_id, terms_id)
);

-- -----------------------------------------------------------------------------
-- 3. MÓDULO: INFRASTRUCTURE (Infraestructura)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    zone_id INT NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL,
    source_type video_source_type NOT NULL DEFAULT 'rtsp',
    source VARCHAR(500) NOT NULL,
    fps INT NOT NULL DEFAULT 30,
    captures_audio BOOLEAN NOT NULL DEFAULT FALSE,
    status connection_status NOT NULL DEFAULT 'disconnected',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sirens (
    id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES zones(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    connection_type hardware_connection_type NOT NULL,
    port VARCHAR(50),
    bluetooth_address VARCHAR(17),
    status connection_status NOT NULL DEFAULT 'disconnected',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------------------------------
-- 4. MÓDULO: INCIDENTS & EVIDENCE (Incidentes y Evidencia)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incident_categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    severity_level severity_level NOT NULL,
    confidence_threshold NUMERIC(3, 2) NOT NULL DEFAULT 0.70,
    persistence_ms INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    camera_id INT NOT NULL REFERENCES cameras(id) ON DELETE RESTRICT,
    category_id INT NOT NULL REFERENCES incident_categories(id) ON DELETE RESTRICT,
    confidence NUMERIC(5, 4) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alarm_active BOOLEAN NOT NULL DEFAULT FALSE,
    silenced_by INT REFERENCES users(id) ON DELETE SET NULL,
    silenced_at TIMESTAMPTZ,
    review_status review_status NOT NULL DEFAULT 'pending',
    reviewed_by INT REFERENCES users(id) ON DELETE SET NULL
);

-- Alertas SOS del botón de pánico. No dependen de cámaras ni categorías,
-- para que una base recién creada (sin seeds) pueda registrarlas desde cero.
CREATE TABLE IF NOT EXISTS sos_alerts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'mobile',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sos_alerts_created_at ON sos_alerts(created_at DESC);

CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    incident_id INT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    type evidence_type NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. MÓDULO: ALERTS & PROTOCOLS (Alertas y Protocolos)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES incident_categories(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    steps TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS emergency_contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    type contact_type NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(150),
    receives_email BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    incident_id INT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    contact_id INT REFERENCES emergency_contacts(id) ON DELETE SET NULL,
    recipient_email VARCHAR(150),
    status notification_status NOT NULL DEFAULT 'pending',
    error TEXT,
    sent_at TIMESTAMPTZ
);

-- -----------------------------------------------------------------------------
-- 6. ÍNDICES DE CONSULTA RÁPIDA
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_cameras_zone_id ON cameras(zone_id);
CREATE INDEX IF NOT EXISTS idx_sirens_zone_id ON sirens(zone_id);
CREATE INDEX IF NOT EXISTS idx_incidents_camera_id ON incidents(camera_id);
CREATE INDEX IF NOT EXISTS idx_incidents_category_id ON incidents(category_id);
CREATE INDEX IF NOT EXISTS idx_incidents_occurred_at ON incidents(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_incident_id ON evidence(incident_id);
CREATE INDEX IF NOT EXISTS idx_notifications_incident_id ON notifications(incident_id);
CREATE INDEX IF NOT EXISTS idx_terms_acceptances_user ON terms_acceptances(user_id);
