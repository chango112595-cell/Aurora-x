#!/usr/bin/env node
// Production-safe IPC shim. Validates payloads and requires explicit enablement.
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

function requireEnabled() {
  if (process.env.AURORA_IPC_ENABLED !== '1') {
    throw new Error('IPC disabled. Set AURORA_IPC_ENABLED=1 to allow node IPC bridge.');
  }
}

rl.on('line', function (line) {
  try {
    requireEnabled();
    const obj = JSON.parse(line);
    if (typeof obj !== 'object' || obj === null) {
      throw new Error('Payload must be an object');
    }
    const resp = { ok: true, echo: obj, ts: Date.now() };
    console.log(JSON.stringify(resp));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: e.toString() }));
  } finally {
    rl.close();
  }
});
