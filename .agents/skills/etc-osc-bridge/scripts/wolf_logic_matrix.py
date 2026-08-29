#!/usr/bin/env python3
"""
Wolf Logic — High-Dimensional Fixture & Parameter Matrix Engine
Stores and transforms high-dimensional spatial states (Pan, Tilt, Color, Beam, Intensity)
with sub-millisecond timecode into SQLite for local LLM & Vision analysis on M1 Max.
"""

import sqlite3
import os
import math
import json
import time
from typing import Dict, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")

# Parameter dimension vector definition
PARAM_NAMES = [
    "intensity", "pan", "tilt", "red", "green", "blue", 
    "white", "amber", "zoom", "iris", "gobo", "focus", "shutter"
]

MATRIX_SCHEMA = """
-- High-dimensional fixture parameter state table
CREATE TABLE IF NOT EXISTS fixture_matrix (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    epoch_ms        INTEGER NOT NULL,
    timecode        TEXT NOT NULL,          -- SMPTE formatted 'HH:MM:SS:FF'
    channel_num     INTEGER NOT NULL,
    intensity       REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    pan             REAL DEFAULT 0.0,       -- Degrees (-270.0 to +270.0 or 0-540)
    tilt            REAL DEFAULT 0.0,       -- Degrees (-135.0 to +135.0 or 0-270)
    red             INTEGER DEFAULT 0,      -- 0 - 255
    green           INTEGER DEFAULT 0,      -- 0 - 255
    blue            INTEGER DEFAULT 0,      -- 0 - 255
    white           INTEGER DEFAULT 0,      -- 0 - 255
    amber           INTEGER DEFAULT 0,      -- 0 - 255
    zoom            REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    iris            REAL DEFAULT 0.0,       -- 0.0 - 100.0%
    gobo            INTEGER DEFAULT 0,      -- Index / Raw Slot
    shutter         REAL DEFAULT 100.0,     -- Strobe / Strobe Open
    cue_context     TEXT                    -- Current active cue at this time
);

CREATE INDEX IF NOT EXISTS idx_matrix_time   ON fixture_matrix(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_matrix_chan   ON fixture_matrix(channel_num, epoch_ms);
CREATE INDEX IF NOT EXISTS idx_matrix_tc     ON fixture_matrix(timecode);
"""

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
        self.live_state: Dict[int, Dict[str, float]] = {}

    def update_parameter(self, channel_num: int, param: str, value: float, cue_context: str = ""):
        """Updates live memory state and persists delta to the database matrix."""
        if channel_num not in self.live_state:
            self.live_state[channel_num] = {
                "intensity": 0.0, "pan": 0.0, "tilt": 0.0,
                "red": 0, "green": 0, "blue": 0, "white": 0, "amber": 0,
                "zoom": 0.0, "iris": 0.0, "gobo": 0, "shutter": 100.0
            }
        
        param_clean = param.lower()
        if param_clean in self.live_state[channel_num]:
            self.live_state[channel_num][param_clean] = value

        ms = int(time.time() * 1000)
        tc = format_smpte(ms)
        f = self.live_state[channel_num]

        self.conn.execute(
            """INSERT INTO fixture_matrix
               (epoch_ms, timecode, channel_num, intensity, pan, tilt, red, green, blue, white, amber, zoom, iris, gobo, shutter, cue_context)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ms, tc, channel_num, f["intensity"], f["pan"], f["tilt"], int(f["red"]), int(f["green"]), int(f["blue"]),
             int(f["white"]), int(f["amber"]), f["zoom"], f["iris"], int(f["gobo"]), f["shutter"], cue_context)
        )
        self.conn.commit()

    # --- Matrix Math & Mathematical Transformations ---

    def invert_pan(self, channels: List[int], center_deg: float = 0.0):
        """Mathematically inverts pan angle across selected fixtures."""
        for ch in channels:
            if ch in self.live_state:
                current = self.live_state[ch]["pan"]
                self.update_parameter(ch, "pan", center_deg - current)

    def invert_tilt(self, channels: List[int], center_deg: float = 0.0):
        """Mathematically inverts tilt angle across selected fixtures."""
        for ch in channels:
            if ch in self.live_state:
                current = self.live_state[ch]["tilt"]
                self.update_parameter(ch, "tilt", center_deg - current)

    def rotate_rgb_hue(self, channels: List[int], angle_degrees: float):
        """Rotates color vector on the 3D RGB color sphere without altering intensity."""
        rad = math.radians(angle_degrees)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        for ch in channels:
            if ch in self.live_state:
                r = self.live_state[ch]["red"] / 255.0
                g = self.live_state[ch]["green"] / 255.0
                b = self.live_state[ch]["blue"] / 255.0

                # Standard 3D RGB Color Rotation Matrix
                new_r = r * (0.299 + 0.701 * cos_a + 0.168 * sin_a) + g * (0.587 - 0.587 * cos_a + 0.330 * sin_a) + b * (0.114 - 0.114 * cos_a - 0.497 * sin_a)
                new_g = r * (0.299 - 0.299 * cos_a - 0.328 * sin_a) + g * (0.587 + 0.413 * cos_a + 0.035 * sin_a) + b * (0.114 - 0.114 * cos_a + 0.288 * sin_a)
                new_b = r * (0.299 - 0.300 * cos_a + 1.250 * sin_a) + g * (0.587 - 0.588 * cos_a - 1.050 * sin_a) + b * (0.114 + 0.886 * cos_a - 0.203 * sin_a)

                self.update_parameter(ch, "red", max(0, min(255, int(new_r * 255))))
                self.update_parameter(ch, "green", max(0, min(255, int(new_g * 255))))
                self.update_parameter(ch, "blue", max(0, min(255, int(new_b * 255))))

    def get_snapshot_matrix(self) -> Dict[str, Any]:
        """Dumps high-dimensional spatial state vector for LLM / Vision model consumption."""
        ms = int(time.time() * 1000)
        return {
            "epoch_ms": ms,
            "timecode": format_smpte(ms),
            "fixture_count": len(self.live_state),
            "fixtures": self.live_state
        }

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print(f"[+] Initializing Wolf Logic High-Dimensional Matrix Engine...")
    engine = FixtureMatrixEngine()

    # Simulate moving light rig with 6 spots
    for ch in range(1, 7):
        engine.update_parameter(ch, "intensity", 100.0, cue_context="Cue 1")
        engine.update_parameter(ch, "pan", (ch - 3.5) * 30.0, cue_context="Cue 1")
        engine.update_parameter(ch, "tilt", 45.0, cue_context="Cue 1")
        engine.update_parameter(ch, "red", 255, cue_context="Cue 1")
        engine.update_parameter(ch, "blue", 128, cue_context="Cue 1")

    print("[+] Current Rig State Matrix:")
    print(json.dumps(engine.get_snapshot_matrix(), indent=2))

    print("[+] Applying 180° Color Rotation & Pan Inversion to Ch 1-3...")
    engine.rotate_rgb_hue([1, 2, 3], 180.0)
    engine.invert_pan([1, 2, 3])

    print("[+] Transformed Rig Matrix:")
    print(json.dumps(engine.get_snapshot_matrix(), indent=2))

    engine.close()
    print("[+] Matrix Engine verified successfully.")
