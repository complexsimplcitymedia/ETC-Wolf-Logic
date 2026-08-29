# ETC OSC Guidelines & Safety Rules

When operating or generating scripts for ETC Eos and TouchOSC OSC integration:

1. **Default Ports**: Always verify RX port `8000` (Eos receive) and TX port `8001`/`3032` (TouchOSC/Eos send) unless configured otherwise.
2. **Network Validation**: Always check IP connectivity and firewall state before attempting live OSC commands.
3. **Safety Notice**: Avoid sending raw `/eos/cmd` "Delete" or "Record" commands automatically without explicit user confirmation.
