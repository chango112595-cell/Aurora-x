#!/usr/bin/env node
import { execSync } from "child_process";

const cmd = process.argv[2];

const SERVICES = {
  backend: "tsx server/index.ts",
  nexus3: "python3 aurora_nexus_v3/main.py",
  nexus2: "python3 tools/luminar_nexus_v2.py serve",
  core: "python3 tools/aurora_core.py"
};

function start() {
  for (const [name, command] of Object.entries(SERVICES)) {
    console.log(`[START] ${name}`);
    execSync(`${command} &`, { stdio: "inherit" });
  }
}

function stop() {
  execSync("pkill -f 'tsx server/index.ts' || true");
  execSync("pkill -f aurora_nexus_v3 || true");
  execSync("pkill -f luminar_nexus_v2 || true");
  execSync("pkill -f aurora_core.py || true");
}

function status() {
  execSync("ps aux | grep -E 'tsx|nexus|aurora_core' | grep -v grep", {
    stdio: "inherit",
  });
}

switch (cmd) {
  case "start": start(); break;
  case "stop": stop(); break;
  case "status": status(); break;
  default:
    console.log("Usage: x-start | x-stop | x-status");
}
