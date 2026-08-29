#!/usr/bin/env python3
"""
ETC Eos OSC Communication & Diagnostic Tool
Tests sending and receiving OSC (Open Sound Control) UDP packets to/from ETC Eos and TouchOSC Bridge.
"""

import socket
import sys
import time
import argparse

def encode_osc_string(s: str) -> bytes:
    """Encodes a string into OSC null-terminated 4-byte padded bytes."""
    b = s.encode('utf-8') + b'\x00'
    pad = (4 - (len(b) % 4)) % 4
    return b + (b'\x00' * pad)

def build_osc_message(address: str, args=None) -> bytes:
    """Builds a basic OSC packet with string or int/float arguments."""
    msg = encode_osc_string(address)
    if not args:
        # Type tag string with just ','
        msg += encode_osc_string(",")
        return msg

    tags = ","
    arg_bytes = b""

    for arg in args:
        if isinstance(arg, str):
            tags += "s"
            arg_bytes += encode_osc_string(arg)
        elif isinstance(arg, int):
            tags += "i"
            import struct
            arg_bytes += struct.pack(">i", arg)
        elif isinstance(arg, float):
            tags += "f"
            import struct
            arg_bytes += struct.pack(">f", arg)

    msg += encode_osc_string(tags)
    msg += arg_bytes
    return msg

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

def main():
    parser = argparse.ArgumentParser(description="Test OSC connection with ETC Eos / TouchOSC Bridge")
    parser.add_argument("--target-ip", default="127.0.0.1", help="Target IP of Eos or TouchOSC host (default: 127.0.0.1)")
    parser.add_argument("--send-port", type=int, default=8000, help="UDP send port (default: 8000)")
    parser.add_argument("--listen-port", type=int, default=8001, help="UDP listen port (default: 8001)")
    parser.add_argument("--cmd", default="/eos/ping", help="OSC address pattern to send (default: /eos/ping)")
    parser.add_argument("--text", default="ping", help="String argument to pass with OSC command")
    parser.add_argument("--listen-only", action="store_true", help="Only listen for incoming OSC packets")
    parser.add_argument("--timeout", type=int, default=5, help="Listen timeout in seconds (default: 5)")

    args = parser.parse_args()

    # Create UDP listening socket
    sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock_rx.bind(("0.0.0.0", args.listen_port))
        sock_rx.settimeout(args.timeout)
        print(f"[+] Listening for OSC response on port {args.listen_port} (timeout: {args.timeout}s)...")
    except Exception as e:
        print(f"[-] Could not bind to listen port {args.listen_port}: {e}")
        sock_rx = None

    if not args.listen_only:
        sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        osc_pkt = build_osc_message(args.cmd, [args.text] if args.text else None)
        print(f"[+] Sending OSC packet '{args.cmd}' [{args.text}] to {args.target_ip}:{args.send_port}...")
        try:
            sock_tx.sendto(osc_pkt, (args.target_ip, args.send_port))
            print("[+] OSC packet sent successfully.")
        except Exception as e:
            print(f"[-] Error sending OSC packet: {e}")
        finally:
            sock_tx.close()

    if sock_rx:
        start_time = time.time()
        while time.time() - start_time < args.timeout:
            try:
                data, addr = sock_rx.recvfrom(4096)
                osc_addr, _ = parse_osc_string(data, 0)
                print(f"[==>] Received OSC from {addr[0]}:{addr[1]} -> Address: {osc_addr}")
            except socket.timeout:
                print("[-] Listening timed out. No packet received.")
                break
            except Exception as e:
                print(f"[-] Error receiving OSC: {e}")
                break
        sock_rx.close()

if __name__ == "__main__":
    main()
