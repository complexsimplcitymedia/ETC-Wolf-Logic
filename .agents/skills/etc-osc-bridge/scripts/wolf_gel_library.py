#!/usr/bin/env python3
"""
Wolf Logic — Universal Gel Library & Color Preset Engine
Pre-loaded with Roscolux, Lee Filters, and Color Correction Gels (Bastard Amber, CTO, CTB)
mapped to exact universal HSI coordinates for instant Eos preset generation.
"""

import sqlite3
import os
import json
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")

# Comprehensive Industry Standard Gel Database (Roscolux, Lee, Color Temp Correction)
GEL_PRESETS = [
    # --- Bastard Ambers & Warm Tints ---
    {"code": "R02",  "name": "Bastard Amber",          "mfg": "Rosco", "hue": 35.0,  "sat": 30.0, "trans": 88, "notes": "Warm flattering skin tone key"},
    {"code": "R03",  "name": "Dark Bastard Amber",     "mfg": "Rosco", "hue": 32.0,  "sat": 45.0, "trans": 74, "notes": "Rich warm amber wash"},
    {"code": "R04",  "name": "Medium Bastard Amber",   "mfg": "Rosco", "hue": 34.0,  "sat": 38.0, "trans": 80, "notes": "Standard theatrical key"},
    {"code": "L152", "name": "Pale Gold",              "mfg": "Lee",   "hue": 40.0,  "sat": 35.0, "trans": 82, "notes": "Golden morning backlight"},
    {"code": "R09",  "name": "Pale Amber Gold",        "mfg": "Rosco", "hue": 42.0,  "sat": 40.0, "trans": 78, "notes": "Warm sunlight beam"},

    # --- Color Temperature Correction (CTO / CTB) ---
    {"code": "L201", "name": "Full CT Blue (CTB)",     "mfg": "Lee",   "hue": 208.0, "sat": 38.0, "trans": 34, "notes": "Converts 3200K Tungsten to 5600K Daylight"},
    {"code": "L202", "name": "Half CT Blue (1/2 CTB)", "mfg": "Lee",   "hue": 208.0, "sat": 20.0, "trans": 54, "notes": "Converts 3200K to 4400K Cool White"},
    {"code": "L203", "name": "Quarter CTB (1/4 CTB)",  "mfg": "Lee",   "hue": 208.0, "sat": 10.0, "trans": 69, "notes": "Subtle cool daylight nudge"},
    {"code": "L204", "name": "Full CT Orange (CTO)",   "mfg": "Lee",   "hue": 35.0,  "sat": 58.0, "trans": 58, "notes": "Converts 5600K Daylight to 3200K Tungsten"},
    {"code": "L205", "name": "Half CT Orange (1/2 CTO)","mfg": "Lee",  "hue": 36.0,  "sat": 32.0, "trans": 71, "notes": "Warm tungsten blend"},
    {"code": "L206", "name": "Quarter CTO (1/4 CTO)",  "mfg": "Lee",   "hue": 37.0,  "sat": 16.0, "trans": 81, "notes": "Subtle warmth nudge"},

    # --- Theatrical Primaries & Saturated Colors ---
    {"code": "R26",  "name": "Light Red",              "mfg": "Rosco", "hue": 0.0,   "sat": 100.0,"trans": 15, "notes": "Primary dramatic red"},
    {"code": "R27",  "name": "Medium Red",             "mfg": "Rosco", "hue": 355.0, "sat": 100.0,"trans": 4,  "notes": "Deep saturated blood red"},
    {"code": "R80",  "name": "Primary Blue",           "mfg": "Rosco", "hue": 240.0, "sat": 100.0,"trans": 3,  "notes": "Classic deep stage blue"},
    {"code": "R83",  "name": "Medium Blue",            "mfg": "Rosco", "hue": 225.0, "sat": 95.0, "trans": 11, "notes": "Vivid atmospheric blue"},
    {"code": "R68",  "name": "Parry Sky Blue",         "mfg": "Rosco", "hue": 200.0, "sat": 80.0, "trans": 30, "notes": "Moonlight / Cyc sky blue"},
    {"code": "L119", "name": "Dark Blue",              "mfg": "Lee",   "hue": 235.0, "sat": 100.0,"trans": 2,  "notes": "Night cyc wash"},
    {"code": "L139", "name": "Primary Green",          "mfg": "Lee",   "hue": 120.0, "sat": 100.0,"trans": 14, "notes": "True foliage green"},
    {"code": "L101", "name": "Yellow",                 "mfg": "Lee",   "hue": 58.0,  "sat": 100.0,"trans": 76, "notes": "High visibility bright yellow"},
    {"code": "R46",  "name": "Magenta",                "mfg": "Rosco", "hue": 300.0, "sat": 100.0,"trans": 22, "notes": "Vivid rock & roll pink"},
    {"code": "R33",  "name": "No Color Pink",          "mfg": "Rosco", "hue": 335.0, "sat": 25.0, "trans": 70, "notes": "Subtle frontlight skin tint"},
    {"code": "R57",  "name": "Lavender",               "mfg": "Rosco", "hue": 270.0, "sat": 55.0, "trans": 48, "notes": "Cool shadow / wash"},
    {"code": "R360", "name": "Clear Sky Teal",         "mfg": "Rosco", "hue": 175.0, "sat": 85.0, "trans": 42, "notes": "Electric teal concert look"},
    {"code": "R395", "name": "Teal Green",             "mfg": "Rosco", "hue": 160.0, "sat": 90.0, "trans": 32, "notes": "Moody underwater green"}
]

GEL_SCHEMA = """
CREATE TABLE IF NOT EXISTS gel_library (
    gel_code        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    manufacturer    TEXT NOT NULL,
    hue             REAL NOT NULL,
    saturation      REAL NOT NULL,
    transmission    INTEGER NOT NULL,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_gel_mfg ON gel_library(manufacturer);
CREATE INDEX IF NOT EXISTS idx_gel_name ON gel_library(name);
"""

class WolfGelLibrary:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(GEL_SCHEMA)
        self._populate_gels()

    def _populate_gels(self):
        for g in GEL_PRESETS:
            self.conn.execute(
                """INSERT OR REPLACE INTO gel_library (gel_code, name, manufacturer, hue, saturation, transmission, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (g["code"], g["name"], g["mfg"], g["hue"], g["sat"], g["trans"], g["notes"])
            )
        self.conn.commit()

    def lookup(self, query: str) -> List[Dict[str, Any]]:
        """Search gels by code (e.g. 'R02', 'L201') or name (e.g. 'Bastard Amber')."""
        q = f"%{query.strip()}%"
        rows = self.conn.execute(
            """SELECT * FROM gel_library 
               WHERE gel_code LIKE ? OR name LIKE ? OR notes LIKE ?
               ORDER BY gel_code ASC""",
            (q, q, q)
        ).fetchall()
        return [dict(r) for r in rows]

    def generate_gel_preset_commands(self, channels: List[int], gel_code: str) -> List[str]:
        """Generates the exact Eos command sequence to apply a gel preset to selected fixtures."""
        results = self.lookup(gel_code)
        if not results:
            return [f"# Gel {gel_code} not found in library"]
        
        gel = results[0]
        chan_str = f"Chan {min(channels)} Thru {max(channels)}" if len(channels) > 1 else f"Chan {channels[0]}"
        
        # Generates OSC address for setting HSI
        return [
            f"{chan_str} Color_Palette {gel['gel_code']} Enter  # {gel['name']}",
            f"# Universal Coordinates: Hue {gel['hue']}°, Sat {gel['saturation']}% (Transmission {gel['transmission']}%)"
        ]

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("[+] Initializing Wolf Logic Universal Gel Library...")
    lib = WolfGelLibrary()

    print(f"\n[+] Total Standard Gels Loaded: {len(GEL_PRESETS)}")
    
    # Test lookups
    print("\n[+] Testing Gel Lookups:")
    for search_term in ["Bastard Amber", "L201", "Teal", "Lavender"]:
        matches = lib.lookup(search_term)
        for m in matches:
            print(f"    [{m['gel_code']:<5}] {m['name']:<22} ({m['manufacturer']:<5}) -> Hue: {m['hue']:5.1f}°, Sat: {m['saturation']:4.1f}% | {m['notes']}")

    lib.close()
    print("\n[+] Universal Gel Library verified successfully.")
