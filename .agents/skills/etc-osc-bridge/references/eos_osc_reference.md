# ETC Eos OSC Command Reference

This document lists standard Open Sound Control (OSC) address patterns supported by the ETC Eos Family software (v3.0+).

## 1. General Control & Command Line

### Execute Command Line Text
- **OSC Address**: `/eos/cmd`
- **Type**: String
- **Examples**:
  - `/eos/cmd` -> `"Chan 1 Thru 10 At Full Enter"`
  - `/eos/cmd` -> `"Go To Cue 1 / 1 Enter"`

### Key Press Emulation
- **OSC Address**: `/eos/key/<key_name>`
- **Examples**:
  - `/eos/key/select_last`
  - `/eos/key/go_0`
  - `/eos/key/stop`
  - `/eos/key/clear_cmd`

### System Ping & Keep-Alive
- **OSC Address**: `/eos/ping`
- **Argument**: Optional string or numeric token.
- **Eos Response**: `/eos/out/ping` with identical token.

---

## 2. Channels & Parameters

| Function | OSC Address Pattern | Data Type | Range / Format |
| :--- | :--- | :--- | :--- |
| **Set Channel Intensity** | `/eos/chan/<chan_num>` | Float / Int | `0` - `100` |
| **Channel Level (Normalized)** | `/eos/chan/<chan_num>/out` | Float | `0.0` - `1.0` |
| **Set Channel Parameter** | `/eos/chan/<chan_num>/param/<param_name>` | Float | e.g. `/eos/chan/1/param/pan` -> `180.0` |
| **Group Selection** | `/eos/group/<group_num>` | Float | Level `0` - `100` |

---

## 3. Cues & Playback

| Function | OSC Address Pattern | Example |
| :--- | :--- | :--- |
| **Fire Cue** | `/eos/cue/<cue_list>/<cue_num>/fire` | `/eos/cue/1/10/fire` |
| **Fire Cue (List 1 default)** | `/eos/cue/<cue_num>/fire` | `/eos/cue/5/fire` |
| **Stop Cue List** | `/eos/cue/<cue_list>/stop` | `/eos/cue/1/stop` |
| **Active Cue Feedback** | `/eos/out/active/cue` | (Eos output to TouchOSC) |
| **Pending Cue Feedback** | `/eos/out/pending/cue` | (Eos output to TouchOSC) |

---

## 4. Submasters & Faders

- **Set Submaster Level**: `/eos/sub/<sub_num>` (Range: `0.0` - `1.0` or `0` - `100`)
- **Fire Submaster Bump**: `/eos/sub/<sub_num>/bump` (Argument `1` = Press, `0` = Release)
- **Fader Bank Control**: `/eos/fader/<bank>/<fader_num>` (Range: `0.0` - `1.0`)

---

## 5. TouchOSC Layout Tips for Eos

1. Use **Labels** mapped to `/eos/out/cmd` to display the active Eos command line live on your mobile / tablet control panel.
2. Use **Faders** mapped to `/eos/fader/1/<1..n>` for multi-fader control.
3. Enable **OSC RX/TX Sync** in TouchOSC preferences to ensure fader positions update automatically when changed on the console.
