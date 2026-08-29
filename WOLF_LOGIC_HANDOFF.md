# Wolf Logic — Client Isolation Bypass & Tailscale Mesh Overlay Architecture
## 🐺 Technical Reference & Final Handoff

**Date**: 2026-08-28  
**Repository**: `https://github.com/complexsimplcitymedia/ETC-Wolf-Logic.git`  
**Target Platform**: Apple Silicon MacBook Pro / Docker Desktop / Native macOS  
**Target Deployment**: Norwegian Cruise Line (NCL) Theatrical Lighting & Maritime Control  

---

## 1. The Cruise Ship Wi-Fi Problem: AP Client Isolation

On all cruise ship crew/guest Wi-Fi networks, the IT infrastructure enforces **Access Point (AP) Client Isolation (Station Isolation / Private VLANs)**:
- **Device A (Phone on Tripod)** and **Device B (MacBook Pro)** are blocked from discovering or talking to each other over the local Wi-Fi subnet.
- Standard LAN broadcasts, Bonjour/mDNS, and direct local IP connections fail.

---

## 2. The Solution: Tailscale Peer-to-Peer Overlay Network

Wolf Logic runs over **Tailscale (WireGuard Mesh Tunnel)** across all personal devices, completely bypassing shipboard client isolation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SHIPBOARD WIRELESS INFRASTRUCTURE                        │
│             (Enforces Strict AP Client Isolation / Private VLANs)           │
└───────────────────────┬─────────────────────────────┬───────────────────────┘
                        │                             │
    [Encrypted Outbound WireGuard UDP]    [Encrypted Outbound WireGuard UDP]
                        │                             │
                        ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TAILSCALE ENCRYPTED PEER-TO-PEER MESH                    │
│                                                                             │
│   [Phone on Tripod] ◄────────────────────────► [M1 Max MacBook Pro]         │
│   (IP: 100.81.x.x)                             (IP: 100.110.x.x)            │
│   • OBS Camera Feed & Timecode                 • Wolf Logic Docker Engine   │
│   • Local OSC Triggering                       • Eos Telemetry Matrix       │
│                                                • Local LLaVA/Qwen AI        │
│                                                       ▲                     │
│                                                       │                     │
│   [Cabin Compute / Fallback Node (ROCm 7800 XT)] ─────┘                     │
│   (IP: 100.95.x.x)                                                          │
│   • Headless Batch AI & Crypto Mining                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Tailscale is Mandatory at Sea:
1. **Punches Through AP Client Isolation**: Every device communicates over virtual `100.x.x.x` WireGuard interfaces. To the ship's access point, it just looks like standard encrypted traffic.
2. **Zero Inbound Router Configuration**: Requires no port forwarding, no static local IP reservation, and no IT department approval.
3. **Encrypted & Private**: No ship passenger or crew member on the shared Wi-Fi can snoop on your lighting triggers, OSC command lines, or video streams.

---

## 3. Dual-NIC Air-Gapped Network Topology

```
                                  M1 MAX MACBOOK PRO
                     ┌───────────────────────────────────────────┐
                     │                                           │
  AIR-GAPPED         │  [Interface 1: Gigabit Thunderbolt NIC]   │
  LIGHTING LAN       │  • Subnet: 10.101.x.x / 255.255.0.0       │
  (Zero Internet) ◄──┼──• Protocols: sACN E1.31, Art-Net 4,     │
                     │    Net3, ETC Eos OSC (8000/8001)          │
                     │  • Direct switch connection to Eos Master │
                     │                                           │
                     ├───────────────────────────────────────────┤
                     │                                           │
  SECURE TELEMETRY   │  [Interface 2: Wi-Fi / Tailscale Mesh]    │
  & AI CONTROL       │  • Subnet: 100.x.x.x (Encrypted Mesh)     │
  (Private Devices)◄─┼──• Bypasses Ship AP Client Isolation      │
                     │  • Phone on Tripod (OBS Camera Stream)   │
                     │  • Audio Console Timecode Sync            │
                     │  • Web Magic Sheet Visualizer (Port 1010) │
                     │  • Local AI Ingest & Analysis (Ollama)    │
                     │                                           │
                     └───────────────────────────────────────────┘
```

---

## 4. Complete Component Manifest

| Component | File / Script | Purpose |
| :--- | :--- | :--- |
| **High-Speed Ingest Server** | [`src/server.js`](file:///mnt/wolf-thumb/ETC-Wolf/src/server.js) | Node.js UDP sockets for OSC, Art-Net, sACN, MIDI |
| **3D Magic Sheet Visualizer**| [`public/magicsheet.html`](file:///mnt/wolf-thumb/ETC-Wolf/public/magicsheet.html) | WebSocket visualizer matching your stage layout |
| **Universal HSI Matrix** | [`scripts/wolf_logic_matrix.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_logic_matrix.py) | 2,560-dimension spatial vector in SQLite WAL |
| **Color Temperature Calibration** | [`scripts/wolf_effect_engine.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_effect_engine.py) | 3200K Tungsten, 4400K Cool White, 5600K Daylight Raw |
| **Universal Gel Library** | [`scripts/wolf_gel_library.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_gel_library.py) | Pre-loaded Roscolux, Lee, and CT gel library |
| **Live Eos Palette Builder** | [`scripts/build_eos_palettes.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/build_eos_palettes.py) | Programs CP 1-11 & CP 101-114 into Eos showfile |
| **NCL Fleet Fixture Catalog**| [`scripts/wolf_ncl_fixture_library.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_ncl_fixture_library.py) | Claypaky, Vari-Lite, Robe, Proteus, ETC profiles |
| **Unpatched Rig CSV** | [`csv_exports/ncl_rig_inventory_unpatched.csv`](file:///mnt/wolf-thumb/ETC-Wolf/csv_exports/ncl_rig_inventory_unpatched.csv) | 120 unpatched fleet fixtures template |
| **3D Augment3d Coordinates** | [`scripts/wolf_augment3d_magicsheet.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_augment3d_magicsheet.py) | Exact XYZ stage metric coordinates |
| **Audio Timecode Sync** | [`scripts/wolf_timecode_sync.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_timecode_sync.py) | Audio console OSC & SMPTE timecode sync |
| **OBS Vision Calibration** | [`scripts/wolf_vision_calibration.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_vision_calibration.py) | Rehearsal video-to-DMX spatial calibration |
| **Local Vision Client** | [`scripts/wolf_local_vision.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_local_vision.py) | Llama 3.2 Vision (11B) & LLaVA (13B) Ollama client |
| **Docker Desktop Stack** | [`Dockerfile`](file:///mnt/wolf-thumb/ETC-Wolf/Dockerfile), [`docker-compose.yml`](file:///mnt/wolf-thumb/ETC-Wolf/docker-compose.yml) | Multi-arch turnkey containerization |
| **1-Hour Port Bootstrap** | [`scripts/port_turnaround_bootstrap.sh`](file:///mnt/wolf-thumb/ETC-Wolf/scripts/port_turnaround_bootstrap.sh) | Parallel offline model & container caching |
| **Gigabit Model Downloader**| [`scripts/download_models_to_drive.sh`](file:///mnt/wolf-thumb/ETC-Wolf/scripts/download_models_to_drive.sh) | Direct GGUF pre-downloader to 256GB card |

---

## 5. Quick Start (Docker Desktop)

```bash
# 1. Start the entire Wolf Logic engine
docker compose up -d

# 2. View live streaming logs
docker compose logs -f wolf-engine

# 3. Open Magic Sheet Visualizer on iPad Pro / Laptop
open http://localhost:1010
```

---

*🐺 Wolf Logic — Rigged once. Air-gapped, Tailscale-isolated, and understood in 2,560 dimensions.*
