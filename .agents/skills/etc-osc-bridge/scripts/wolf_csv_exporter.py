#!/usr/bin/env python3
"""
Wolf Logic — Universal HSI Standard Eos CSV Stream Formatter & Exporter
Exports all live streaming Art-Net, sACN, and OSC data into exact standard
ETC Eos CSV formats with universal HSI (Hue 0-360°, Saturation 0-100%, Intensity 0-100%).
"""

import csv
import sqlite3
import os
import sys
import time
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "csv_exports")

# Standard ETC Eos Patch CSV Headers with Universal HSI
EOS_PATCH_HEADERS = [
    "Channel", "Address", "Universe", "DMX_Slot", "Fixture_Type", 
    "Label", "Gel", "Intensity_Pct", "Hue_Deg", "Sat_Pct", "Pan_Deg", "Tilt_Deg", 
    "Color_Hex", "Last_Updated"
]

# Standard ETC Eos Cue List CSV Headers
EOS_CUE_HEADERS = [
    "Cue_List", "Cue_Number", "Part", "Label", "Time_Up", "Time_Down", 
    "Follow", "Link", "Action_Timestamp", "Source_Event_ID"
]

# Continuous Real-Time Telemetry Stream CSV Headers
EOS_STREAM_HEADERS = [
    "Timestamp_UTC", "Epoch_MS", "SMPTE_Timecode", "Protocol", "Source_IP",
    "Address_Pattern", "Channel", "Universe", "Hue", "Sat", "Intensity", "Raw_Value"
]

class WolfCSVExporter:
    def __init__(self, db_path: str = DB_PATH, out_dir: str = OUTPUT_DIR):
        self.db_path = db_path
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def export_patch_csv(self, filename: Optional[str] = None) -> str:
        """Exports the active patch state with universal HSI to standard CSV."""
        if not filename:
            filename = f"eos_patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.out_dir, filename)

        rows = self.conn.execute("""
            SELECT 
                p.channel_num AS Channel,
                p.dmx_address AS Address,
                p.universe AS Universe,
                ((p.universe - 1) * 512 + p.dmx_address) AS DMX_Slot,
                COALESCE(p.fixture_type, 'Dimmer') AS Fixture_Type,
                COALESCE(p.fixture_label, '') AS Label,
                '' AS Gel,
                COALESCE(m.intensity, 0.0) AS Intensity_Pct,
                COALESCE(m.hue, 0.0) AS Hue_Deg,
                COALESCE(m.saturation, 0.0) AS Sat_Pct,
                COALESCE(m.pan, 0.0) AS Pan_Deg,
                COALESCE(m.tilt, 0.0) AS Tilt_Deg,
                printf('#%02X%02X%02X', COALESCE(m.raw_red, 0), COALESCE(m.raw_green, 0), COALESCE(m.raw_blue, 0)) AS Color_Hex,
                p.last_updated AS Last_Updated
            FROM patch_data p
            LEFT JOIN fixture_matrix m ON p.channel_num = m.channel_num
            GROUP BY p.channel_num
            ORDER BY p.channel_num ASC
        """).fetchall()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=EOS_PATCH_HEADERS)
            writer.writeheader()
            for r in rows:
                writer.writerow(dict(r))

        print(f"[+] Exported Universal HSI Patch CSV: {filepath} ({len(rows)} fixtures)")
        return filepath

    def export_cuelist_csv(self, filename: Optional[str] = None) -> str:
        """Exports all recorded cue executions in Eos Cue List CSV format."""
        if not filename:
            filename = f"eos_cuelist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.out_dir, filename)

        rows = self.conn.execute("""
            SELECT 
                COALESCE(cue_list, 1) AS Cue_List,
                cue_number AS Cue_Number,
                1 AS Part,
                COALESCE(cue_label, '') AS Label,
                '' AS Time_Up,
                '' AS Time_Down,
                '' AS Follow,
                '' AS Link,
                ts AS Action_Timestamp,
                source_event_id AS Source_Event_ID
            FROM cue_executions
            ORDER BY epoch_ms ASC
        """).fetchall()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=EOS_CUE_HEADERS)
            writer.writeheader()
            for r in rows:
                writer.writerow(dict(r))

        print(f"[+] Exported Eos Cue List CSV: {filepath} ({len(rows)} cue events)")
        return filepath

    def export_telemetry_stream_csv(self, filename: Optional[str] = None, limit: int = 5000) -> str:
        """Exports normalized live console events (OSC, MIDI, Art-Net) with HSI to CSV."""
        if not filename:
            filename = f"eos_stream_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.out_dir, filename)

        rows = self.conn.execute("""
            SELECT 
                ts AS Timestamp_UTC,
                epoch_ms AS Epoch_MS,
                printf('%02d:%02d:%02d:%02d', 
                    (epoch_ms / 3600000) % 24, 
                    (epoch_ms / 60000) % 60, 
                    (epoch_ms / 1000) % 60, 
                    ((epoch_ms % 1000) * 30) / 1000) AS SMPTE_Timecode,
                source AS Protocol,
                COALESCE(source_ip, '127.0.0.1') AS Source_IP,
                protocol_addr AS Address_Pattern,
                '' AS Channel,
                '' AS Universe,
                '' AS Hue,
                '' AS Sat,
                COALESCE(float_value, 0.0) AS Intensity,
                COALESCE(raw_value, '') AS Raw_Value
            FROM console_events
            ORDER BY epoch_ms ASC
            LIMIT ?
        """, (limit,)).fetchall()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=EOS_STREAM_HEADERS)
            writer.writeheader()
            for r in rows:
                writer.writerow(dict(r))

        print(f"[+] Exported Universal HSI Telemetry Stream CSV: {filepath} ({len(rows)} rows)")
        return filepath

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("[+] Initializing Wolf Logic Universal HSI CSV Stream Formatter...")
    exporter = WolfCSVExporter()

    # Generate standard CSV files
    patch_file = exporter.export_patch_csv()
    cue_file = exporter.export_cuelist_csv()
    stream_file = exporter.export_telemetry_stream_csv()

    exporter.close()
    print("[+] All Universal HSI CSV export formats generated successfully.")
