#!/usr/bin/env python3
"""
Windows Local Eos OSC Relay Daemon
Runs locally on the Windows host machine (BRICE-HP).
Binds to 127.0.0.1:8001 to capture native Eos OSC transmit data,
and relays OSC updates over the network to the remote Linux agent.
"""

import socket
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Local Eos OSC Relay for Isolated Lighting Networks")
    parser.add_argument("--eos-tx-port", type=int, default=8001, help="Default Eos TX port (default: 8001)")
    parser.add_argument("--eos-rx-port", type=int, default=8000, help="Default Eos RX port (default: 8000)")
    parser.add_argument("--relay-target", default="100.81.66.31", help="Target Linux Agent IP (default: 100.81.66.31)")
    parser.add_argument("--relay-port", type=int, default=9000, help="Relay output port (default: 9000)")

    args = parser.parse_args()

    # Bind to local interface to receive Eos output
    sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock_rx.bind(("0.0.0.0", args.eos_tx_port))
        print(f"[+] Windows Eos Local Relay Active!")
        print(f"[+] Listening for native Eos OSC on port {args.eos_tx_port}...")
        print(f"[+] Forwarding relay stream to Linux Agent at {args.relay_target}:{args.relay_port}")
    except Exception as e:
        print(f"[-] Could not bind to port {args.eos_tx_port}: {e}")
        sys.exit(1)

    sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            data, addr = sock_rx.recvfrom(4096)
            sock_tx.sendto(data, (args.relay_target, args.relay_port))
            print(f"[Relay ➔ Linux] Relayed {len(data)} bytes from Eos ({addr[0]})")
    except KeyboardInterrupt:
        print("\n[+] Relay stopped.")
    finally:
        sock_rx.close()
        sock_tx.close()

if __name__ == "__main__":
    main()
