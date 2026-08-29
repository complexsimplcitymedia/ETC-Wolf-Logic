#!/usr/bin/env python3
"""
Wolf Logic — NCL Fleet Unpatched Fixture Inventory CSV Generator
Generates a clean template CSV with 10 of each NCL moving light / fixture model
without channel numbers or DMX addresses, ready for custom patch design.
"""

import csv
import os
import sys

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "csv_exports", "ncl_rig_inventory_unpatched.csv")

# 12 Major NCL Fleet Fixtures
NCL_MODELS = [
    {
        "mfg": "Claypaky",
        "model": "Claypaky Sharpy",
        "mode": "Standard 16ch",
        "footprint": 16,
        "color_engine": "Color_Wheel",
        "category": "Beam",
        "pan": "540 deg", "tilt": "250 deg",
        "venue": "Stardust Theater / Nightclubs"
    },
    {
        "mfg": "Claypaky",
        "model": "Claypaky HY B-Eye K15",
        "mode": "Standard 35ch",
        "footprint": 35,
        "color_engine": "RGBW Matrix",
        "category": "Wash / Effect",
        "pan": "540 deg", "tilt": "210 deg",
        "venue": "Prima Theater / Sensoria Nightclub"
    },
    {
        "mfg": "Claypaky",
        "model": "Claypaky Arolla Aqua LT",
        "mode": "Standard 38ch",
        "footprint": 38,
        "color_engine": "CMY + Linear CTO",
        "category": "Profile / Spot (IP66 Marine)",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Top Deck / Glow Parties / Aqua Park"
    },
    {
        "mfg": "Claypaky",
        "model": "Claypaky Sinfonya Profile HP",
        "mode": "Standard 44ch",
        "footprint": 44,
        "color_engine": "RGBAL Engine",
        "category": "Theatrical Framing Profile",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Main Stage Broadway Productions"
    },
    {
        "mfg": "Vari-Lite",
        "model": "Vari-Lite VL3600 Profile IP",
        "mode": "Standard 45ch",
        "footprint": 45,
        "color_engine": "CMY + Linear CTO",
        "category": "Heavy-Duty Framing Profile (IP65)",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Main Stage (Beetlejuice / Choir of Man)"
    },
    {
        "mfg": "Vari-Lite",
        "model": "Vari-Lite VL1600 Profile",
        "mode": "Standard 36ch",
        "footprint": 36,
        "color_engine": "Tunable White + CMY",
        "category": "Theatrical Key Profile (High CRI)",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Front of House Theatrical Key"
    },
    {
        "mfg": "Robe",
        "model": "Robe MegaPointe",
        "mode": "Mode 1 (39ch)",
        "footprint": 39,
        "color_engine": "CMY + Color Wheel",
        "category": "Hybrid Beam / Spot / FX",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Concert Stage / Rock & Pop Shows"
    },
    {
        "mfg": "Robe",
        "model": "Robe Spiider",
        "mode": "Mode 1 (27ch)",
        "footprint": 27,
        "color_engine": "RGBW + Flower FX",
        "category": "LED Wash / Beam / Flower",
        "pan": "540 deg", "tilt": "230 deg",
        "venue": "Overhead Wash Grid / Lounges"
    },
    {
        "mfg": "Elation",
        "model": "Elation Proteus Maximus",
        "mode": "Standard 47ch",
        "footprint": 47,
        "color_engine": "CMY + Linear CTO",
        "category": "Ultra-High Output IP65 Marine",
        "pan": "540 deg", "tilt": "270 deg",
        "venue": "Pool Deck / Outdoor Funnel Glow"
    },
    {
        "mfg": "Elation",
        "model": "Elation Proteus Hybrid",
        "mode": "Standard 28ch",
        "footprint": 28,
        "color_engine": "CMY + Color Wheel",
        "category": "IP65 Marine Beam / Spot",
        "pan": "540 deg", "tilt": "240 deg",
        "venue": "Top Deck Concerts & Pool Stages"
    },
    {
        "mfg": "ETC",
        "model": "ETC ColorSource Spot V",
        "mode": "Standard 8ch",
        "footprint": 8,
        "color_engine": "5-Color (RGB-Lime-Indigo)",
        "category": "Static LED Theatrical Profile",
        "pan": "Static (0 deg)", "tilt": "Static (0 deg)",
        "venue": "Atriums & Theatrical Overheads"
    },
    {
        "mfg": "ETC",
        "model": "ETC Source Four LED Series 3",
        "mode": "Direct 10ch (Lustr X8)",
        "footprint": 10,
        "color_engine": "Lustr X8 Array (7-Color)",
        "category": "Theatrical Flagship Profile",
        "pan": "Static (0 deg)", "tilt": "Static (0 deg)",
        "venue": "Main Stage Front of House Key"
    }
]

CSV_HEADERS = [
    "Fixture_Index",
    "Unit_Number",
    "Manufacturer",
    "Fixture_Type",
    "Default_Mode",
    "DMX_Channels",
    "Color_Mixing_Engine",
    "Category",
    "Pan_Range",
    "Tilt_Range",
    "Deployment_Venue",
    "Channel_Number",     # Left blank for user custom numbering
    "DMX_Universe",      # Left blank for user custom addressing
    "DMX_Address",       # Left blank for user custom addressing
    "Label_Notes"
]

def generate_csv(out_path: str = OUTPUT_FILE):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    rows = []
    global_idx = 1

    for fixture in NCL_MODELS:
        for unit in range(1, 11):  # 10 units per model
            rows.append({
                "Fixture_Index": global_idx,
                "Unit_Number": f"{unit:02d}",
                "Manufacturer": fixture["mfg"],
                "Fixture_Type": fixture["model"],
                "Default_Mode": fixture["mode"],
                "DMX_Channels": fixture["footprint"],
                "Color_Mixing_Engine": fixture["color_engine"],
                "Category": fixture["category"],
                "Pan_Range": fixture["pan"],
                "Tilt_Range": fixture["tilt"],
                "Deployment_Venue": fixture["venue"],
                "Channel_Number": "",  # Empty
                "DMX_Universe": "",   # Empty
                "DMX_Address": "",    # Empty
                "Label_Notes": f"{fixture['model']} #{unit}"
            })
            global_idx += 1

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[+] Successfully generated unpatched NCL inventory CSV:")
    print(f"    Path: {os.path.abspath(out_path)}")
    print(f"    Total Fixtures: {len(rows)} (12 models x 10 units each)")

if __name__ == "__main__":
    generate_csv()
