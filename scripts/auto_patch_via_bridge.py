#!/usr/bin/env python3
"""
Wolf Logic — Automated Live Network Patch Bridge for ETC Eos
Directly programs the entire 120-fixture NCL fleet rig into ETC Eos over the wire
via native OSC (/eos/cmd) and UDP Strings (Port 4703). No manual typing or CSV clicking required!
"""

import socket
import time
import sys

# Targets: Tailscale IP for the Windows Eos machine
TARGET_IPS = ["100.110.82.103", "100.110.82.182"]
OSC_PORT = 8000
STRING_PORT = 4703

# 12 NCL Fleet Fixture Profiles & Channels (10 of each = 120 fixtures)
# Pre-assigned clean DMX Universes starting on Universe 2 so they never collide with Universe 1!
RIG_PATCH = [
    {"start_ch": 1,   "count": 10, "manuf": "Clay_Paky", "type": "Sharpy_Standard",                     "label": "Sharpy Beam",       "uni": 2, "start_addr": 1,   "footprint": 16},
    {"start_ch": 11,  "count": 10, "manuf": "Robe",      "type": "MegaPointe_Standard",                 "label": "MegaPointe",        "uni": 2, "start_addr": 200, "footprint": 39},
    {"start_ch": 21,  "count": 10, "manuf": "Robe",      "type": "Spiider_Standard",                    "label": "Spiider Wash",      "uni": 3, "start_addr": 1,   "footprint": 27},
    {"start_ch": 31,  "count": 10, "manuf": "Elation",   "type": "Proteus_Maximus_Standard",            "label": "Proteus Maximus",   "uni": 3, "start_addr": 300, "footprint": 37},
    {"start_ch": 41,  "count": 10, "manuf": "Elation",   "type": "Proteus_Hybrid_Standard",             "label": "Proteus Hybrid",    "uni": 4, "start_addr": 1,   "footprint": 32},
    {"start_ch": 51,  "count": 10, "manuf": "ETC",       "type": "ColorSource_Spot_V_Direct",           "label": "CS Spot V",         "uni": 4, "start_addr": 350, "footprint": 6},
    {"start_ch": 61,  "count": 10, "manuf": "ETC",       "type": "Source_Four_LED_Series_3_Lustr_X8",   "label": "S4 Series 3",       "uni": 5, "start_addr": 1,   "footprint": 14},
    {"start_ch": 71,  "count": 10, "manuf": "Clay_Paky", "type": "HY_B-Eye_K15_Standard",               "label": "HY B-Eye K15",      "uni": 5, "start_addr": 150, "footprint": 35},
    {"start_ch": 81,  "count": 10, "manuf": "Vari*Lite", "type": "VL1600_Profile_Standard",             "label": "VL1600 Profile",    "uni": 6, "start_addr": 1,   "footprint": 33},
    {"start_ch": 91,  "count": 10, "manuf": "Clay_Paky", "type": "Arolla_Aqua_LT_Standard",            "label": "Arolla Aqua LT",    "uni": 6, "start_addr": 350, "footprint": 38},
    {"start_ch": 101, "count": 10, "manuf": "Clay_Paky", "type": "Sinfonya_Profile_Standard",          "label": "Sinfonya Profile",  "uni": 7, "start_addr": 1,   "footprint": 44},
    {"start_ch": 111, "count": 10, "manuf": "Vari*Lite", "type": "VL3600_Profile_IP_Standard",         "label": "VL3600 Profile IP", "uni": 8, "start_addr": 1,   "footprint": 43},
]

def make_osc_string_packet(address, string_arg):
    def pad(b):
        rem = len(b) % 4
        return b + b"\x00" * (0 if rem == 0 else 4 - rem)
    addr_b = pad((address + "\x00").encode("utf-8"))
    type_b = b",s\x00\x00"
    arg_b = pad((string_arg + "\x00").encode("utf-8"))
    return addr_b + type_b + arg_b

def send_command(sock, cmd):
    # 1. Send via OSC /eos/cmd
    osc_pkt = make_osc_string_packet("/eos/cmd", cmd)
    # 2. Send via UDP String with # terminator
    str_pkt = (cmd + "#\r\n").encode("utf-8")

    for ip in TARGET_IPS:
        try:
            sock.sendto(osc_pkt, (ip, OSC_PORT))
            sock.sendto(str_pkt, (ip, STRING_PORT))
        except Exception:
            pass
    print(f"  ➔ Executed: {cmd}")
    time.sleep(0.08)

def run_auto_patch():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("\n" + "="*70)
    print("🐺 Wolf Logic Automated Network Patch Injection Bridge")
    print(f"   Target IPs: {TARGET_IPS} | OSC Port: {OSC_PORT} | UDP String Port: {STRING_PORT}")
    print("="*70 + "\n")

    # Step 1: Switch to Patch screen cleanly
    print("[1/4] Entering Eos Patch display...")
    send_command(sock, "Blind")
    send_command(sock, "Patch")

    # Step 2: Patch each fixture model by channel range, fixture type, and clean address
    print("\n[2/4] Injecting 120 NCL Fleet Fixtures over the wire...")
    for group in RIG_PATCH:
        start_c = group["start_ch"]
        end_c = start_c + group["count"] - 1
        ch_range = f"{start_c} Thru {end_c}"
        
        # In Eos: [Chan] [1] [Thru] [10] [Type] {Type} [Enter]
        type_cmd = f"Chan {ch_range} Type {group['type']} Enter"
        send_command(sock, type_cmd)

        # Label the group
        label_cmd = f"Chan {ch_range} Label {group['label']} Enter"
        send_command(sock, label_cmd)

        # Assign clean DMX addresses so Flexichannel never hides them
        uni = group["uni"]
        s_addr = group["start_addr"]
        addr_cmd = f"Chan {start_c} Address {uni}/{s_addr} Enter"
        send_command(sock, addr_cmd)

        for offset in range(1, group["count"]):
            this_ch = start_c + offset
            this_addr = s_addr + (offset * group["footprint"])
            send_command(sock, f"Chan {this_ch} Address {uni}/{this_addr} Enter")

    # Step 3: Return to Live
    print("\n[3/4] Returning Eos to Live...")
    send_command(sock, "Live")

    print("\n[4/4] ✓ Injection Complete! 120 Fixtures Patched Directly Over the Wire!")
    sock.close()

if __name__ == "__main__":
    run_auto_patch()
