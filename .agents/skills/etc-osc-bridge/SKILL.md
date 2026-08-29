---
name: etc-osc-bridge
description: >-
  Use this skill when setting up, troubleshooting, or communicating with ETC Eos
  lighting software/consoles using OSC (Open Sound Control), TouchOSC / TouchOSC Bridge MIDI,
  Protokol relays, and DMX over IP protocols (sACN / ANSI E1.31 and Art-Net).
---

# ETC Eos, Protokol / Local Relay & DMX Integration

This skill provides comprehensive setup guides, network configuration, diagnostic scripts, and reference documentation for:
1. **ETC Eos Isolated Network & Local Relay** (`windows_eos_relay.py` on Windows).
2. **Art-Net to ETC Eos OSC Protocol Converter** (`artnet_to_osc_bridge.py`).
3. **TouchOSC Bridge MIDI Control** (`test_midi.py`).
4. **DMX Protocol Suite (sACN / ANSI E1.31 and Art-Net 4)** (`dmx_tool.py`).

---

## 1. Network Isolation Architecture (Eos Default Settings)

In professional lighting environments, ETC Eos remains bound strictly to its default local network ports and loopback interface:
- **Eos RX Port**: `8000`
- **Eos TX Port**: `8001`
- **Eos TX Target IP**: `127.0.0.1` (Isolated local lighting network)

### Local Windows Relay (`windows_eos_relay.py`):
To relay Eos OSC updates across the network to remote agents without breaking Eos network isolation:
- Run `windows_eos_relay.py` directly on the Windows host machine (`BRICE-HP`):
  ```cmd
  python C:\Users\d_ada\windows_eos_relay.py --relay-target 100.81.66.31 --relay-port 9000
  ```
- The relay captures native Eos OSC on port `8001` and forwards streams securely across Tailscale/LAN.

---

## 2. TouchOSC & Protokol Bridge Setup

- **TouchOSC / Protokol MIDI**: UDP port `58210`.
- **Protokol OSC Monitoring**: Binds to port `8001` or `8000` to mirror OSC strings live.

---

## 3. Diagnostic & Protocol Tool Suite

| Tool | Script | Purpose |
| :--- | :--- | :--- |
| **Local Eos Relay** | [`windows_eos_relay.py`](./scripts/windows_eos_relay.py) | Relays isolated Eos OSC outputs to remote agent |
| **Art-Net ➔ OSC Bridge** | [`artnet_to_osc_bridge.py`](./scripts/artnet_to_osc_bridge.py) | Converts Art-Net DMX levels to Eos OSC commands |
| **DMX Suite** | [`dmx_tool.py`](./scripts/dmx_tool.py) | Transmits & monitors sACN (E1.31) and Art-Net universes |
| **MIDI Diagnostic** | [`test_midi.py`](./scripts/test_midi.py) | Monitors TouchOSC / Protokol MIDI packets |
| **OSC Diagnostic** | [`test_osc.py`](./scripts/test_osc.py) | Sends OSC pings & address queries (`/eos/cmd`, `/eos/ping`) |

---

## 4. Documentation References

- [`eos_osc_reference.md`](./references/eos_osc_reference.md): Eos OSC syntax and address patterns.
- [`dmx_reference.md`](./references/dmx_reference.md): sACN (E1.31) and Art-Net protocol specs and patch guide.
