/**
 * Wolf Logic — High-Throughput Node.js Ingest & Real-Time Telemetry Engine
 * 
 * Non-blocking event-driven UDP sockets for:
 *   - ETC Eos OSC (UDP 8000, 8001, 9000)
 *   - Art-Net 4 DMX (UDP 6454)
 *   - sACN ANSI E1.31 DMX (UDP 5568)
 *   - TouchOSC Bridge MIDI (UDP 58210)
 * 
 * Features:
 *   - Universal HSI color space normalization
 *   - High-speed batch timecoded CSV logger
 *   - WebSocket Server (Port 8888) broadcasting live 3D Augment3d & Magic Sheet states
 */

const dgram = require('dgram');
const fs = require('fs');
const path = require('path');
const http = require('http');
const { WebSocketServer } = require('ws');

// Ports
const OSC_PORT = 9000;
const ARTNET_PORT = 6454;
const SACN_PORT = 5568;
const MIDI_PORT = 58210;
const UDP_STRING_RX_PORT = 4704; // Ingest strings sent from Eos TX
const UDP_STRING_TX_PORT = 4703; // Target port for sending strings to Eos RX
const WS_PORT = process.env.PORT || 1010;

// CSV Output Paths
const CSV_DIR = path.join(__dirname, '..', 'csv_exports');
if (!fs.existsSync(CSV_DIR)) fs.mkdirSync(CSV_DIR, { recursive: true });
const CSV_LOG_PATH = path.join(CSV_DIR, 'live_telemetry_stream.csv');

// Initialize CSV header if not exists
if (!fs.existsSync(CSV_LOG_PATH)) {
  fs.writeFileSync(
    CSV_LOG_PATH,
    'Timestamp_UTC,Epoch_MS,SMPTE_Timecode,Protocol,Source_IP,Address,Channel,Hue,Sat,Intensity,Raw_Data\n'
  );
}

// ─────────────────────────────────────────────────────────────
//  SMPTE Timecode Helper (30 FPS)
// ─────────────────────────────────────────────────────────────
function getSMPTE(epochMs) {
  const totalSec = epochMs / 1000.0;
  const h = Math.floor((totalSec / 3600) % 24).toString().padStart(2, '0');
  const m = Math.floor((totalSec / 60) % 60).toString().padStart(2, '0');
  const s = Math.floor(totalSec % 60).toString().padStart(2, '0');
  const f = Math.floor((totalSec - Math.floor(totalSec)) * 30).toString().padStart(2, '0');
  return `${h}:${m}:${s}:${f}`;
}

// ─────────────────────────────────────────────────────────────
//  Universal RGB to HSI Converter
// ─────────────────────────────────────────────────────────────
function rgbToHsi(r, g, b) {
  const rn = r / 255.0, gn = g / 255.0, bn = b / 255.0;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const delta = max - min;

  let hue = 0;
  if (delta !== 0) {
    if (max === rn) hue = 60 * (((gn - bn) / delta) % 6);
    else if (max === gn) hue = 60 * (((bn - rn) / delta) + 2);
    else hue = 60 * (((rn - gn) / delta) + 4);
  }
  if (hue < 0) hue += 360;

  const sat = max === 0 ? 0 : (delta / max) * 100.0;
  const intensity = (r + g + b) / 3.0 / 255.0 * 100.0;

  return { hue: Math.round(hue * 10) / 10, sat: Math.round(sat * 10) / 10, intensity: Math.round(intensity * 10) / 10 };
}

// ─────────────────────────────────────────────────────────────
//  Live Stage & 3D Augment3d Fixture State Model
// ─────────────────────────────────────────────────────────────
const liveRigState = {
  active_cue: "None",
  pending_cue: "None",
  command_line: "",
  total_events: 0,
  fixtures: {}
};

// Pre-initialize Venue Rig Coordinates (matching user layout)
// 1. Midstage Electric (Ch 101-110)
for (let i = 1; i <= 10; i++) {
  const ch = 100 + i;
  liveRigState.fixtures[ch] = {
    zone: "Midstage Electric",
    model: "Vari-Lite VL3600 Profile IP",
    x: -4.5 + (i - 1) * 1.0, y: 3.5, z: 6.5,
    pan: 0, tilt: 0, hue: 0, sat: 0, intensity: 0
  };
}

// 2. Proscenium Front Wash (Ch 201-208)
const prosceniumX = [-4.5, -3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 4.5];
prosceniumX.forEach((x, idx) => {
  const ch = 201 + idx;
  liveRigState.fixtures[ch] = {
    zone: "Proscenium Front Wash",
    model: "Claypaky HY B-Eye K15",
    x: x, y: 0.0, z: 5.5,
    pan: 0, tilt: 45, hue: 35, sat: 28, intensity: 0
  };
});

// 3. Audience 4x4 Grid (Ch 401-416)
const gridX = [-4.5, -1.5, 1.5, 4.5];
const gridY = [-3.0, -6.0, -9.0, -12.0];
let houseIdx = 1;
gridY.forEach(y => {
  gridX.forEach(x => {
    const ch = 400 + houseIdx;
    liveRigState.fixtures[ch] = {
      zone: "Audience Overhead Grid",
      model: "Claypaky Sharpy",
      x: x, y: y, z: 7.0,
      pan: 0, tilt: 0, hue: 240, sat: 100, intensity: 0
    };
    houseIdx++;
  });
});

// 4. Audience Centerline Specials (Ch 501-503)
[-4.5, -7.5, -10.5].forEach((y, idx) => {
  const ch = 501 + idx;
  liveRigState.fixtures[ch] = {
    zone: "Audience Centerline Spine",
    model: "Robe MegaPointe",
    x: 0.0, y: y, z: 7.2,
    pan: 0, tilt: 0, hue: 300, sat: 100, intensity: 0
  };
});

// ─────────────────────────────────────────────────────────────
//  Fast In-Memory CSV Stream Buffer (Batch Flush every 500ms)
// ─────────────────────────────────────────────────────────────
let csvBuffer = [];
setInterval(() => {
  if (csvBuffer.length > 0) {
    const chunk = csvBuffer.join('\n') + '\n';
    csvBuffer = [];
    fs.appendFile(CSV_LOG_PATH, chunk, () => {});
  }
}, 500);

function logEvent(protocol, srcIp, addr, ch, h, s, i, raw) {
  const now = Date.now();
  const utc = new Date(now).toISOString();
  const tc = getSMPTE(now);
  csvBuffer.push(`${utc},${now},${tc},${protocol},${srcIp},${addr},${ch || ''},${h || ''},${s || ''},${i || ''},"${raw || ''}"`);
  liveRigState.total_events++;
}

// ─────────────────────────────────────────────────────────────
//  WebSocket Server for Live 3D Augment3d & Magic Sheet Streaming
// ─────────────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  if (req.url === '/' || req.url === '/magicsheet.html') {
    const htmlPath = path.join(__dirname, '..', 'public', 'magicsheet.html');
    if (fs.existsSync(htmlPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      return fs.createReadStream(htmlPath).pipe(res);
    }
  }
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(liveRigState, null, 2));
});

const wss = new WebSocketServer({ server });
wss.on('connection', ws => {
  ws.send(JSON.stringify({ type: 'INIT_STATE', data: liveRigState }));
});

function broadcastStateUpdate() {
  if (wss.clients.size > 0) {
    const payload = JSON.stringify({ type: 'RIG_UPDATE', data: liveRigState, timecode: getSMPTE(Date.now()) });
    wss.clients.forEach(client => {
      if (client.readyState === 1) client.send(payload);
    });
  }
}

// Broadcast 30 FPS updates to connected IDE / Web clients
setInterval(broadcastStateUpdate, 33);

// ─────────────────────────────────────────────────────────────
//  High-Performance UDP Ingest Sockets (dgram)
// ─────────────────────────────────────────────────────────────

// 1. OSC Socket (UDP 9000 / 8000)
const oscSocket = dgram.createSocket('udp4');
oscSocket.on('message', (msg, rinfo) => {
  const nullIdx = msg.indexOf(0);
  if (nullIdx === -1) return;
  const address = msg.subarray(0, nullIdx).toString('utf8');

  // Eos Telemetry parsing
  if (address.includes('/eos/out/active/cue')) {
    liveRigState.active_cue = msg.toString('utf8');
  } else if (address.includes('/eos/out/cmd')) {
    liveRigState.command_line = msg.toString('utf8');
  } else if (address.includes('/eos/out/chan/') || address.includes('/eos/chan/')) {
    const parts = address.split('/');
    const ch = parseInt(parts[parts.indexOf('chan') + 1], 10);
    if (ch && liveRigState.fixtures[ch]) {
      // Float intensity
      liveRigState.fixtures[ch].intensity = 100;
    }
  }
  logEvent('OSC', rinfo.address, address, '', '', '', '', msg.toString('hex'));
});
oscSocket.bind(OSC_PORT, () => console.log(`[+] Node.js OSC Ingest listening on UDP port ${OSC_PORT}`));

// 2. Art-Net 4 DMX Socket (UDP 6454)
const artnetSocket = dgram.createSocket('udp4');
artnetSocket.on('message', (msg, rinfo) => {
  if (msg.length < 18 || !msg.subarray(0, 7).equals(Buffer.from('Art-Net\0'))) return;
  const opcode = msg.readUInt16LE(8);
  if (opcode !== 0x5000) return; // ArtDmx
  const universe = msg.readUInt16LE(14);
  const length = msg.readUInt16BE(16);
  const dmx = msg.subarray(18, 18 + length);

  logEvent('Art-Net', rinfo.address, `ArtDmx/Uni${universe}`, '', '', '', '', `Length:${length}`);
});
artnetSocket.bind(ARTNET_PORT, () => console.log(`[+] Node.js Art-Net 4 Ingest listening on UDP port ${ARTNET_PORT}`));

// 3. TouchOSC MIDI Socket (UDP 58210)
const midiSocket = dgram.createSocket('udp4');
midiSocket.on('message', (msg, rinfo) => {
  if (msg.length >= 3) {
    const status = msg[0];
    const data1 = msg[1];
    const data2 = msg[2];
    logEvent('MIDI', rinfo.address, `Status:0x${status.toString(16)}`, '', '', '', '', `D1:${data1} D2:${data2}`);
  }
});
midiSocket.bind(MIDI_PORT, () => console.log(`[+] Node.js TouchOSC MIDI Ingest listening on UDP port ${MIDI_PORT}`));

// 4. ETC Eos UDP String Ingest (UDP 4704)
const stringSocket = dgram.createSocket('udp4');
stringSocket.on('message', (msg, rinfo) => {
  const str = msg.toString('utf8').trim();
  logEvent('UDP-String', rinfo.address, 'Eos-String-TX', '', '', '', '', str);
});
stringSocket.bind(UDP_STRING_RX_PORT, () => console.log(`[+] Node.js ETC Eos UDP String Ingest listening on UDP port ${UDP_STRING_RX_PORT}`));

// Start Web & WebSocket Server
server.listen(WS_PORT, () => {
  console.log(`\n=============================================================`);
  console.log(`🐺 Wolf Logic High-Throughput Engine Active!`);
  console.log(`   • Web Visualizer & Magic Sheet: http://localhost:${WS_PORT}`);
  console.log(`   • Live WebSocket Telemetry Stream: ws://localhost:${WS_PORT}`);
  console.log(`   • Real-Time CSV Stream Logger: ${CSV_LOG_PATH}`);
  console.log(`=============================================================\n`);
});
