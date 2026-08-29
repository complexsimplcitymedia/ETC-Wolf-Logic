#!/usr/bin/env python3
"""
Wolf Logic — Augment3d 3D Coordinate & Magic Sheet Template Generator
Maps the venue layout (Midstage Electric, Proscenium Wash, LED Columns, House Grid, FOH)
into exact Augment3d 3D XYZ spatial coordinates and Eos Magic Sheet layout.
"""

import csv
import os
import json
from typing import List, Dict

AUGMENT3D_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "csv_exports", "eos_augment3d_rig_coordinates.csv")

# Standard Augment3d CSV Import Columns
AUGMENT3D_HEADERS = [
    "Channel", "Fixture_Type", "Position_X_meters", "Position_Y_meters", "Position_Z_meters",
    "Rotation_X_deg", "Rotation_Y_deg", "Rotation_Z_deg", "Location_Zone", "Notes"
]

def generate_augment3d_coordinates(out_path: str = AUGMENT3D_CSV_PATH):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []

    # 1. Midstage Electric (10 Moving Heads / Spots across Midstage Truss)
    # Z = 6.5m overhead, Y = +3.5m (upstage), X from -4.5m to +4.5m
    for i in range(1, 11):
        x_pos = round(-4.5 + (i - 1) * 1.0, 2)
        rows.append({
            "Channel": f"1{i:02d}", # Ch 101-110
            "Fixture_Type": "Vari-Lite VL3600 Profile IP",
            "Position_X_meters": x_pos,
            "Position_Y_meters": 3.5,
            "Position_Z_meters": 6.5,
            "Rotation_X_deg": 0.0,
            "Rotation_Y_deg": 0.0,
            "Rotation_Z_deg": 0.0,
            "Location_Zone": "Midstage Electric Pipe",
            "Notes": f"Midstage Spot #{i}"
        })

    # 2. Proscenium Front Wash (8 Fixtures along Downstage Edge)
    # Z = 0.5m / 6.0m FOH angle, Y = 0.0m, X = -4.5m to -1.5m and +1.5m to +4.5m
    proscenium_x = [-4.5, -3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 4.5]
    for idx, x_pos in enumerate(proscenium_x, 1):
        rows.append({
            "Channel": f"2{idx:02d}", # Ch 201-208
            "Fixture_Type": "Claypaky HY B-Eye K15",
            "Position_X_meters": x_pos,
            "Position_Y_meters": 0.0,
            "Position_Z_meters": 5.5,
            "Rotation_X_deg": 45.0, # Angled downstage
            "Rotation_Y_deg": 0.0,
            "Rotation_Z_deg": 0.0,
            "Location_Zone": "Proscenium Front Wash",
            "Notes": f"Front Wash #{idx}"
        })

    # 3. Stage Left & Stage Right LED Columns / Towers
    # SR: X = -5.5m, Y = 2.0m | SL: X = +5.5m, Y = 2.0m
    for side, x_col, side_name in [("SR", -5.5, "Stage Right"), ("SL", 5.5, "Stage Left")]:
        for panel in range(1, 5):
            ch_num = 300 + (10 if side == "SR" else 20) + panel
            rows.append({
                "Channel": str(ch_num),
                "Fixture_Type": "ETC ColorSource Spot V",
                "Position_X_meters": x_col,
                "Position_Y_meters": 2.0,
                "Position_Z_meters": round(1.0 + (panel - 1) * 1.2, 2),
                "Rotation_X_deg": 0.0,
                "Rotation_Y_deg": 0.0,
                "Rotation_Z_deg": -90.0 if side == "SR" else 90.0,
                "Location_Zone": f"LED Column {side_name}",
                "Notes": f"Column {side} Panel #{panel}"
            })

    # 4. Audience Seating & Overhead House Grid (4x4 Grid = 16 fixtures + 3 Centerline)
    # Grid X: -4.5m, -1.5m, +1.5m, +4.5m | Grid Y: -3.0m, -6.0m, -9.0m, -12.0m | Z = 7.0m
    grid_x_coords = [-4.5, -1.5, 1.5, 4.5]
    grid_y_coords = [-3.0, -6.0, -9.0, -12.0]

    house_idx = 1
    for y_pos in grid_y_coords:
        for x_pos in grid_x_coords:
            rows.append({
                "Channel": f"4{house_idx:02d}", # Ch 401-416
                "Fixture_Type": "Claypaky Sharpy",
                "Position_X_meters": x_pos,
                "Position_Y_meters": y_pos,
                "Position_Z_meters": 7.0,
                "Rotation_X_deg": 0.0,
                "Rotation_Y_deg": 0.0,
                "Rotation_Z_deg": 0.0,
                "Location_Zone": "Audience Overhead Grid",
                "Notes": f"House Grid #{house_idx} (X:{x_pos}, Y:{y_pos})"
            })
            house_idx += 1

    # 5. Centerline Audience Specials (3 Center Fixtures)
    centerline_y = [-4.5, -7.5, -10.5]
    for c_idx, y_pos in enumerate(centerline_y, 1):
        rows.append({
            "Channel": f"5{c_idx:02d}", # Ch 501-503
            "Fixture_Type": "Robe MegaPointe",
            "Position_X_meters": 0.0,
            "Position_Y_meters": y_pos,
            "Position_Z_meters": 7.2,
            "Rotation_X_deg": 0.0,
            "Rotation_Y_deg": 0.0,
            "Rotation_Z_deg": 0.0,
            "Location_Zone": "Audience Centerline Spine",
            "Notes": f"Center Special #{c_idx}"
        })

    # Write Augment3d CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=AUGMENT3D_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[+] Generated Augment3d 3D Stage Coordinates CSV:")
    print(f"    Path: {os.path.abspath(out_path)}")
    print(f"    Total Modeled 3D Fixtures: {len(rows)}")

if __name__ == "__main__":
    generate_augment3d_coordinates()
