-- ==============================================================================
-- Wolf Logic — PostgreSQL & PostgREST Relational Telemetry Schema
-- ==============================================================================
-- Auto-initializes on port 5433 (Postgres) and serves REST APIs on port 3000 (PostgREST).
-- User: ncl / Password: breakaway / Superuser: postgres
-- ==============================================================================

-- 1. Create ncl user and assign permissions
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ncl') THEN
      CREATE ROLE ncl WITH LOGIN PASSWORD 'breakaway' SUPERUSER;
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE wolf_logic TO ncl;

-- 2. Console Events Stream
CREATE TABLE IF NOT EXISTS console_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp_utc TEXT NOT NULL,
    epoch_ms DOUBLE PRECISION NOT NULL,
    smpte_timecode VARCHAR(32) NOT NULL,
    protocol VARCHAR(32) NOT NULL,          -- 'OSC', 'sACN', 'Art-Net', 'MIDI'
    source_ip VARCHAR(64) NOT NULL,
    address TEXT NOT NULL,                  -- '/eos/out/param/pan', '/eos/cmd', etc.
    raw_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Master Fixture Inventory & Patch
CREATE TABLE IF NOT EXISTS fixture_patch (
    fixture_id SERIAL PRIMARY KEY,
    unit_number VARCHAR(32),
    manufacturer VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    mode VARCHAR(64) NOT NULL,
    dmx_channels INTEGER NOT NULL,
    category VARCHAR(64),                   -- 'Profile', 'Wash', 'Beam', 'Batten'
    channel_number INTEGER,                 -- User Assigned Channel
    dmx_universe INTEGER,                   -- User Assigned Universe
    dmx_address INTEGER,                    -- User Assigned Address
    pos_x REAL DEFAULT 0.0,
    pos_y REAL DEFAULT 0.0,
    pos_z REAL DEFAULT 0.0
);

-- 4. Live 2,560-Dimension Spatial HSI State Vector Snapshot
CREATE TABLE IF NOT EXISTS live_fixture_state (
    fixture_id SERIAL PRIMARY KEY,
    channel_number INTEGER,
    hue REAL DEFAULT 0.0,                   -- 0.0 - 360.0 degrees
    saturation REAL DEFAULT 0.0,            -- 0.0 - 100.0 percent
    intensity REAL DEFAULT 0.0,             -- 0.0 - 100.0 percent
    cct_kelvin REAL DEFAULT 4400.0,         -- Color Temperature (Kelvin)
    pan REAL DEFAULT 0.0,                   -- In degrees or raw 16-bit
    tilt REAL DEFAULT 0.0,
    zoom REAL DEFAULT 0.0,
    shutter_strobe INTEGER DEFAULT 0,
    last_updated_epoch DOUBLE PRECISION
);

-- Indices for sub-millisecond query performance
CREATE INDEX IF NOT EXISTS idx_events_timecode ON console_events(smpte_timecode);
CREATE INDEX IF NOT EXISTS idx_events_epoch ON console_events(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_patch_channel ON fixture_patch(channel_number);

-- Grant full access to anonymous PostgREST user
GRANT USAGE ON SCHEMA public TO ncl;
GRANT ALL ON ALL TABLES IN SCHEMA public TO ncl;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ncl;
