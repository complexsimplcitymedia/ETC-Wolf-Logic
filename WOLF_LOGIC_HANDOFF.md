# Wolf Logic — Dual-NIC Air-Gapped Network Architecture & Telemetry Blueprint
## 🐺 Final Handoff Document

**Date**: 2026-08-28  
**Repository**: `https://github.com/complexsimplcitymedia/ETC-Wolf-Logic.git`  
**Target Platform**: Apple Silicon MacBook Pro / Docker Desktop / Native macOS  
**Target Deployment**: Norwegian Cruise Line (NCL) Main Theater & Stage Production  

---

## 1. Dual-NIC Air-Gapped Network Topology

macOS naturally maintains strict physical separation between multiple network interfaces, ensuring the **ETC Lighting Network remains 100% air-gapped and closed**, while your personal control mesh handles device telemetry:

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
  (Private Devices)◄─┼──• Phone on Tripod (OBS Camera Stream)   │
                     │  • FOH Audio Console Timecode Sync        │
                     │  • Web Magic Sheet Visualizer (Port 8888) │
                     │  • Local AI Ingest & Analysis (Ollama)    │
                     │                                           │
                     └───────────────────────────────────────────┘
```

### Key Security & Routing Rules:
1. **Never Bridge the Subnets**: macOS routing ensures broadcast/multicast DMX packets (sACN/Art-Net) stay strictly on the physical Ethernet lighting switch and never leak to Wi-Fi or Tailscale.
2. **Deterministic Console Communication**: Eos Nomad talks directly to the master lighting desk on the air-gapped lighting network without interference.
3. **Total Telemetry Freedom**: Your phone camera, OBS stream, and Wolf Logic AI models sync over your private device mesh without touching ship guest/crew networks.

---

## 2. Complete Component Manifest

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
| **OBS Vision Calibration** | [`scripts/wolf_vision_calibration.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_vision_calibration.py) | Phone camera rehearsal frame-by-frame mapping |
| **Local Vision Client** | [`scripts/wolf_local_vision.py`](file:///mnt/wolf-thumb/ETC-Wolf/.agents/skills/etc-osc-bridge/scripts/wolf_local_vision.py) | Llama 3.2 Vision (11B) & LLaVA (13B) Ollama client |
| **Docker Desktop Stack** | [`Dockerfile`](file:///mnt/wolf-thumb/ETC-Wolf/Dockerfile), [`docker-compose.yml`](file:///mnt/wolf-thumb/ETC-Wolf/docker-compose.yml) | Multi-arch turnkey containerization |
| **1-Hour Port Bootstrap** | [`scripts/port_turnaround_bootstrap.sh`](file:///mnt/wolf-thumb/ETC-Wolf/scripts/port_turnaround_bootstrap.sh) | Parallel offline model & container caching script |

---

## 3. Quick Start (Docker Desktop)

```bash
# 1. Start the entire Wolf Logic engine
docker compose up -d

# 2. View live streaming logs
docker compose logs -f wolf-engine

# 3. Open Magic Sheet Visualizer
open http://localhost:8888
```

---

*🐺 Wolf Logic — Rigged once. Air-gapped, unified, and understood in 2,560 dimensions.*
