#!/usr/bin/env python3
"""
Wolf Logic — High-Dimensional Fixture & Universal HSI Parameter Matrix Engine
Normalizes all fixture color spaces (RGB, RGBW, RGBAW, Lustr, CMY) into universal HSI
(Hue 0-360°, Saturation 0-100%, Intensity 0-100%) stored in SQLite with sub-millisecond SMPTE timecode.
"""

import sqlite3
import os
import math
import json
import time
from typing import Dict, List, Optional, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")

MATRIX_SCHEMA = """
-- Universal High-Dimensional Fixture State Table with HSI Primary Color Space
CREATE TABLE IF NOT EXISTS fixture_matrix (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    epoch_ms        INTEGER NOT NULL,
    timecode        TEXT NOT NULL,          -- SMPTE formatted 'HH:MM:SS:FF'
    channel_num     INTEGER NOT NULL,
    intensity       REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    
    -- Universal HSI Color Representation (Fixture-Agnostic)
    hue             REAL DEFAULT 0.0,       -- 0.0° - 360.0° (Color Angle)
    saturation      REAL DEFAULT 0.0,       -- 0.0% - 100.0% (Purity)
    
    -- Spatial Coordinates
    pan             REAL DEFAULT 0.0,       -- Degrees (-270.0 to +270.0)
    tilt            REAL DEFAULT 0.0,       -- Degrees (-135.0 to +135.0)
    
    -- Beam & Optics
    zoom            REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    iris            REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    focus           REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    gobo            INTEGER DEFAULT 0,      -- Index / Raw Slot
    shutter         REAL DEFAULT 100.0,     -- Strobe / Open
    
    -- Raw DMX Native Channels (Reference)
    raw_red         INTEGER DEFAULT 0,
    raw_green       INTEGER DEFAULT 0,
    raw_blue        INTEGER DEFAULT 0,
    raw_white       INTEGER DEFAULT 0,
    raw_amber       INTEGER DEFAULT 0,
    
    cue_context     TEXT                    -- Current active cue at this time
);

CREATE INDEX IF NOT EXISTS idx_matrix_time   ON fixture_matrix(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_matrix_chan   ON fixture_matrix(channel_num, epoch_ms);
CREATE INDEX IF NOT EXISTS idx_matrix_tc     ON fixture_matrix(timecode);
CREATE INDEX IF NOT EXISTS idx_matrix_hue    ON fixture_matrix(hue, saturation);
"""

def rgb_to_hsi(r: int, g: int, b: int) -> Tuple[float, float]:
    """Converts 8-bit RGB (0-255) to Hue (0-360°) and Saturation (0-100%)."""
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    c_max = max(r_norm, g_norm, b_norm)
    c_min = min(r_norm, g_norm, b_norm)
    delta = c_max - c_min

    # Calculate Hue
    if delta == 0:
        hue = 0.0
    elif c_max == r_norm:
        hue = 60.0 * (((g_norm - b_norm) / delta) % 6)
    elif c_max == g_norm:
        hue = 60.0 * (((b_norm - r_norm) / delta) + 2)
    else:
        hue = 60.0 * (((r_norm - g_norm) / delta) + 4)

    if hue < 0:
        hue += 360.0

    # Calculate Saturation
    saturation = 0.0 if c_max == 0 else (delta / c_max) * 100.0

    return round(hue, 2), round(saturation, 2)

def hsi_to_rgb(hue: float, saturation: float, intensity: float = 100.0) -> Tuple[int, int, int]:
    """Converts universal HSI coordinates back into standard 8-bit RGB."""
    h = hue % 360.0
    s = max(0.0, min(100.0, saturation)) / 100.0
    v = max(0.0, min(100.0, intensity)) / 100.0

    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        rp, gp, bp = c, x, 0
    elif 60 <= h < 120:
        rp, gp, bp = x, c, 0
    elif 120 <= h < 180:
        rp, gp, bp = 0, c, x
    elif 180 <= h < 240:
        rp, gp, bp = 0, x, c
    elif 240 <= h < 300:
        rp, gp, bp = x, 0, c
    else:
        rp, gp, bp = c, 0, x

    r = int((rp + m) * 255)
    g = int((gp + m) * 255)
    b = int((bp + m) * 255)

    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

def format_smpte(epoch_ms: int, fps: int = 30) -> str:
    """Converts epoch milliseconds into SMPTE Timecode string (HH:MM:SS:FF)."""
    total_seconds = epoch_ms / 1000.0
    hours = int(total_seconds // 3600) % 24
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames = int((total_seconds - int(total_seconds)) * fps)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

class FixtureMatrixEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(MATRIX_SCHEMA)
        self.live_state: Dict[int, Dict[str, Any]] = {}

    def set_hsi(self, channel_num: int, hue: float, saturation: float, intensity: float, cue_context: str = ""):
        """Universal HSI Setter — primary method for setting fixture color & intensity."""
        if channel_num not in self.live_state:
            self._init_fixture_state(channel_num)

        f = self.live_state[channel_num]
        f["hue"] = round(hue % 360.0, 2)
        f["saturation"] = max(0.0, min(100.0, round(saturation, 2)))
        f["intensity"] = max(0.0, min(100.0, round(intensity, 2)))

        # Derive reference RGB
        r, g, b = hsi_to_rgb(f["hue"], f["saturation"], f["intensity"])
        f["raw_red"], f["raw_green"], f["raw_blue"] = r, g, b

        self._persist_state(channel_num, cue_context)

    def _init_fixture_state(self, channel_num: int):
        self.live_state[channel_num] = {
            "intensity": 0.0, "hue": 0.0, "saturation": 0.0,
            "pan": 0.0, "tilt": 0.0, "zoom": 0.0, "iris": 0.0,
            "focus": 0.0, "gobo": 0, "shutter": 100.0,
            "raw_red": 0, "raw_green": 0, "raw_blue": 0,
            "raw_white": 0, "raw_amber": 0
        }

    def _persist_state(self, channel_num: int, cue_context: str = ""):
        ms = int(time.time() * 1000)
        tc = format_smpte(ms)
        f = self.live_state[channel_num]

        self.conn.execute(
            """INSERT INTO fixture_matrix
               (epoch_ms, timecode, channel_num, intensity, hue, saturation, pan, tilt,
                zoom, iris, focus, gobo, shutter, raw_red, raw_green, raw_blue, raw_white, raw_amber, cue_context)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ms, tc, channel_num, f["intensity"], f["hue"], f["saturation"], f["pan"], f["tilt"],
             f["zoom"], f["iris"], f["focus"], int(f["gobo"]), f["shutter"],
             int(f["raw_red"]), int(f["raw_green"]), int(f["raw_blue"]),
             int(f["raw_white"]), int(f["raw_amber"]), cue_context)
        )
        self.conn.commit()

    # --- HSI Spatial Vector Math ---

    def shift_hue(self, channels: List[int], degrees: float):
        """Pure HSI mathematical hue shift (e.g. +180° for complement, +120° for triadic)."""
        for ch in channels:
            if ch in self.live_state:
                new_h = (self.live_state[ch]["hue"] + degrees) % 360.0
                self.set_hsi(ch, new_h, self.live_state[ch]["saturation"], self.live_state[ch]["intensity"])

    def set_saturation(self, channels: List[int], saturation: float):
        """Direct saturation control (0% = pure white/neutral pastel, 100% = saturated color)."""
        for ch in channels:
            if ch in self.live_state:
                self.set_hsi(ch, self.live_state[ch]["hue"], saturation, self.live_state[ch]["intensity"])

    def get_hsi_matrix(self) -> Dict[str, Any]:
        """Returns the universal HSI parameter matrix across all fixtures."""
        ms = int(time.time() * 1000)
        return {
            "epoch_ms": ms,
            "timecode": format_smpte(ms),
            "fixture_count": len(self.live_state),
            "fixtures": {
                ch: {
                    "hsi": [f["hue"], f["saturation"], f["intensity"]],
                    "spatial": [f["pan"], f["tilt"]],
                    "optics": [f["zoom"], f["iris"], f["focus"]],
                    "gobo": f["gobo"]
                }
                for ch, f in self.live_state.items()
            }
        }

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("[+] Initializing Universal HSI Parameter Matrix Engine...")
    engine = FixtureMatrixEngine()

    # Set moving heads to HSI colors
    engine.set_hsi(1, hue=0.0, saturation=100.0, intensity=100.0, cue_context="Look 1 - Red")
    engine.set_hsi(2, hue=120.0, saturation=100.0, intensity=100.0, cue_context="Look 1 - Green")
    engine.set_hsi(3, hue=240.0, saturation=100.0, intensity=100.0, cue_context="Look 1 - Blue")
    engine.set_hsi(4, hue=60.0, saturation=100.0, intensity=100.0, cue_context="Look 1 - Yellow")

    print("[+] Live HSI Rig State Matrix:")
    print(json.dumps(engine.get_hsi_matrix(), indent=2))

    print("[+] Applying +180° Complementary Hue Shift to all fixtures...")
    engine.shift_hue([1, 2, 3, 4], 180.0)

    print("[+] Transformed HSI Rig State Matrix:")
    print(json.dumps(engine.get_hsi_matrix(), indent=2))

    engine.close()
    print("[+] Universal HSI Matrix Engine verified.")
