#!/usr/bin/env python3
"""
Wolf Logic — Master ETC Eos Native Structured Patch CSV Generator
Replicates the exact table format, block delimiters (START_CHANNELS / END_CHANNELS),
and column headers exported directly by ETC Eos from the master showfile 'ETC Wolf'.
"""

import csv
import os

# Exact 12 NCL Fleet Fixtures (10 units each = 120 fixtures)
NCL_FIXTURES = [
    {"manuf": "Clay_Paky", "type": "Sharpy_Standard", "label": "Claypaky Sharpy"},
    {"manuf": "Clay_Paky", "type": "HY_B-Eye_K15_Standard", "label": "Claypaky HY B-Eye K15"},
    {"manuf": "Clay_Paky", "type": "Arolla_Aqua_LT_Standard", "label": "Claypaky Arolla Aqua LT IP66"},
    {"manuf": "Clay_Paky", "type": "Sinfonya_Profile_Standard", "label": "Claypaky Sinfonya Profile"},
    {"manuf": "Vari*Lite", "type": "VL3600_Profile_IP_Standard", "label": "Vari-Lite VL3600 Profile IP"},
    {"manuf": "Vari*Lite", "type": "VL1600_Profile_Standard", "label": "Vari-Lite VL1600 Profile"},
    {"manuf": "Robe", "type": "MegaPointe_Standard", "label": "Robe MegaPointe"},
    {"manuf": "Robe", "type": "Spiider_Standard", "label": "Robe Spiider"},
    {"manuf": "Elation", "type": "Proteus_Maximus_Standard", "label": "Elation Proteus Maximus IP65"},
    {"manuf": "Elation", "type": "Proteus_Hybrid_Standard", "label": "Elation Proteus Hybrid IP65"},
    {"manuf": "ETC", "type": "ColorSource_Spot_V_Direct", "label": "ETC ColorSource Spot V"},
    {"manuf": "ETC", "type": "Source_Four_LED_Series_3_Lustr_X8", "label": "ETC Source Four LED Series 3"},
]

OUTPUT_FILE = "/mnt/wolf-thumb/ETC-Wolf/csv/ETC_Wolf_Master_Patch.csv"

def generate_exact_patch():
    # Exact header from ETC_Wolf.csv line 51
    header_cols = [
        "CHANNEL", "FIXTURE_TYPE", "MANUFACTURER", "FIXTURE_DCID", "SOURCE_DCID",
        "PATCH_DCID", "ADDRESS", "LABEL", "PROPORTION", "CURVE", "GEL", "NOTES",
        "TEXT1", "TEXT2", "TEXT3", "TEXT4", "TEXT5", "TEXT6", "TEXT7", "TEXT8",
        "TEXT9", "TEXT10", "LOCATION_X", "LOCATION_Y", "LOCATION_Z", "ORIENTATION_X",
        "ORIENTATION_Y", "ORIENTATION_Z", "PROCESSOR"
    ]
    # In ETC_Wolf.csv, header line ends with 8 trailing commas
    header_line = ",".join(header_cols) + ",,,,,,,,"

    lines = []
    lines.append("START_CHANNELS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    lines.append(header_line)

    # 1. Preserve your 10 existing patched Sharpy Wash 330s (Channels 3301 - 3310)
    for i in range(1, 11):
        ch = 3300 + i
        addr_start = 1 + ((i - 1) * 18)
        addr_end = addr_start + 17
        addr_str = f" 1/{addr_start}<{addr_end}"
        row = [
            str(ch),
            "Sharpy_Wash_330_Standard",
            "Clay_Paky",
            "A3333B09-1B9A-D846-81D7-558512BFCA3F",
            "",
            "",
            addr_str,
            f"Sharpy Wash 330 #{i}",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", ""
        ]
        lines.append(",".join(row) + ",,,,,,,,")

    # 2. Add 120 Unpatched NCL Fleet Fixtures (10 of each model)
    # Channel and Address are left 100% BLANK as requested!
    unit_total = 0
    for fix in NCL_FIXTURES:
        for u in range(1, 11):
            unit_total += 1
            row = [
                "",                         # CHANNEL (Blank for custom user assignment)
                fix["type"],                # FIXTURE_TYPE matching Eos library
                fix["manuf"],               # MANUFACTURER matching Eos library
                "",                         # FIXTURE_DCID
                "",                         # SOURCE_DCID
                "",                         # PATCH_DCID
                "",                         # ADDRESS (Blank for custom user assignment)
                f"{fix['label']} #{u:02d}", # LABEL
                "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", ""
            ]
            lines.append(",".join(row) + ",,,,,,,,")

    lines.append("END_CHANNELS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print(f"✓ Master ETC Eos Patch CSV created with exact table format at: {OUTPUT_FILE}")
    print(f"  • Existing Patched Sharpy 330s: 10 units (Ch 3301-3310)")
    print(f"  • Unpatched NCL Fleet Fixtures: {unit_total} units (Blank Channel & Blank DMX)")

if __name__ == "__main__":
    generate_exact_patch()
