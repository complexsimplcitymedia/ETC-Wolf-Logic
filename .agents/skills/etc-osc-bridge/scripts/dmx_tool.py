#!/usr/bin/env python3
"""
DMX Protocol Diagnostic & Testing Utility
Supports sACN (ANSI E1.31) and Art-Net 4 DMX transmission and monitoring.
"""

import socket
import struct
import sys
import time
import argparse
import uuid

# --- sACN / E1.31 Packet Builder ---
VECTOR_ROOT_E131_DATA = 0x00000004
VECTOR_E131_DATA_PACKET = 0x00000002
VECTOR_DMP_SET_PROPERTY = 0x02

SOURCE_NAME = "ETC-Wolf DMX Agent"
DEFAULT_CID = uuid.uuid4().bytes

def create_sacn_packet(universe: int, dmx_channels: bytes, sequence: int = 0, priority: int = 100) -> bytes:
    """
    Constructs a compliant ANSI E1.31 (sACN) DMX packet.
    dmx_channels: bytes of length up to 512.
    """
    if len(dmx_channels) > 512:
        dmx_channels = dmx_channels[:512]
    # Pad to 512 channels if necessary
    dmx_data = dmx_channels + b'\x00' * (512 - len(dmx_channels))

    # ACN Root Layer (38 bytes)
    preamble_size = 0x0010
    postamble_size = 0x0000
    acn_pid = b'ASC-E1.17\x00\x00\x00'
    
    root_fl = 0x7000 | (38 + 77 + 10 + 1 + 512)  # Flags (0x7) + Length
    vector_root = struct.pack(">I", VECTOR_ROOT_E131_DATA)

    root_layer = (
        struct.pack(">HH", preamble_size, postamble_size) +
        acn_pid +
        struct.pack(">H", root_fl) +
        vector_root +
        DEFAULT_CID
    )

    # Framing Layer (77 bytes)
    framing_fl = 0x7000 | (77 + 10 + 1 + 512)
    source_name_bytes = SOURCE_NAME.encode('utf-8').ljust(64, b'\x00')
    vector_framing = struct.pack(">I", VECTOR_E131_DATA_PACKET)

    framing_layer = (
        struct.pack(">H", framing_fl) +
        vector_framing +
        source_name_bytes +
        struct.pack(">BBH", priority, 0, universe)
    )
    # Sequence (1 byte), Options (1 byte)
    framing_layer += struct.pack(">BB", sequence & 0xFF, 0x00)

    # DMP Layer (10 + 1 + 512 bytes)
    dmp_fl = 0x7000 | (10 + 1 + 512)
    vector_dmp = bytes([VECTOR_DMP_SET_PROPERTY])
    address_type_datatype = bytes([0xa1]) # 0xa1 = One-byte address, incrementing
    first_property_address = struct.pack(">H", 0x0000)
    address_increment = struct.pack(">H", 0x0001)
    property_value_count = struct.pack(">H", 513) # 1 START code + 512 DMX slots
    start_code = b'\x00' # DMX512 START code

    dmp_layer = (
        struct.pack(">H", dmp_fl) +
        vector_dmp +
        address_type_datatype +
        first_property_address +
        address_increment +
        property_value_count +
        start_code +
        dmx_data
    )

    return root_layer + framing_layer + dmp_layer

# --- Art-Net Packet Builder ---
def create_artnet_packet(universe: int, dmx_channels: bytes, sequence: int = 0) -> bytes:
    """
    Constructs an ArtDmx (Art-Net 4) packet.
    """
    if len(dmx_channels) > 512:
        dmx_channels = dmx_channels[:512]
    dmx_data = dmx_channels + b'\x00' * (512 - len(dmx_channels))

    header = b'Art-Net\x00'
    opcode = struct.pack("<H", 0x5000) # OpOutput / ArtDmx
    proto_ver = struct.pack(">H", 14) # Art-Net version 14
    seq = bytes([sequence & 0xFF])
    physical = b'\x00'
    sub_universe = struct.pack("<H", universe & 0x7FFF)
    length = struct.pack(">H", len(dmx_data))

    return header + opcode + proto_ver + seq + physical + sub_universe + length + dmx_data


def main():
    parser = argparse.ArgumentParser(description="DMX Protocol Utility (sACN & Art-Net)")
    subparsers = parser.add_subparsers(dest="protocol", required=True)

    # sACN Subcommand
    sacn_parser = subparsers.add_parser("sacn", help="Send sACN (ANSI E1.31) DMX data")
    sacn_parser.add_argument("--universe", type=int, default=1, help="sACN Universe (1-63999, default: 1)")
    sacn_parser.add_argument("--channel", type=int, default=1, help="DMX Channel (1-512, default: 1)")
    sacn_parser.add_argument("--level", type=int, default=255, help="DMX Channel Level (0-255, default: 255)")
    sacn_parser.add_argument("--ip", default=None, help="Target unicast IP (default: multicast 239.255.u_hi.u_lo)")
    sacn_parser.add_argument("--priority", type=int, default=100, help="sACN priority (0-200, default: 100)")
    sacn_parser.add_argument("--count", type=int, default=3, help="Number of packets to send (default: 3)")

    # Art-Net Subcommand
    art_parser = subparsers.add_parser("artnet", help="Send Art-Net DMX data")
    art_parser.add_argument("--universe", type=int, default=0, help="Art-Net Universe (0-32767, default: 0)")
    art_parser.add_argument("--channel", type=int, default=1, help="DMX Channel (1-512, default: 1)")
    art_parser.add_argument("--level", type=int, default=255, help="DMX Channel Level (0-255, default: 255)")
    art_parser.add_argument("--ip", default="255.255.255.255", help="Target broadcast/unicast IP (default: 255.255.255.255)")
    art_parser.add_argument("--count", type=int, default=3, help="Number of packets to send (default: 3)")

    # Listen Subcommand
    listen_parser = subparsers.add_parser("listen", help="Listen for sACN DMX packets")
    listen_parser.add_argument("--universe", type=int, default=1, help="sACN Universe to listen to (default: 1)")
    listen_parser.add_argument("--timeout", type=int, default=10, help="Listen timeout in seconds (default: 10)")

    args = parser.parse_args()

    if args.protocol == "sacn":
        dmx_vals = bytearray(512)
        if 1 <= args.channel <= 512:
            dmx_vals[args.channel - 1] = max(0, min(255, args.level))
        
        target_ip = args.ip
        if not target_ip:
            u_hi = (args.universe >> 8) & 0xFF
            u_lo = args.universe & 0xFF
            target_ip = f"239.255.{u_hi}.{u_lo}"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        print(f"[+] Transmitting sACN (E1.31) Universe {args.universe} -> Channel {args.channel} = {args.level}")
        print(f"[+] Target IP: {target_ip}:5568 | Priority: {args.priority}")

        for i in range(args.count):
            pkt = create_sacn_packet(args.universe, bytes(dmx_vals), sequence=i+1, priority=args.priority)
            sock.sendto(pkt, (target_ip, 5568))
            time.sleep(0.1)
        print("[+] sACN transmission completed.")
        sock.close()

    elif args.protocol == "artnet":
        dmx_vals = bytearray(512)
        if 1 <= args.channel <= 512:
            dmx_vals[args.channel - 1] = max(0, min(255, args.level))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"[+] Transmitting Art-Net Universe {args.universe} -> Channel {args.channel} = {args.level}")
        print(f"[+] Target IP: {args.ip}:6454")

        for i in range(args.count):
            pkt = create_artnet_packet(args.universe, bytes(dmx_vals), sequence=i+1)
            sock.sendto(pkt, (args.ip, 6454))
            time.sleep(0.1)
        print("[+] Art-Net transmission completed.")
        sock.close()

    elif args.protocol == "listen":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(("0.0.0.0", 5568))
            sock.settimeout(args.timeout)
            print(f"[+] Bound to UDP port 5568. Monitoring sACN Universe {args.universe} (Timeout: {args.timeout}s)...")
            start = time.time()
            while time.time() - start < args.timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    if len(data) > 125:
                        rx_univ = struct.unpack(">H", data[113:115])[0] if len(data) >= 115 else 0
                        print(f"[==>] Received sACN packet from {addr[0]} (Len: {len(data)} bytes, Universe: {rx_univ})")
                except socket.timeout:
                    print("[-] sACN listen timed out.")
                    break
        except Exception as e:
            print(f"[-] Could not bind sACN socket: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    main()
