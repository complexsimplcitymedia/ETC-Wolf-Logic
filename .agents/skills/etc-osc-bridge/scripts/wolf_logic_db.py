#!/usr/bin/env python3
"""
Wolf Logic — Unified Data Ingest & SQLite Telemetry Engine
Normalizes all ETC Eos data streams (OSC, MIDI, Art-Net, DMX) into a single
SQLite database with timecodes for downstream AI analysis.

Database: wolf_logic_telemetry.db
"""

import sqlite3
import os
import time
from datetime import datetime, timezone
from typing import Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "wolf_logic_telemetry.db")


# ─────────────────────────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

-- Every raw event that arrives from any protocol
CREATE TABLE IF NOT EXISTS console_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,               -- ISO-8601 UTC timestamp
    epoch_ms        INTEGER NOT NULL,               -- Unix epoch milliseconds
    source          TEXT    NOT NULL,               -- 'osc' | 'midi' | 'artnet' | 'sacn'
    source_ip       TEXT,                           -- originating IP address
    protocol_addr   TEXT    NOT NULL,               -- OSC address / MIDI type / DMX ch
    raw_value       TEXT,                           -- raw string representation of value
    float_value     REAL,                           -- numeric value if applicable (0-100 %)
    notes           TEXT                            -- optional human-readable annotation
);

-- Cue fire events parsed from /eos/out/active/cue
CREATE TABLE IF NOT EXISTS cue_executions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    epoch_ms        INTEGER NOT NULL,
    cue_list        INTEGER,
    cue_number      TEXT,                           -- can be '1.5', '10', etc.
    cue_label       TEXT,
    source_event_id INTEGER REFERENCES console_events(id)
);

-- Command line entries from /eos/out/cmd
CREATE TABLE IF NOT EXISTS command_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    epoch_ms        INTEGER NOT NULL,
    command_text    TEXT    NOT NULL,
    source_event_id INTEGER REFERENCES console_events(id)
);

-- Channel intensity snapshots (per-change, not per-frame)
CREATE TABLE IF NOT EXISTS channel_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    epoch_ms        INTEGER NOT NULL,
    channel_num     INTEGER NOT NULL,
    level_pct       REAL    NOT NULL,               -- 0.0 – 100.0
    source          TEXT    NOT NULL,               -- 'osc' | 'artnet' | 'sacn'
    universe        INTEGER,                        -- DMX universe if from Art-Net / sACN
    source_event_id INTEGER REFERENCES console_events(id)
);

-- Patch data (populated when Eos reports fixture info)
CREATE TABLE IF NOT EXISTS patch_data (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_num     INTEGER NOT NULL UNIQUE,
    fixture_type    TEXT,
    fixture_label   TEXT,
    universe        INTEGER,
    dmx_address     INTEGER,
    last_updated    TEXT    NOT NULL
);

-- Session markers (show start/stop, timecode sync points)
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    epoch_ms        INTEGER NOT NULL,
    event_type      TEXT    NOT NULL,               -- 'session_start' | 'session_end' | 'tc_sync'
    label           TEXT,
    metadata        TEXT                            -- JSON blob for extra context
);

-- Indexes for fast time-range queries
CREATE INDEX IF NOT EXISTS idx_events_epoch   ON console_events(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_events_source  ON console_events(source);
CREATE INDEX IF NOT EXISTS idx_cues_epoch     ON cue_executions(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_cmd_epoch      ON command_history(epoch_ms);
CREATE INDEX IF NOT EXISTS idx_chan_num       ON channel_snapshots(channel_num, epoch_ms);
"""


# ─────────────────────────────────────────────────────────────
#  Database Connection
# ─────────────────────────────────────────────────────────────

def get_db(path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a WAL-mode SQLite connection with row factory."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


# ─────────────────────────────────────────────────────────────
#  Timestamp helpers
# ─────────────────────────────────────────────────────────────

def now_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def now_epoch_ms() -> int:
    return int(time.time() * 1000)


# ─────────────────────────────────────────────────────────────
#  Core Ingest API
# ─────────────────────────────────────────────────────────────

class WolfLogicDB:
    """Unified ingest interface for all Wolf Logic data streams."""

    def __init__(self, path: str = DB_PATH):
        self.conn = get_db(path)
        self._log_session("session_start", "Wolf Logic DB initialized")

    # ── Raw event ingestion ──────────────────────────────────

    def ingest(
        self,
        source: str,
        protocol_addr: str,
        raw_value: Optional[str] = None,
        float_value: Optional[float] = None,
        source_ip: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Insert a raw event. Returns the new row ID."""
        ts = now_ts()
        ms = now_epoch_ms()
        cur = self.conn.execute(
            """INSERT INTO console_events
               (ts, epoch_ms, source, source_ip, protocol_addr, raw_value, float_value, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (ts, ms, source, source_ip, protocol_addr, raw_value, float_value, notes),
        )
        self.conn.commit()
        return cur.lastrowid

    # ── Specialized parsers ──────────────────────────────────

    def ingest_osc(self, address: str, args: list, source_ip: str = "127.0.0.1") -> int:
        """Normalize and store an OSC message. Triggers specialized sub-tables."""
        raw = str(args)
        float_val = float(args[0]) if args and isinstance(args[0], (int, float)) else None
        event_id = self.ingest("osc", address, raw_value=raw, float_value=float_val, source_ip=source_ip)

        # Specialized sub-table routing
        if "/eos/out/active/cue" in address:
            self._record_cue(args, event_id)
        elif "/eos/out/cmd" in address:
            self._record_command(args, event_id)
        elif "/eos/out/chan" in address or "/eos/chan" in address:
            parts = address.strip("/").split("/")
            ch_idx = next((i for i, p in enumerate(parts) if p == "chan"), None)
            if ch_idx is not None and ch_idx + 1 < len(parts) and parts[ch_idx + 1].isdigit():
                ch = int(parts[ch_idx + 1])
                lvl = float_val or 0.0
                self._record_channel_snapshot(ch, lvl, "osc", event_id=event_id)
        return event_id

    def ingest_midi(self, msg_type: str, channel: int, cc_or_note: int, value: int,
                    source_ip: str = "127.0.0.1") -> int:
        """Normalize and store a MIDI event."""
        addr = f"midi/{msg_type}/ch{channel}/{cc_or_note}"
        pct = round((value / 127.0) * 100.0, 2)
        return self.ingest("midi", addr, raw_value=str(value), float_value=pct, source_ip=source_ip)

    def ingest_artnet(self, universe: int, channel: int, level: int, source_ip: str = "0.0.0.0") -> int:
        """Normalize and store an Art-Net DMX channel event."""
        addr = f"artnet/uni{universe}/ch{channel}"
        pct = round((level / 255.0) * 100.0, 2)
        event_id = self.ingest("artnet", addr, raw_value=str(level), float_value=pct, source_ip=source_ip)
        self._record_channel_snapshot(channel, pct, "artnet", universe=universe, event_id=event_id)
        return event_id

    def ingest_sacn(self, universe: int, channel: int, level: int, source_ip: str = "0.0.0.0") -> int:
        """Normalize and store a sACN (E1.31) DMX channel event."""
        addr = f"sacn/uni{universe}/ch{channel}"
        pct = round((level / 255.0) * 100.0, 2)
        event_id = self.ingest("sacn", addr, raw_value=str(level), float_value=pct, source_ip=source_ip)
        self._record_channel_snapshot(channel, pct, "sacn", universe=universe, event_id=event_id)
        return event_id

    # ── Sub-table helpers ────────────────────────────────────

    def _record_cue(self, args: list, event_id: int):
        text = " ".join(str(a) for a in args)
        # Try to parse "List X Cue Y" or just a cue number
        cue_list, cue_num = None, text
        parts = text.lower().replace("list", "").replace("cue", "").split()
        nums = [p for p in parts if p.replace(".", "").isdigit()]
        if len(nums) >= 2:
            cue_list, cue_num = int(float(nums[0])), nums[1]
        elif len(nums) == 1:
            cue_num = nums[0]
        self.conn.execute(
            """INSERT INTO cue_executions (ts, epoch_ms, cue_list, cue_number, cue_label, source_event_id)
               VALUES (?,?,?,?,?,?)""",
            (now_ts(), now_epoch_ms(), cue_list, cue_num, text, event_id),
        )
        self.conn.commit()

    def _record_command(self, args: list, event_id: int):
        text = str(args[0]) if args else ""
        if text:
            self.conn.execute(
                """INSERT INTO command_history (ts, epoch_ms, command_text, source_event_id)
                   VALUES (?,?,?,?)""",
                (now_ts(), now_epoch_ms(), text, event_id),
            )
            self.conn.commit()

    def _record_channel_snapshot(self, channel: int, level_pct: float, source: str,
                                  universe: int = None, event_id: int = None):
        self.conn.execute(
            """INSERT INTO channel_snapshots
               (ts, epoch_ms, channel_num, level_pct, source, universe, source_event_id)
               VALUES (?,?,?,?,?,?,?)""",
            (now_ts(), now_epoch_ms(), channel, level_pct, source, universe, event_id),
        )
        self.conn.commit()

    def _log_session(self, event_type: str, label: str = ""):
        self.conn.execute(
            """INSERT INTO sessions (ts, epoch_ms, event_type, label) VALUES (?,?,?,?)""",
            (now_ts(), now_epoch_ms(), event_type, label),
        )
        self.conn.commit()

    # ── Query helpers ────────────────────────────────────────

    def recent_cues(self, limit: int = 10):
        return self.conn.execute(
            "SELECT ts, cue_list, cue_number, cue_label FROM cue_executions ORDER BY epoch_ms DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def recent_commands(self, limit: int = 20):
        return self.conn.execute(
            "SELECT ts, command_text FROM command_history ORDER BY epoch_ms DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def channel_history(self, channel: int, limit: int = 50):
        return self.conn.execute(
            "SELECT ts, level_pct, source FROM channel_snapshots WHERE channel_num=? ORDER BY epoch_ms DESC LIMIT ?",
            (channel, limit),
        ).fetchall()

    def event_count(self) -> dict:
        counts = {}
        for src in ("osc", "midi", "artnet", "sacn"):
            row = self.conn.execute(
                "SELECT COUNT(*) as n FROM console_events WHERE source=?", (src,)
            ).fetchone()
            counts[src] = row["n"]
        return counts

    def close(self):
        self._log_session("session_end", "Wolf Logic DB closed")
        self.conn.close()


# ─────────────────────────────────────────────────────────────
#  CLI: Schema init + quick stats
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    print(f"[+] Initializing Wolf Logic Telemetry DB at: {os.path.abspath(DB_PATH)}")
    db = WolfLogicDB()

    # Inject a few test events to verify the pipeline
    db.ingest_osc("/eos/out/active/cue", ["List 1 Cue 5"], source_ip="10.0.0.247")
    db.ingest_osc("/eos/out/cmd", ["Chan 1 Thru 10 At Full Enter"], source_ip="10.0.0.247")
    db.ingest_osc("/eos/chan/1", [100.0], source_ip="10.0.0.247")
    db.ingest_artnet(0, 5, 200, source_ip="10.0.0.247")
    db.ingest_midi("cc", 1, 7, 127, source_ip="10.0.0.247")

    counts = db.event_count()
    print(f"[+] Event counts by source: {json.dumps(counts, indent=2)}")

    cues = db.recent_cues()
    print(f"[+] Recent cues:")
    for row in cues:
        print(f"    {row['ts']}  →  List {row['cue_list']} Cue {row['cue_number']}")

    cmds = db.recent_commands()
    print(f"[+] Recent commands:")
    for row in cmds:
        print(f"    {row['ts']}  →  {row['command_text']}")

    db.close()
    print("[+] Wolf Logic DB initialized and verified successfully.")
