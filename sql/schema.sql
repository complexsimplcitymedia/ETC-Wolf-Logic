-- ==============================================================================
-- Wolf Logic — Master SQLite & PostgREST Relational Telemetry Schema
-- ==============================================================================
-- Tracks raw Eos OSC events, cue execution, command history, and the
-- 2,560-dimension spatial HSI parameter matrix with sub-millisecond timestamps.
-- ==============================================================================

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- 1. Console Events Stream
CREATE TABLE IF NOT EXISTS console_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT NOT NULL,
    epoch_ms REAL NOT NULL,
    smpte_timecode TEXT NOT NULL,
    protocol TEXT NOT NULL,          -- 'OSC', 'sACN', 'Art-Net', 'MIDI'
    source_ip TEXT NOT NULL,
    address TEXT NOT NULL,           -- '/eos/out/param/pan', '/eos/cmd', etc.
    raw_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Master Fixture Inventory & Patch
CREATE TABLE IF NOT EXISTS fixture_patch (
    fixture_id INTEGER PRIMARY KEY,
    unit_number TEXT,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    mode TEXT NOT NULL,
    dmx_channels INTEGER NOT NULL,
    category TEXT,                   -- 'Profile', 'Wash', 'Beam', 'Batten'
    channel_number INTEGER,          -- User Assigned Channel
    dmx_universe INTEGER,            -- User Assigned Universe
    dmx_address INTEGER,             -- User Assigned Address
    pos_x REAL DEFAULT 0.0,
    pos_y REAL DEFAULT 0.0,
    pos_z REAL DEFAULT 0.0
);

-- 3. Live 2,560-Dimension Spatial HSI State Vector Snapshot
CREATE TABLE IF NOT EXISTS live_fixture_state (
    fixture_id INTEGER PRIMARY KEY,
    channel_number INTEGER,
    hue REAL DEFAULT 0.0,            -- 0.0 - 360.0 degrees
    saturation REAL DEFAULT 0.0,     -- 0.0 - 100.0 percent
    intensity REAL DEFAULT 0.0,      -- 0.0 - 100.0 percent
    cct_kelvin REAL DEFAULT 4400.0,  -- Color Temperature (Kelvin)
    pan REAL DEFAULT 0.0,            -- In degrees or raw 16-bit
    tilt REAL DEFAULT 0.0,
    zoom REAL DEFAULT 0.0,
    shutter_strobe INTEGER DEFAULT 0,
    last_updated_epoch REAL
);

-- Indices for sub-millisecond query performance
CREATE INDEX IF NOT EXISTS idx_events_timecode ON console_events(smpte_timecode);
CREATE INDEX IF NOT EXISTS idx_events_epoch ON console_events(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_patch_channel ON fixture_patch(channel_number);
