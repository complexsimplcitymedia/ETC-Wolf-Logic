#!/usr/bin/env python3
"""
Art-Net to ETC Eos OSC Protocol Converter Bridge
Receives incoming Art-Net DMX packets (UDP port 6454), converts channel levels to OSC,
and transmits OSC messages to ETC Eos on UDP port 8000.
"""

import socket
import struct
import sys
import time
import argparse

def encode_osc_string(s: str) -> bytes:
    """Encodes a string into OSC null-terminated 4-byte padded bytes."""
    b = s.encode('utf-8') + b'\x00'
    pad = (4 - (len(b) % 4)) % 4
    return b + (b'\x00' * pad)

def build_osc_message(address: str, value: float) -> bytes:
    """Builds an OSC message with a single float argument."""
    msg = encode_osc_string(address)
    msg += encode_osc_string(",f")
    msg += struct.pack(">f", float(value))
    return msg

def parse_artnet_packet(data: bytes) -> tuple:
    """
    Parses an Art-Net packet. Returns (universe, dmx_channels) or (None, None) if invalid.
    """
    if len(data) < 18 or not data.startswith(b'Art-Net\x00'):
        return None, None

    opcode = struct.unpack("<H", data[8:10])[0]
    if opcode != 0x5000:  # ArtDmx OpCode
        return None, None

    proto_ver = struct.unpack(">H", data[10:12])[0]
    seq = data[12]
    physical = data[13]
    sub_universe = struct.unpack("<H", data[14:16])[0]
    length = struct.unpack(">H", data[16:18])[0]

    dmx_data = data[18:18 + length]
    return sub_universe, dmx_data

def main():
    parser = argparse.ArgumentParser(description="Art-Net to ETC Eos OSC Protocol Converter Bridge")
    parser.add_argument("--listen-port", type=int, default=6454, help="Art-Net UDP listen port (default: 6454)")
    parser.add_argument("--target-ip", default="10.0.0.247", help="ETC Eos Target IP (default: 10.0.0.247)")
    parser.add_argument("--target-port", type=int, default=8000, help="ETC Eos OSC UDP port (default: 8000)")
    parser.add_argument("--universe", type=int, default=0, help="Art-Net Universe to convert (default: 0)")
    parser.add_argument("--mode", choices=["chan", "sub", "fader"], default="chan", help="OSC mapping mode: chan (/eos/chan/x), sub (/eos/sub/x), fader (/eos/fader/1/x)")
    parser.add_argument("--min-delta", type=int, default=1, help="Minimum DMX level change to trigger OSC packet (default: 1)")

    args = parser.parse_args()

    # Socket to receive Art-Net
    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        rx_sock.bind(("0.0.0.0", args.listen_port))
        print(f"[+] Art-Net to OSC Bridge active!")
        print(f"[+] Listening for Art-Net on UDP port {args.listen_port} (Universe {args.universe})...")
        print(f"[+] Forwarding OSC ({args.mode} mode) to Eos at {args.target_ip}:{args.target_port}")
    except Exception as e:
        print(f"[-] Error binding Art-Net port {args.listen_port}: {e}")
        sys.exit(1)

    # Socket to send OSC to Eos
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # DMX state tracking for delta filtering
    previous_dmx_state = [ -1 ] * 512

    try:
        while True:
            data, addr = rx_sock.recvfrom(2048)
            univ, dmx_bytes = parse_artnet_packet(data)
            
            if univ is None or univ != args.universe:
                continue

            for ch_idx, val in enumerate(dmx_bytes[:512]):
                prev_val = previous_dmx_state[ch_idx]
                if abs(val - prev_val) >= args.min_delta:
                    previous_dmx_state[ch_idx] = val
                    ch_num = ch_idx + 1

                    # Convert 8-bit DMX (0-255) to OSC percentage (0.0-100.0)
                    osc_pct = round((val / 255.0) * 100.0, 2)

                    if args.mode == "chan":
                        osc_addr = f"/eos/chan/{ch_num}"
                    elif args.mode == "sub":
                        osc_addr = f"/eos/sub/{ch_num}"
                    elif args.mode == "fader":
                        osc_addr = f"/eos/fader/1/{ch_num}"

                    osc_packet = build_osc_message(osc_addr, osc_pct)
                    tx_sock.sendto(osc_packet, (args.target_ip, args.target_port))
                    print(f"[Art-Net ➔ OSC] Ch {ch_num:3d}: DMX {val:3d} ➔ {osc_addr} ({osc_pct}%)")

    except KeyboardInterrupt:
        print("\n[+] Art-Net to OSC Bridge stopped.")
    finally:
        rx_sock.close()
        tx_sock.close()

if __name__ == "__main__":
    main()
