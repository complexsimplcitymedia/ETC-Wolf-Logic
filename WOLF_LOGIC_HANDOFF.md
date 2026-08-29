# Wolf Logic — ETC Eos Telemetry System
## 🐺 Session Handoff Document

**Date**: 2026-08-28  
**Session**: Antigravity IDE — Conversation `17a3fd27-6000-41ec-9134-b446707eb8c8`  
**Operator**: d_ada / thewolfwalksalone  
**Project Root**: `/mnt/wolf-thumb/ETC-Wolf/`

---

## The Vision

Wolf Logic is a **live lighting intelligence system** designed for a professional lighting programmer working aboard a Norwegian Cruise Line ship with an **ETC Eos Family lighting console**. The system:

1. **Captures every console event** (cues, channels, command line, submasters, parameters) in real time via OSC.
2. **Stores everything in a SQLite database** (`wolf_logic_telemetry.db`) with timecodes.
3. **Runs a local LLM** (QwQ 3.7 27B or Qwen 4B) via Ollama on an **M1 Max MacBook Pro (64GB Unified Memory)** to analyze show data and surface insights.
4. **Captures video of the console workspace** and runs a **vision model** on the feed (with tolerable delay) to analyze what is happening on screen.
5. **Makes the programmer faster** — Wolf Logic becomes their embedded AI co-pilot for live production.

---

## Current Status: What Has Been Built

### ✅ Core OSC Diagnostic Suite
All scripts live in `.agents/skills/etc-osc-bridge/scripts/`

| Script | Purpose |
| :--- | :--- |
| `test_osc.py` | Send/receive raw OSC packets to ETC Eos |
| `test_midi.py` | Send/monitor MIDI CC/Note packets to TouchOSC Bridge (UDP 58210) |
| `dmx_tool.py` | Transmit/monitor sACN (ANSI E1.31) and Art-Net 4 universes |
| `artnet_to_osc_bridge.py` | Art-Net DMX → ETC Eos OSC converter with delta filtering |
| `windows_eos_relay.py` | Runs on Windows; relays isolated Eos OSC output (127.0.0.1:8001) to remote agents |
| `eos_realtime_monitor.py` | Persistent daemon: captures all Eos OSC telemetry → `live_eos_state.json` |

### ✅ Reference Documentation
| File | Purpose |
| :--- | :--- |
| `SKILL.md` | Antigravity skill definition — network setup, protocol guide |
| `eos_osc_reference.md` | Full Eos OSC address reference (`/eos/cmd`, `/eos/cue/...`, `/eos/fader/...`) |
| `dmx_reference.md` | sACN E1.31 & Art-Net 4 protocol specifications |

### ✅ Conda Environment
| Item | Value |
| :--- | :--- |
| **Environment Name** | `wolfetc` |
| **Python Version** | 3.11 |
| **Environment Path** | `/home/thewolfwalksalone/miniconda3/envs/wolfetc` |
| **Environment Spec** | `environment.yml` |

### ✅ Verified Windows Network Stack (BRICE-HP at `10.0.0.247`)
| Service | PID | Port |
| :--- | :--- | :--- |
| ETC Eos Family | 30320 | UDP 8000 (RX), 8001 (TX) |
| Hexler Protokol | 32824 | OSC/MIDI relay |
| TouchOSC Bridge | 37104 | UDP 58210 / Virtual MIDI |
| SSH Access | active | `d_ada@10.0.0.247` |
| WSL SSH Access | active | `wolf@100.110.82.182` (key auth configured) |

### ✅ Existing DMX Extension in Repo
There is a pre-existing DMX language/tooling project at `/mnt/wolf-thumb/ETC-Wolf/dmx/` (includes a VS Code extension, compiler toolchain, and website). This is **separate** from Wolf Logic but may be relevant for future fixture library integration.

---

## Live Data Flow Architecture

```
[ETC Eos Console (Windows 10.0.0.247)]
    │ OSC TX → 127.0.0.1:8001 (isolated network)
    ▼
[windows_eos_relay.py  (runs on BRICE-HP Windows)]
    │ UDP relay → Port 9000 over LAN/Tailscale
    ▼
[eos_realtime_monitor.py  (Linux / macOS wolfetc env)]
    ├── Writes → live_eos_state.json  (real-time snapshot for IDE backend)
    └── INSERT → wolf_logic_telemetry.db  (SQLite, timecoded events)
                     │
                     ├── SELECT queries → Local LLM (QwQ 27B / Qwen 4B via Ollama)
                     └── Vision analysis ← vision_analyzer.py ← video_capture.py
```

---

## What Needs to Be Built Next

### Phase 1 — Git Repo & Project Structure
- [ ] Initialize Git repo (`git init`) in `/mnt/wolf-thumb/ETC-Wolf/`
- [ ] Create proper `.gitignore` (exclude `node_modules/`, `.pyc`, runtime DB files, screenshots)
- [ ] Create top-level `README.md`
- [ ] Push to GitHub (private repo — name suggestion: `wolf-logic-eos`)

### Phase 2 — Wolf Logic SQLite Telemetry Engine
- [ ] Create `wolf_logic_db.py` — SQLite schema & write API
  - Tables: `console_events`, `cue_executions`, `command_history`, `channel_snapshots`, `patch_data`
- [ ] Integrate into `eos_realtime_monitor.py` — stream OSC events → SQLite with SMPTE/system timecodes
- [ ] Create SQL query helpers ("what cues fired in the last hour", "show me all ch1-10 moves tonight")

### Phase 3 — M1 Max macOS Deployment
- [ ] Test all Python scripts on macOS ARM64 (`conda activate wolfetc`)
- [ ] Install Ollama: `brew install ollama`
- [ ] Pull local LLM models:
  ```bash
  ollama pull qwen2.5:7b        # fast queries
  ollama pull qwq:32b           # deep analysis  
  ollama pull llava:13b         # vision model
  ```
- [ ] Create `wolf_logic_ai.py` — LLM query interface over SQLite
- [ ] Test with live Eos console on M1 Max hardware

### Phase 4 — Vision Model & Video Capture Pipeline
- [ ] Create `video_capture.py` — screen capture/camera feed recorder with frame timestamps
- [ ] Correlate video frames to console events via timecode in SQLite
- [ ] Create `vision_analyzer.py` — batch analyze frames with LLaVA/Qwen-VL
- [ ] Write vision analysis results to `wolf_logic_telemetry.db`

---

## Key Constraints & Architecture Decisions

> **CRITICAL — ETC Eos Network Isolation**: Eos must remain on its default local network binding (`127.0.0.1:8001` TX, `0.0.0.0:8000` RX). Do NOT try to change Eos TX IP to a remote address. Always use `windows_eos_relay.py` on the Windows host to bridge the isolated Eos network to external agents. Protokol can also serve as a relay bridge on the same isolated network.

> **Tailscale Topology**:
> - Linux Penguin: `100.81.66.31`
> - WSL BRICE-HP: `100.110.82.182` (SSH port 22, key auth ✅)
> - Windows BRICE-HP: `10.0.0.247` (LAN), Tailscale `100.110.82.43` (SSH port 22, password auth)

> **Ultimate Deployment Target**: M1 Max MacBook Pro (64GB Unified Memory) running macOS. All code must be ARM64 compatible. Use `conda activate wolfetc` for all Python work. No WSL or separate Linux server needed on the ship.

---

## Activation Commands (Current Environment)

```bash
# Start Conda environment
conda activate wolfetc

# Start Windows Eos Relay (run from Linux/Mac)
sshpass -p "6658" ssh d_ada@10.0.0.247 \
  "python C:/Users/d_ada/windows_eos_relay.py --relay-target 100.81.66.31 --relay-port 9000"

# Start Real-Time Eos Monitor Daemon
python .agents/skills/etc-osc-bridge/scripts/eos_realtime_monitor.py --port 9000

# Check live console state
cat .agents/skills/etc-osc-bridge/live_eos_state.json

# Test Art-Net → OSC Bridge
python .agents/skills/etc-osc-bridge/scripts/artnet_to_osc_bridge.py \
  --target-ip 10.0.0.247 --mode chan

# Send OSC command to Eos
python .agents/skills/etc-osc-bridge/scripts/test_osc.py \
  --target-ip 10.0.0.247 --send-port 8000 --cmd "/eos/cmd" --text "Chan 1 At Full Enter"
```

---

*🐺 Wolf Logic — Baked in so you can focus on the show.*
