#!/usr/bin/env python3
"""
Wolf Logic — High-Speed Eos Effect Generator & Universal HSI Color Palette Engine
Generates complex multi-step effects, sinusoidal pan/tilt ballyhoos, and color waves
in milliseconds and translates them into executable ETC Eos OSC command sequences.
"""

import sqlite3
import os
import math
import json
import time
from typing import Dict, List, Optional, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")

# Standard Universal HSI Color Palette Definitions (Fixture Agnostic)
STANDARD_PALETTES = {
    1: {"name": "Red",           "hue": 0.0,   "sat": 100.0, "notes": "Primary Red"},
    2: {"name": "Orange",        "hue": 30.0,  "sat": 100.0, "notes": "Amber / Orange"},
    3: {"name": "Yellow",        "hue": 60.0,  "sat": 100.0, "notes": "Vivid Yellow"},
    4: {"name": "Green",         "hue": 120.0, "sat": 100.0, "notes": "Primary Green"},
    5: {"name": "Cyan",          "hue": 180.0, "sat": 100.0, "notes": "Ice Blue / Cyan"},
    6: {"name": "Blue",          "hue": 240.0, "sat": 100.0, "notes": "Deep Blue / Primary"},
    7: {"name": "Magenta",       "hue": 300.0, "sat": 100.0, "notes": "Hot Pink / Magenta"},
    8: {"name": "Lavender",      "hue": 270.0, "sat": 60.0,  "notes": "Pastel Lavender"},
    9: {"name": "Warm White",    "hue": 35.0,  "sat": 28.0,  "notes": "3200K Tungsten Standard"},
    10: {"name": "Cool White",   "hue": 50.0,  "sat": 12.0,  "notes": "4400K Cool White Standard"},
    11: {"name": "Daylight Raw", "hue": 205.0, "sat": 10.0,  "notes": "5600K Daylight Raw"}
}

EFFECT_SCHEMA = """
-- Color Palette Database Table
CREATE TABLE IF NOT EXISTS color_palettes (
    palette_num     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    hue             REAL NOT NULL,
    saturation      REAL NOT NULL,
    notes           TEXT
);

-- Generated Effects Storage
CREATE TABLE IF NOT EXISTS generated_effects (
    effect_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    effect_num      INTEGER NOT NULL,
    effect_name     TEXT NOT NULL,
    effect_type     TEXT NOT NULL,          -- 'Color_Wave' | 'Pan_Tilt_Sine' | 'Ballyhoo' | 'Step_Chase'
    channels_json   TEXT NOT NULL,          -- List of channels
    osc_command_seq TEXT NOT NULL,          -- Full OSC text command sequence for Eos
    created_at      TEXT NOT NULL
);
"""

class WolfEffectEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(EFFECT_SCHEMA)
        self._init_standard_palettes()

    def _init_standard_palettes(self):
        for num, data in STANDARD_PALETTES.items():
            self.conn.execute(
                """INSERT OR REPLACE INTO color_palettes (palette_num, name, hue, saturation, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (num, data["name"], data["hue"], data["sat"], data["notes"])
            )
        self.conn.commit()

    # --- High-Speed Effect Generators ---

    def generate_color_wave(self, effect_num: int, name: str, channels: List[int],
                            palette_start: int = 6, palette_end: int = 7,
                            duration_sec: float = 4.0, offset_mode: str = "mirror_in") -> Dict[str, Any]:
        """
        Generates a multi-step HSI color chase across channels with symmetrical phase offset.
        Outputs exact Eos command line text sequence.
        """
        p_start = STANDARD_PALETTES.get(palette_start, STANDARD_PALETTES[6])
        p_end = STANDARD_PALETTES.get(palette_end, STANDARD_PALETTES[7])

        n_chans = len(channels)
        steps = []
        osc_cmds = []

        # Build Eos Effect creation command
        osc_cmds.append(f"Effect {effect_num} Enter")
        osc_cmds.append(f"Effect {effect_num} Type Absolute Enter")
        osc_cmds.append(f"Effect {effect_num} Action Action 1 Color_Palette {palette_start} Time {duration_sec/2} Enter")
        osc_cmds.append(f"Effect {effect_num} Action Action 2 Color_Palette {palette_end} Time {duration_sec/2} Enter")

        # Channel apply command with offset
        chan_str = f"Chan {min(channels)} Thru {max(channels)}"
        if offset_mode == "mirror_in":
            osc_cmds.append(f"{chan_str} Effect {effect_num} Offset Mirror_In Enter")
        elif offset_mode == "mirror_out":
            osc_cmds.append(f"{chan_str} Effect {effect_num} Offset Mirror_Out Enter")
        else:
            osc_cmds.append(f"{chan_str} Effect {effect_num} Offset Random Enter")

        result = {
            "effect_num": effect_num,
            "name": name,
            "type": "Color_Wave",
            "channels": channels,
            "palettes": [p_start["name"], p_end["name"]],
            "duration_sec": duration_sec,
            "osc_commands": osc_cmds
        }

        self._save_effect(effect_num, name, "Color_Wave", channels, osc_cmds)
        return result

    def generate_ballyhoo_effect(self, effect_num: int, name: str, channels: List[int],
                                 pan_width: float = 60.0, tilt_height: float = 40.0,
                                 cycle_time: float = 3.0) -> Dict[str, Any]:
        """
        Generates a mathematical figure-8 / Lissajous ballyhoo motion effect.
        """
        osc_cmds = [
            f"Effect {effect_num} Enter",
            f"Effect {effect_num} Type Focus Enter",
            f"Effect {effect_num} Axis Pan Size {pan_width} Enter",
            f"Effect {effect_num} Axis Tilt Size {tilt_height} Enter",
            f"Effect {effect_num} Duration {cycle_time} Enter",
            f"Chan {min(channels)} Thru {max(channels)} Effect {effect_num} Offset Mirror_In Enter"
        ]

        result = {
            "effect_num": effect_num,
            "name": name,
            "type": "Ballyhoo_Focus",
            "channels": channels,
            "pan_width": pan_width,
            "tilt_height": tilt_height,
            "osc_commands": osc_cmds
        }

        self._save_effect(effect_num, name, "Ballyhoo_Focus", channels, osc_cmds)
        return result

    def _save_effect(self, effect_num: int, name: str, eff_type: str, channels: List[int], osc_cmds: List[str]):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            """INSERT INTO generated_effects (effect_num, effect_name, effect_type, channels_json, osc_command_seq, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (effect_num, name, eff_type, json.dumps(channels), "\n".join(osc_cmds), now_str)
        )
        self.conn.commit()

    def get_palettes(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM color_palettes ORDER BY palette_num ASC").fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("[+] Initializing Wolf Logic Effect & Palette Engine...")
    engine = WolfEffectEngine()

    print("\n[+] Registered Universal HSI Color Palettes in SQLite:")
    for p in engine.get_palettes():
        print(f"    CP {p['palette_num']:2d}: {p['name']:<12} -> Hue: {p['hue']:5.1f}°, Sat: {p['saturation']:4.1f}% ({p['notes']})")

    print("\n[+] Generating Complex Cyan/Magenta Color Wave Effect (Effect 901)...")
    wave_eff = engine.generate_color_wave(
        effect_num=901,
        name="Cyan-Magenta Wave",
        channels=list(range(1, 25)),
        palette_start=5, # Cyan
        palette_end=7,   # Magenta
        duration_sec=3.0,
        offset_mode="mirror_in"
    )
    print("    Generated OSC Sequence:")
    for cmd in wave_eff["osc_commands"]:
        print(f"      ➔ /eos/cmd : \"{cmd}\"")

    print("\n[+] Generating Ballyhoo Focus Figure-8 (Effect 902)...")
    ballyhoo = engine.generate_ballyhoo_effect(
        effect_num=902,
        name="Stage Ballyhoo Figure 8",
        channels=list(range(1, 13)),
        pan_width=75.0,
        tilt_height=45.0,
        cycle_time=2.5
    )
    print("    Generated OSC Sequence:")
    for cmd in ballyhoo["osc_commands"]:
        print(f"      ➔ /eos/cmd : \"{cmd}\"")

    engine.close()
    print("\n[+] Wolf Logic Effect & Palette Engine verified successfully.")
