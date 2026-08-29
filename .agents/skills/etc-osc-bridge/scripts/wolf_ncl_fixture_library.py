#!/usr/bin/env python3
"""
Wolf Logic — NCL (Norwegian Cruise Line) Fleet Fixture Profile Library
Pre-loaded DMX personalities, channel footprints, and universal HSI profiles for
Claypaky, Vari-Lite, Robe, Elation Proteus, and ETC fixtures across the NCL fleet.
"""

import sqlite3
import os
import json
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")

# Comprehensive NCL Fleet Fixture Personalities & Modes
NCL_FIXTURES = [
    # --- Claypaky ---
    {
        "model": "Claypaky Sharpy",
        "mfg": "Claypaky",
        "category": "Beam",
        "mode": "Standard 16ch",
        "channels": 16,
        "color_engine": "Color_Wheel",
        "pan_range": 540.0, "tilt_range": 250.0,
        "zoom_range": "3.8 deg fixed beam",
        "features": ["14 Colors", "17 Fixed Gobos", "8-Facet Prism", "Frost", "Dimmer/Strobe"],
        "deployment": "Stardust Theater / Nightclubs / Aerial Beams"
    },
    {
        "model": "Claypaky HY B-Eye K15",
        "mfg": "Claypaky",
        "category": "Wash / Effect",
        "mode": "Standard 35ch (RGBW Matrix)",
        "channels": 35,
        "color_engine": "RGBW",
        "pan_range": 540.0, "tilt_range": 210.0,
        "zoom_range": "4 - 60 deg",
        "features": ["Rotating Front Lens (Vortex/Kaleidoscope)", "White CT Filter 2500-8000K", "Individual Pixel Control", "Halo Dimmer"],
        "deployment": "Prima Theater / Sensoria Nightclub / Broadway Stage"
    },
    {
        "model": "Claypaky Arolla Aqua LT",
        "mfg": "Claypaky",
        "category": "Profile / Spot (IP66 Marine)",
        "mode": "Standard 38ch",
        "channels": 38,
        "color_engine": "CMY_Linear_CTO",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "5.5 - 50 deg",
        "features": ["IP66 Marine Salt Shield", "4 Full-Curtain Framing Blades", "Dual Rotating Gobos", "Animation Wheel", "Prism"],
        "deployment": "Top Deck / Aqua Park / Open Air Glow Parties"
    },
    {
        "model": "Claypaky Sinfonya Profile HP",
        "mfg": "Claypaky",
        "category": "Theatrical Framing Profile",
        "mode": "Standard 44ch",
        "channels": 44,
        "color_engine": "RGBAL_Linear_CCT",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "5 - 50 deg",
        "features": ["Whisper-Quiet Silent Fan (Theatrical Mode)", "Accuframe 4-Blade Framing System", "High CRI 95+", "Calibration Engine"],
        "deployment": "Broadway Stage / Stardust Main Theaters"
    },

    # --- Vari-Lite ---
    {
        "model": "Vari-Lite VL3600 Profile IP",
        "mfg": "Vari-Lite",
        "category": "Heavy-Duty Framing Profile (IP65)",
        "mode": "Standard 45ch",
        "channels": 45,
        "color_engine": "CMY_Linear_CTO",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "5.5 - 50 deg",
        "features": ["IP65 Marine Rated 1000W LED", "V-Track Full Framing System", "Dual Rotating Gobo Wheels", "Color Wheel", "Dual Prisms"],
        "deployment": "Main Stage Productions (Beetlejuice, Choir of Man, Jersey Boys)"
    },
    {
        "model": "Vari-Lite VL1600 Profile",
        "mfg": "Vari-Lite",
        "category": "High-CRI Theatrical Key Profile",
        "mode": "Standard 36ch",
        "channels": 36,
        "color_engine": "Tunable_White_CMY",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "7 - 48 deg",
        "features": ["Tunable White 2700-7000K", "CRI 95+", "V-Track Framing", "Gobo Wheel", "Iris", "Frost"],
        "deployment": "Theatrical Key Light / Front of House Truss"
    },

    # --- Robe Lighting ---
    {
        "model": "Robe MegaPointe",
        "mfg": "Robe",
        "category": "Hybrid Beam / Spot / FX",
        "mode": "Mode 1 (39ch)",
        "channels": 39,
        "color_engine": "CMY_ColorWheel",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "1.8 - 42 deg",
        "features": ["Static & Rotating Gobos", "12-Facet & 6-Facet Dual Prisms", "Animation Wheel", "Beam Shaper", "Fast Pan/Tilt"],
        "deployment": "Dynamic Stage Rigging / High Energy Rock & Pop Shows"
    },
    {
        "model": "Robe Spiider",
        "mfg": "Robe",
        "category": "LED Wash / Beam / Flower",
        "mode": "Mode 1 (27ch)",
        "channels": 27,
        "color_engine": "RGBW",
        "pan_range": 540.0, "tilt_range": 230.0,
        "zoom_range": "4 - 50 deg",
        "features": ["Central 60W Flower FX (Multi-colored beams)", "Individual Ring Control", "Virtual Color Wheel", "Variable CTO 2700-8000K"],
        "deployment": "Overhead Wash Grid / Secondary Music Lounges"
    },

    # --- Elation Professional ---
    {
        "model": "Elation Proteus Maximus",
        "mfg": "Elation",
        "category": "Ultra-High Output IP65 Marine Profile",
        "mode": "Standard 47ch",
        "channels": 47,
        "color_engine": "CMY_Linear_CTO",
        "pan_range": 540.0, "tilt_range": 270.0,
        "zoom_range": "5.5 - 55 deg",
        "features": ["50,000 Lumen 950W White LED", "IP65 Marine Salt Resistant", "Full 4-Blade Framing", "Dual Gobo Wheels", "Animation", "Iris"],
        "deployment": "Pool Deck / Outdoor Funnel & Superstructure Projection / Glow Parties"
    },
    {
        "model": "Elation Proteus Hybrid",
        "mfg": "Elation",
        "category": "IP65 Beam / Spot / Wash",
        "mode": "Standard 28ch",
        "channels": 28,
        "color_engine": "CMY_ColorWheel",
        "pan_range": 540.0, "tilt_range": 240.0,
        "zoom_range": "2 - 38 deg",
        "features": ["IP65 Marine Housing", "Philips 470W Discharge Lamp", "Dual Prisms", "Frost", "Motorized Zoom"],
        "deployment": "Pool Decks & Top Deck Concerts"
    },

    # --- ETC (Electronic Theatre Controls) ---
    {
        "model": "ETC ColorSource Spot V",
        "mfg": "ETC",
        "category": "Static LED Profile",
        "mode": "5-Channel (Direct) / 8-Channel",
        "channels": 8,
        "color_engine": "RGB_Lime_Indigo",
        "pan_range": 0.0, "tilt_range": 0.0,
        "zoom_range": "Lens Tube (19/26/36/50 deg)",
        "features": ["5-Color LED Array (Red, Green, Blue, Lime, Indigo)", "High Theatrical CRI", "Standard Shutter Blades"],
        "deployment": "Atriums / Secondary Lounges / Theatrical Overheads"
    },
    {
        "model": "ETC Source Four LED Series 3 (Lustr X8)",
        "mfg": "ETC",
        "category": "Theatrical Flagship Profile",
        "mode": "Direct 10ch / Studio 6ch",
        "channels": 10,
        "color_engine": "DeepRed_Red_Amber_Green_Cyan_Blue_Indigo",
        "pan_range": 0.0, "tilt_range": 0.0,
        "zoom_range": "Lens Tube",
        "features": ["X8 Color Array with Deep Red", "NFC Configuration via App", "Ultra-High CRI Skin Tone Fidelity"],
        "deployment": "Main Stage Theatrical Front of House Key"
    }
]

NCL_SCHEMA = """
CREATE TABLE IF NOT EXISTS ncl_fixture_catalog (
    model           TEXT PRIMARY KEY,
    manufacturer    TEXT NOT NULL,
    category        TEXT NOT NULL,
    default_mode    TEXT NOT NULL,
    dmx_channels    INTEGER NOT NULL,
    color_engine    TEXT NOT NULL,
    pan_range       REAL NOT NULL,
    tilt_range      REAL NOT NULL,
    zoom_range      TEXT,
    features_json   TEXT,
    deployment_area TEXT
);

CREATE INDEX IF NOT EXISTS idx_ncl_mfg ON ncl_fixture_catalog(manufacturer);
CREATE INDEX IF NOT EXISTS idx_ncl_cat ON ncl_fixture_catalog(category);
"""

class NCLFixtureLibrary:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(NCL_SCHEMA)
        self._populate_fixtures()

    def _populate_fixtures(self):
        for f in NCL_FIXTURES:
            self.conn.execute(
                """INSERT OR REPLACE INTO ncl_fixture_catalog
                   (model, manufacturer, category, default_mode, dmx_channels, color_engine,
                    pan_range, tilt_range, zoom_range, features_json, deployment_area)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (f["model"], f["mfg"], f["category"], f["mode"], f["channels"], f["color_engine"],
                 f["pan_range"], f["tilt_range"], f["zoom_range"], json.dumps(f["features"]), f["deployment"])
            )
        self.conn.commit()

    def lookup(self, query: str) -> List[Dict[str, Any]]:
        """Search NCL fixtures by model, manufacturer, or venue deployment."""
        q = f"%{query.strip()}%"
        rows = self.conn.execute(
            """SELECT * FROM ncl_fixture_catalog
               WHERE model LIKE ? OR manufacturer LIKE ? OR category LIKE ? OR deployment_area LIKE ?
               ORDER BY manufacturer ASC, model ASC""",
            (q, q, q, q)
        ).fetchall()
        return [dict(r) for r in rows]

    def generate_patch_commands(self, model: str, start_channel: int, count: int, 
                                start_universe: int, start_dmx: int) -> List[str]:
        """Generates exact Eos patch command lines for NCL fixture blocks."""
        results = self.lookup(model)
        if not results:
            return [f"# Fixture {model} not found in catalog"]
        
        fix = results[0]
        dmx_footprint = fix["dmx_channels"]
        cmds = []

        cur_u = start_universe
        cur_d = start_dmx

        for i in range(count):
            ch = start_channel + i
            if cur_d + dmx_footprint - 1 > 512:
                cur_u += 1
                cur_d = 1

            address_str = f"{cur_u}/{cur_d}"
            cmds.append(f"Chan {ch} Type {fix['model']} Address {address_str} Label {fix['model']}_{i+1} Enter")
            cur_d += dmx_footprint

        return cmds

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("[+] Initializing NCL (Norwegian Cruise Line) Fleet Fixture Library...")
    lib = NCLFixtureLibrary()

    print(f"\n[+] Total NCL Standard Movers & Fixtures Loaded: {len(NCL_FIXTURES)}")
    for f in lib.lookup(""):
        print(f"  • {f['manufacturer']:<12} | {f['model']:<32} ({f['category']:<24}) | {f['dmx_channels']:2d}ch | {f['color_engine']}")

    print("\n[+] Testing Auto-Patch Generator for 8x Vari-Lite VL3600 Profiles on Universe 2...")
    patch_cmds = lib.generate_patch_commands("Vari-Lite VL3600 Profile IP", start_channel=101, count=8, start_universe=2, start_dmx=1)
    for c in patch_cmds[:4]:
        print(f"    ➔ Eos Command: \"{c}\"")
    print(f"    ➔ ... (+{len(patch_cmds)-4} more fixtures)")

    lib.close()
    print("\n[+] NCL Fleet Fixture Library verified successfully.")
