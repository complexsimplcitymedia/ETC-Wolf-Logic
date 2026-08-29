#!/usr/bin/env python3
"""
TouchOSC Bridge & MIDI Connection Diagnostic Tool
Monitors and tests MIDI input/output over TouchOSC Bridge (UDP port 58210) and system MIDI interfaces.
"""

import socket
import sys
import time
import argparse

def parse_midi_message(data: bytes):
    """Basic parser for standard raw MIDI bytes (Status, Data1, Data2)."""
    if len(data) < 1:
        return "Empty data"
    
    status = data[0]
    msg_type = status & 0xF0
    channel = (status & 0x0F) + 1

    if msg_type == 0x90:
        note = data[1] if len(data) > 1 else 0
        velocity = data[2] if len(data) > 2 else 0
        return f"Note On  | Ch {channel:2d} | Note {note:3d} | Velocity {velocity:3d}"
    elif msg_type == 0x80:
        note = data[1] if len(data) > 1 else 0
        velocity = data[2] if len(data) > 2 else 0
        return f"Note Off | Ch {channel:2d} | Note {note:3d} | Velocity {velocity:3d}"
    elif msg_type == 0xB0:
        cc = data[1] if len(data) > 1 else 0
        val = data[2] if len(data) > 2 else 0
        return f"Control Change (CC) | Ch {channel:2d} | CC {cc:3d} | Value {val:3d}"
    elif msg_type == 0xC0:
        prog = data[1] if len(data) > 1 else 0
        return f"Program Change | Ch {channel:2d} | Program {prog:3d}"
    elif msg_type == 0xE0:
        lsb = data[1] if len(data) > 1 else 0
        msb = data[2] if len(data) > 2 else 0
        val = (msb << 7) | lsb
        return f"Pitch Bend | Ch {channel:2d} | Value {val:5d}"
    else:
        return f"Raw MIDI (0x{status:02X}) -> {data.hex()}"

def build_midi_cc_packet(channel: int, cc: int, value: int) -> bytes:
    """Constructs a 3-byte Control Change MIDI message."""
    status = 0xB0 | ((channel - 1) & 0x0F)
    return bytes([status, cc & 0x7F, value & 0x7F])

def build_midi_note_packet(channel: int, note: int, velocity: int) -> bytes:
    """Constructs a 3-byte Note On MIDI message."""
    status = 0x90 | ((channel - 1) & 0x0F)
    return bytes([status, note & 0x7F, velocity & 0x7F])

def main():
    parser = argparse.ArgumentParser(description="Test TouchOSC Bridge MIDI & UDP Signals")
    parser.add_argument("--listen-port", type=int, default=58210, help="TouchOSC Bridge UDP listen port (default: 58210)")
    parser.add_argument("--target-ip", default="127.0.0.1", help="Target IP for TouchOSC Bridge (default: 127.0.0.1)")
    parser.add_argument("--send-port", type=int, default=58210, help="Target UDP port to send MIDI (default: 58210)")
    parser.add_argument("--send-cc", type=int, help="Send MIDI Control Change (CC) number (0-127)")
    parser.add_argument("--send-note", type=int, help="Send MIDI Note On number (0-127)")
    parser.add_argument("--value", type=int, default=127, help="MIDI value / velocity (0-127, default 127)")
    parser.add_argument("--channel", type=int, default=1, help="MIDI channel (1-16, default 1)")
    parser.add_argument("--timeout", type=int, default=10, help="Listening timeout in seconds (default: 10)")

    args = parser.parse_args()

    # Create socket for listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", args.listen_port))
        sock.settimeout(args.timeout)
        print(f"[+] Bound UDP socket to port {args.listen_port}. Monitoring TouchOSC Bridge MIDI packets...")
    except Exception as e:
        print(f"[-] Could not bind UDP socket to port {args.listen_port}: {e}")
        sock = None

    # Handle sending test MIDI packet
    if args.send_cc is not None or args.send_note is not None:
        tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if args.send_cc is not None:
            pkt = build_midi_cc_packet(args.channel, args.send_cc, args.value)
            print(f"[+] Sending MIDI CC {args.send_cc} (Val: {args.value}, Ch: {args.channel}) to {args.target_ip}:{args.send_port}...")
        else:
            pkt = build_midi_note_packet(args.channel, args.send_note, args.value)
            print(f"[+] Sending MIDI Note {args.send_note} (Vel: {args.value}, Ch: {args.channel}) to {args.target_ip}:{args.send_port}...")

        try:
            tx_sock.sendto(pkt, (args.target_ip, args.send_port))
            print("[+] MIDI packet sent successfully.")
        except Exception as e:
            print(f"[-] Error sending MIDI packet: {e}")
        finally:
            tx_sock.close()

    # Handle listening loop
    if sock:
        start_time = time.time()
        print(f"[+] Waiting for incoming MIDI packets (timeout: {args.timeout}s)...")
        while time.time() - start_time < args.timeout:
            try:
                data, addr = sock.recvfrom(1024)
                parsed = parse_midi_message(data)
                print(f"[==>] Received from {addr[0]}:{addr[1]} -> {parsed}")
            except socket.timeout:
                print("[-] Listening timed out.")
                break
            except Exception as e:
                print(f"[-] Error receiving packet: {e}")
                break
        sock.close()

if __name__ == "__main__":
    main()
