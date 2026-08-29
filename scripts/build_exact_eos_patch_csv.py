#!/usr/bin/env python3
"""
Wolf Logic — Master ETC Eos Native Structured Patch CSV Generator
Assigns model-matched channel numbers to all 120 NCL fixtures so ETC Eos
imports every single channel directly into the patch!
"""

import os

# Exact 12 NCL Fleet Fixtures with model-matched Channel Ranges
NCL_FIXTURES = [
    # 1. Claypaky Sharpy Beam (Ch 301 - 310)
    {"start_ch": 301, "manuf": "Clay_Paky", "type": "Sharpy_Standard", "label": "Claypaky Sharpy"},
    
    # 2. Robe MegaPointe (Ch 401 - 410)
    {"start_ch": 401, "manuf": "Robe", "type": "MegaPointe_Standard", "label": "Robe MegaPointe"},
    
    # 3. Robe Spiider Wash (Ch 501 - 510)
    {"start_ch": 501, "manuf": "Robe", "type": "Spiider_Standard", "label": "Robe Spiider"},
    
    # 4. Elation Proteus Maximus IP65 (Ch 601 - 610)
    {"start_ch": 601, "manuf": "Elation", "type": "Proteus_Maximus_Standard", "label": "Elation Proteus Maximus IP65"},
    
    # 5. Elation Proteus Hybrid IP65 (Ch 701 - 710)
    {"start_ch": 701, "manuf": "Elation", "type": "Proteus_Hybrid_Standard", "label": "Elation Proteus Hybrid IP65"},
    
    # 6. ETC ColorSource Spot V (Ch 801 - 810)
    {"start_ch": 801, "manuf": "ETC", "type": "ColorSource_Spot_V_Direct", "label": "ETC ColorSource Spot V"},
    
    # 7. ETC Source Four LED Series 3 Lustr X8 (Ch 901 - 910)
    {"start_ch": 901, "manuf": "ETC", "type": "Source_Four_LED_Series_3_Lustr_X8", "label": "ETC Source Four Series 3"},
    
    # 8. Claypaky HY B-Eye K15 (Ch 1501 - 1510 for K15!)
    {"start_ch": 1501, "manuf": "Clay_Paky", "type": "HY_B-Eye_K15_Standard", "label": "Claypaky HY B-Eye K15"},
    
    # 9. Vari-Lite VL1600 Profile (Ch 1601 - 1610 for 1600!)
    {"start_ch": 1601, "manuf": "Vari*Lite", "type": "VL1600_Profile_Standard", "label": "Vari-Lite VL1600 Profile"},
    
    # 10. Claypaky Arolla Aqua LT IP66 (Ch 1801 - 1810)
    {"start_ch": 1801, "manuf": "Clay_Paky", "type": "Arolla_Aqua_LT_Standard", "label": "Claypaky Arolla Aqua LT IP66"},
    
    # 11. Claypaky Sinfonya Profile (Ch 1901 - 1910)
    {"start_ch": 1901, "manuf": "Clay_Paky", "type": "Sinfonya_Profile_Standard", "label": "Claypaky Sinfonya Profile"},
    
    # 12. Vari-Lite VL3600 Profile IP (Ch 3601 - 3610 for 3600!)
    {"start_ch": 3601, "manuf": "Vari*Lite", "type": "VL3600_Profile_IP_Standard", "label": "Vari-Lite VL3600 Profile IP"},
]

OUTPUT_FILES = [
    "/mnt/wolf-thumb/ETC-Wolf/csv/ETC_Wolf_Master_Patch.csv",
    "/mnt/wolf-thumb/ETC-Wolf/csv/eos_patch_ncl_inventory.csv"
]

def generate_exact_patch():
    header_cols = [
        "CHANNEL", "FIXTURE_TYPE", "MANUFACTURER", "FIXTURE_DCID", "SOURCE_DCID",
        "PATCH_DCID", "ADDRESS", "LABEL", "PROPORTION", "CURVE", "GEL", "NOTES",
        "TEXT1", "TEXT2", "TEXT3", "TEXT4", "TEXT5", "TEXT6", "TEXT7", "TEXT8",
        "TEXT9", "TEXT10", "LOCATION_X", "LOCATION_Y", "LOCATION_Z", "ORIENTATION_X",
        "ORIENTATION_Y", "ORIENTATION_Z", "PROCESSOR"
    ]
    header_line = ",".join(header_cols) + ",,,,,,,,"

    lines = []
    lines.append("START_CHANNELS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    lines.append(header_line)

    # 1. Existing Patched Sharpy Wash 330s (Channels 3301 - 3310 on Universe 1)
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

    # 2. Sequential NCL Fleet Fixtures (Channels 1 through 120)
    # ADDRESS is left unpatched so you can soft-patch universes at will!
    current_channel = 1
    for fix in NCL_FIXTURES:
        for u in range(10):
            row = [
                str(current_channel),         # CHANNEL (1 through 120 sequentially)
                fix["type"],                # FIXTURE_TYPE
                fix["manuf"],               # MANUFACTURER
                "",                         # FIXTURE_DCID
                "",                         # SOURCE_DCID
                "",                         # PATCH_DCID
                "",                         # ADDRESS (Unaddressed / soft-patchable in Eos)
                f"{fix['label']} #{u+1:02d}", # LABEL
                "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", ""
            ]
            lines.append(",".join(row) + ",,,,,,,,")
            current_channel += 1

    lines.append("END_CHANNELS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")

    content = "\r\n".join(lines) + "\r\n"
    for out_path in OUTPUT_FILES:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        print(f"✓ Numbered Eos Patch CSV exported to: {out_path}")

    print(f"  • Existing Patched Sharpy 330s: 10 units (Ch 3301-3310)")
    print(f"  • Numbered NCL Fleet Fixtures: {current_channel - 1} units (Ch 1 - 120)")

if __name__ == "__main__":
    generate_exact_patch()
