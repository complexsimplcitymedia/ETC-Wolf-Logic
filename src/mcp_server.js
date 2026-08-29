#!/usr/bin/env node
/**
 * ==============================================================================
 * Wolf Logic — Official ETC Eos Model Context Protocol (MCP) Server Wrapper
 * ==============================================================================
 * Exposes full ETC Eos console control, OSC command lines, cue execution,
 * color palettes, and real-time SQLite telemetry to any AI agent (Claude,
 * Antigravity, Cursor, or local LLMs) over standard MCP stdio JSON-RPC.
 * ==============================================================================
 */

const dgram = require('dgram');
const readline = require('readline');
const sqlite3 = require('sqlite3');
const path = require('path');
const fs = require('fs');

const EOS_IP = process.env.EOS_IP || '10.0.0.247';
const EOS_PORT = parseInt(process.env.EOS_PORT || '8000', 10);
const DB_PATH = process.env.WOLF_DB_PATH || path.join(__dirname, '..', 'data', 'wolf_logic_telemetry.db');

const oscClient = dgram.createSocket('udp4');

// Minimal OSC String Encoder for /eos/cmd
function createOscStringMessage(address, stringArg) {
  function pad(len) {
    const rem = len % 4;
    return rem === 0 ? 0 : 4 - rem;
  }

  const addrBuf = Buffer.from(address + '\0');
  const addrPad = Buffer.alloc(pad(addrBuf.length));
  
  const typeBuf = Buffer.from(',s\0\0');
  
  const argBuf = Buffer.from(stringArg + '\0');
  const argPad = Buffer.alloc(pad(argBuf.length));

  return Buffer.concat([addrBuf, addrPad, typeBuf, argBuf, argPad]);
}

function sendOscCommand(cmd) {
  return new Promise((resolve, reject) => {
    const packet = createOscStringMessage('/eos/cmd', cmd);
    oscClient.send(packet, EOS_PORT, EOS_IP, (err) => {
      if (err) reject(err);
      else resolve(`Sent: /eos/cmd "${cmd}" to ${EOS_IP}:${EOS_PORT}`);
    });
  });
}

function sendOscAddressOnly(address) {
  return new Promise((resolve, reject) => {
    const addrBuf = Buffer.from(address + '\0');
    const rem = addrBuf.length % 4;
    const pad = rem === 0 ? 0 : 4 - rem;
    const packet = Buffer.concat([addrBuf, Buffer.alloc(pad), Buffer.from(',\0\0\0')]);
    oscClient.send(packet, EOS_PORT, EOS_IP, (err) => {
      if (err) reject(err);
      else resolve(`Sent: ${address} to ${EOS_IP}:${EOS_PORT}`);
    });
  });
}

// Tool Definitions
const TOOLS = [
  {
    name: 'eos_send_command',
    description: 'Execute any native ETC Eos command line syntax directly on the console (e.g. "Chan 1 Thru 10 At Full Enter", "Group 1 Out", "Sneak Enter").',
    inputSchema: {
      type: 'object',
      properties: {
        command: { type: 'string', description: 'ETC Eos command line syntax string.' }
      },
      required: ['command']
    }
  },
  {
    name: 'eos_fire_cue',
    description: 'Fire a specific cue on a specified cue list in ETC Eos.',
    inputSchema: {
      type: 'object',
      properties: {
        cue_list: { type: 'number', default: 1, description: 'Cue list number (Default: 1)' },
        cue_number: { type: 'number', description: 'Cue number to execute (e.g. 5 or 10.5)' }
      },
      required: ['cue_number']
    }
  },
  {
    name: 'eos_recall_color_palette',
    description: 'Recall a calibrated core or gel color palette on selected channels (e.g. CP 9 for 3200K Tungsten, CP 10 for 4400K Cool White, CP 11 for 5600K Daylight Raw).',
    inputSchema: {
      type: 'object',
      properties: {
        channels: { type: 'string', description: 'Channels or group to apply palette to (e.g. "1 Thru 10" or "Group 1")' },
        palette_number: { type: 'number', description: 'Color palette number (1-11 for Core, 101-114 for Gels)' }
      },
      required: ['channels', 'palette_number']
    }
  },
  {
    name: 'eos_set_hsi',
    description: 'Directly set Hue (0-360 deg), Saturation (0-100%), and Intensity (0-100%) on target fixtures.',
    inputSchema: {
      type: 'object',
      properties: {
        channels: { type: 'string', description: 'Target channels (e.g. "Chan 1 Thru 5")' },
        hue: { type: 'number', minimum: 0, maximum: 360, description: 'Hue angle in degrees (0-360)' },
        saturation: { type: 'number', minimum: 0, maximum: 100, description: 'Saturation percentage (0-100)' },
        intensity: { type: 'number', minimum: 0, maximum: 100, description: 'Intensity percentage (0-100)' }
      },
      required: ['channels', 'hue', 'saturation', 'intensity']
    }
  },
  {
    name: 'eos_get_live_telemetry',
    description: 'Query the latest live console state, active cue, recent command lines, and total logged packets from the SQLite telemetry database.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', default: 10, description: 'Number of recent events to return' }
      }
    }
  }
];

// MCP JSON-RPC Server Handler
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', async (line) => {
  if (!line.trim()) return;
  try {
    const request = JSON.parse(line);
    const { id, method, params } = request;

    if (method === 'initialize') {
      const response = {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: {
            name: 'wolf-logic-mcp-server',
            version: '1.0.0'
          }
        }
      };
      console.log(JSON.stringify(response));
      return;
    }

    if (method === 'tools/list') {
      const response = {
        jsonrpc: '2.0',
        id,
        result: { tools: TOOLS }
      };
      console.log(JSON.stringify(response));
      return;
    }

    if (method === 'tools/call') {
      const { name, arguments: args } = params;
      let resultText = '';

      if (name === 'eos_send_command') {
        resultText = await sendOscCommand(args.command);
      } else if (name === 'eos_fire_cue') {
        const list = args.cue_list || 1;
        const cue = args.cue_number;
        resultText = await sendOscAddressOnly(`/eos/cue/${list}/${cue}/fire`);
      } else if (name === 'eos_recall_color_palette') {
        const cmd = `${args.channels} Color_Palette ${args.palette_number} Enter`;
        resultText = await sendOscCommand(cmd);
      } else if (name === 'eos_set_hsi') {
        const cmd = `${args.channels} At ${args.intensity} Hue ${args.hue} Saturation ${args.saturation} Enter`;
        resultText = await sendOscCommand(cmd);
      } else if (name === 'eos_get_live_telemetry') {
        resultText = await new Promise((resolve) => {
          if (!fs.existsSync(DB_PATH)) {
            return resolve(JSON.stringify({ status: 'No database found', path: DB_PATH }));
          }
          const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY);
          db.all(
            `SELECT id, timestamp_utc, smpte_timecode, protocol, address, raw_data 
             FROM console_events ORDER BY id DESC LIMIT ?`,
            [args.limit || 10],
            (err, rows) => {
              db.close();
              if (err) resolve(JSON.stringify({ error: err.message }));
              else resolve(JSON.stringify({ count: rows.length, recent_events: rows }, null, 2));
            }
          );
        });
      } else {
        throw new Error(`Unknown tool: ${name}`);
      }

      const response = {
        jsonrpc: '2.0',
        id,
        result: {
          content: [{ type: 'text', text: resultText }]
        }
      };
      console.log(JSON.stringify(response));
      return;
    }
  } catch (err) {
    const errorResponse = {
      jsonrpc: '2.0',
      id: null,
      error: { code: -32603, message: err.message }
    };
    console.log(JSON.stringify(errorResponse));
  }
});
