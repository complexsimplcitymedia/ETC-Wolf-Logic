#!/usr/bin/env python3
"""
Wolf Logic — Eos Color Palette & Gel Preset Showfile Builder
Sends OSC command lines directly to ETC Eos to program standard Color Palettes
(CP 1-11 Core Colors & CP 101-114 Standard Gel Library) with clean labels into the active showfile.
"""

import socket
import struct
import time
import argparse
from typing import List, Dict

EOS_TARGET_IP = "10.0.0.247"
EOS_PORT = 8000

# Universal Core Color Palettes
CORE_PALETTES = [
    {"cp": 1,  "name": "Red",           "hue": 0.0,   "sat": 100.0},
    {"cp": 2,  "name": "Orange",        "hue": 30.0,  "sat": 100.0},
    {"cp": 3,  "name": "Yellow",        "hue": 60.0,  "sat": 100.0},
    {"cp": 4,  "name": "Green",         "hue": 120.0, "sat": 100.0},
    {"cp": 5,  "name": "Cyan",          "hue": 180.0, "sat": 100.0},
    {"cp": 6,  "name": "Blue",          "hue": 240.0, "sat": 100.0},
    {"cp": 7,  "name": "Magenta",       "hue": 300.0, "sat": 100.0},
    {"cp": 8,  "name": "Lavender",      "hue": 270.0, "sat": 60.0},
    {"cp": 9,  "name": "Warm White",    "hue": 35.0,  "sat": 28.0},  # 3200K Tungsten
    {"cp": 10, "name": "Cool White",    "hue": 50.0,  "sat": 12.0},  # 4400K Neutral
    {"cp": 11, "name": "Daylight Raw",  "hue": 205.0, "sat": 10.0}   # 5600K Daylight
]

# Standard Gel Library Palettes (CP 101+)
GEL_PALETTES = [
    {"cp": 101, "name": "R02 Bastard Amber",     "hue": 35.0,  "sat": 30.0},
    {"cp": 102, "name": "R04 Med Bastard Amber", "hue": 34.0,  "sat": 38.0},
    {"cp": 103, "name": "L152 Pale Gold",         "hue": 40.0,  "sat": 35.0},
    {"cp": 104, "name": "L201 Full CTB 5600K",    "hue": 208.0, "sat": 38.0},
    {"cp": 105, "name": "L202 Half CTB 4400K",    "hue": 208.0, "sat": 20.0},
    {"cp": 106, "name": "L204 Full CTO 3200K",    "hue": 35.0,  "sat": 58.0},
    {"cp": 107, "name": "R26 Light Red",          "hue": 0.0,   "sat": 100.0},
    {"cp": 108, "name": "R80 Primary Blue",       "hue": 240.0, "sat": 100.0},
    {"cp": 109, "name": "R68 Parry Sky Blue",     "hue": 200.0, "sat": 80.0},
    {"cp": 110, "name": "L139 Primary Green",     "hue": 120.0, "sat": 100.0},
    {"cp": 111, "name": "R46 Magenta",            "hue": 300.0, "sat": 100.0},
    {"cp": 112, "name": "R33 No Color Pink",      "hue": 335.0, "sat": 25.0},
    {"cp": 113, "name": "R57 Lavender",           "hue": 270.0, "sat": 55.0},
    {"cp": 114, "name": "R360 Clear Sky Teal",    "hue": 175.0, "sat": 85.0}
]

def encode_osc_string(s: str) -> bytes:
    b = s.encode('utf-8') + b'\x00'
    pad = (4 - (len(b) % 4)) % 4
    return b + (b'\x00' * pad)

def build_osc_cmd(command_text: str) -> bytes:
    """Builds an /eos/cmd OSC message with string argument."""
    msg = encode_osc_string("/eos/cmd")
    msg += encode_osc_string(",s")
    msg += encode_osc_string(command_text)
    return msg

def send_osc(sock: socket.socket, target_ip: str, port: int, cmd_text: str, delay: float = 0.08):
    pkt = build_osc_cmd(cmd_text)
    sock.sendto(pkt, (target_ip, port))
    print(f"  ➔ /eos/cmd : \"{cmd_text}\"")
    time.sleep(delay)

def build_palettes(target_ip: str = EOS_TARGET_IP, port: int = EOS_PORT, chan_range: str = "Group 1"):
    print(f"[+] Connecting to Eos at {target_ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    all_palettes = CORE_PALETTES + GEL_PALETTES
    print(f"[+] Programming {len(all_palettes)} Standard Color Palettes into Eos showfile...")

    # Clear command line first
    send_osc(sock, target_ip, port, "Clear_Cmd Enter", delay=0.1)

    for p in all_palettes:
        cp_num = p["cp"]
        name = p["name"]
        hue = p["hue"]
        sat = p["sat"]

        # Eos Command Sequence to set Hue/Sat and Record Color Palette with Label
        # 1. Select group/fixtures, set Hue and Saturation
        send_osc(sock, target_ip, port, f"{chan_range} Hue {hue} Saturation {sat} Enter")
        # 2. Record Color Palette and Label it
        send_osc(sock, target_ip, port, f"Record Color_Palette {cp_num} Label {name} Enter")

    # Clear command line when done
    send_osc(sock, target_ip, port, "Clear_Cmd Enter", delay=0.1)
    sock.close()
    print(f"\n[+] Successfully programmed {len(all_palettes)} Color Palettes into Eos Master Showfile!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Program Standard Color Palettes & Gels into Eos Showfile")
    parser.add_argument("--ip", default=EOS_TARGET_IP, help=f"Eos IP address (default: {EOS_TARGET_IP})")
    parser.add_argument("--port", type=int, default=EOS_PORT, help="Eos OSC RX Port (default: 8000)")
    parser.add_argument("--group", default="Group 1", help="Fixture group or channel selection (default: 'Group 1' or 'Chan 1 Thru 50')")

    args = parser.parse_args()
    build_palettes(args.ip, args.port, args.group)
