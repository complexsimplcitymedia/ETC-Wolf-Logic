#!/usr/bin/env python3
"""
Real-Time ETC Eos Transmit Monitor Daemon
Listens continuously for relayed Eos OSC transmission packets, logs live console events,
and maintains a live JSON state file for IDE backend integration.
"""

import socket
import struct
import json
import os
import sys
import time
import argparse
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "live_eos_state.json")

def parse_osc_string(data: bytes, offset: int = 0) -> tuple:
    """Parses a null-terminated 4-byte aligned OSC string."""
    null_idx = data.find(b'\x00', offset)
    if null_idx == -1:
        return "", len(data)
    s = data[offset:null_idx].decode('utf-8', errors='ignore')
    next_offset = null_idx + 1
    pad = (4 - (next_offset % 4)) % 4
    next_offset += pad
    return s, next_offset

def parse_osc_packet(data: bytes) -> tuple:
    """Parses an OSC address and its arguments (strings, ints, floats)."""
    if not data or not data.startswith(b'/'):
        return None, []

    address, offset = parse_osc_string(data, 0)
    if offset >= len(data) or data[offset:offset+1] != b',':
        return address, []

    type_tags, offset = parse_osc_string(data, offset)
    args = []

    for tag in type_tags[1:]:  # Skip leading ','
        if tag == 's':
            s_val, offset = parse_osc_string(data, offset)
            args.append(s_val)
        elif tag == 'f':
            if offset + 4 <= len(data):
                f_val = struct.unpack(">f", data[offset:offset+4])[0]
                args.append(round(f_val, 2))
                offset += 4
        elif tag == 'i':
            if offset + 4 <= len(data):
                i_val = struct.unpack(">i", data[offset:offset+4])[0]
                args.append(i_val)
                offset += 4

    return address, args

class EosLiveState:
    def __init__(self):
        self.state = {
            "last_updated": "",
            "active_cue": "None",
            "pending_cue": "None",
            "command_line": "",
            "active_channels": {},
            "submasters": {},
            "recent_events": []
        }

    def update(self, address: str, args: list):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state["last_updated"] = now_str

        event_str = f"[{now_str}] {address}"
        if args:
            event_str += f" -> {args}"

        # Maintain 20 recent events
        self.state["recent_events"].insert(0, event_str)
        self.state["recent_events"] = self.state["recent_events"][:20]

        # Parse specific Eos telemetry
        if "/eos/out/active/cue" in address:
            self.state["active_cue"] = " ".join(map(str, args)) if args else address
        elif "/eos/out/pending/cue" in address:
            self.state["pending_cue"] = " ".join(map(str, args)) if args else address
        elif "/eos/out/cmd" in address:
            self.state["command_line"] = str(args[0]) if args else ""
        elif "/eos/out/param" in address or "/eos/out/chan" in address:
            parts = address.split("/")
            if len(parts) >= 5 and parts[3].isdigit():
                ch = parts[3]
                val = args[0] if args else 0
                self.state["active_channels"][ch] = val
        elif "/eos/out/sub" in address:
            parts = address.split("/")
            if len(parts) >= 5 and parts[4].isdigit():
                sub = parts[4]
                val = args[0] if args else 0
                self.state["submasters"][sub] = val

        self.save()

    def save(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            pass

def main():
    parser = argparse.ArgumentParser(description="Real-Time ETC Eos Transmit Monitor Daemon")
    parser.add_argument("--port", type=int, default=9000, help="UDP listen port (default: 9000)")
    parser.add_argument("--quiet", action="store_true", help="Suppress console logging and write JSON state only")

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", args.port))
        print(f"[+] Real-Time ETC Eos Transmit Monitor active!")
        print(f"[+] Listening on UDP port {args.port}...")
        print(f"[+] Live state recording to: {os.path.abspath(STATE_FILE)}")
    except Exception as e:
        print(f"[-] Could not bind to port {args.port}: {e}")
        sys.exit(1)

    live_state = EosLiveState()

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            osc_addr, osc_args = parse_osc_packet(data)

            if osc_addr:
                live_state.update(osc_addr, osc_args)
                if not args.quiet:
                    print(f"[Eos Transmit {addr[0]}] {osc_addr} -> {osc_args}")

    except KeyboardInterrupt:
        print("\n[+] Monitor daemon stopped.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
