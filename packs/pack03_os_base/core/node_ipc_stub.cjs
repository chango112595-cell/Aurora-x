#!/usr/bin/env node
// node_ipc_stub.js - reads JSON line from stdin, replies with modified JSON
const readline = require('readline');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });
rl.on('line', function(line){
    try {
        const obj = JSON.parse(line);
        const resp = { ok: true, echo: obj, ts: Date.now() };
        console.log(JSON.stringify(resp));
    } catch(e){
        console.log(JSON.stringify({ok:false, error: e.toString()}));
    }
    rl.close();
});
