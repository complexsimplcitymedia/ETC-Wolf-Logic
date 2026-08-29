# DMX512 over IP Reference: sACN (ANSI E1.31) & Art-Net 4

This reference document outlines DMX-over-IP protocol specifications, network port definitions, universe layout, and ETC Eos patch settings.

---

## 1. sACN (Streaming ACN / ANSI E1.31)

**sACN (Streaming ACN)** is the primary lighting control network protocol used by ETC Eos family consoles, gateways, and fixtures.

### Protocol Parameters
- **Transport**: UDP Multicast or Unicast
- **Port**: `5568`
- **Universe Range**: `1` to `63999`
- **Channels per Universe**: 512 DMX channels (Slots 1–512)
- **Multicast IP Group Formula**: `239.255.<Universe_High_Byte>.<Universe_Low_Byte>`
  - *Example*: Universe 1 -> `239.255.0.1`
  - *Example*: Universe 256 -> `239.255.1.0`

### Priority Levels
- **Range**: `0` to `200` (Default: `100`).
- Higher priority streams supersede lower priority streams. Equal priorities merge via Highest-Takes-Precedence (HTP).

---

## 2. Art-Net 4

**Art-Net** is an Ethernet protocol based on UDP for transferring DMX512 lighting data.

### Protocol Parameters
- **Transport**: UDP Broadcast or Unicast
- **Port**: `6454`
- **Universe Range**: `0` to `32767` (Sub-Net & Universe bits)
- **OpCodes**:
  - `0x5000` (ArtDmx): DMX frame transmission
  - `0x2000` (ArtPoll): Node discovery request
  - `0x2100` (ArtPollReply): Node discovery response

---

## 3. ETC Eos DMX Output Settings

1. Open Eos **Setup**: `Display` -> `Setup` -> `System` -> `Network`.
2. Under **Output Protocols**:
   - Enable **sACN** (Set to *Draft* or *Standard ANSI E1.31*).
   - Set **sACN Volume / Priority** defaults.
   - Enable **Art-Net** if required by legacy fixtures or 3rd party visualizers (e.g. Capture, Unreal Engine, L8).
3. **Patching DMX Universes**:
   - In Eos Patch: Address syntax is `<Universe>/<Address>` (e.g., `1/1` for Universe 1 Channel 1, `2/51` for Universe 2 Channel 51).
