#!/usr/bin/env node
import { execSync, spawn } from "child_process";
import fs from "fs";
import path from "path";

const PYTHON =
  process.env.AURORA_PYTHON ||
  process.env.PYTHON ||
  process.env.PYTHON_CMD ||
  (process.platform === "win32" ? "python" : "python3");

const SERVICES = {
  backend: "tsx server/index.ts",
  nexus3: `${PYTHON} aurora_nexus_v3/main.py`,
  nexus2: `${PYTHON} tools/luminar_nexus_v2.py serve`,
  core: `${PYTHON} tools/aurora_core.py`,
};

const PID_FILE = path.join(process.cwd(), ".aurora", "launcher_pids.json");

function loadPids() {
  try {
    return JSON.parse(fs.readFileSync(PID_FILE, "utf8"));
  } catch {
    return {};
  }
}

function savePids(pids) {
  fs.mkdirSync(path.dirname(PID_FILE), { recursive: true });
  fs.writeFileSync(PID_FILE, JSON.stringify(pids, null, 2));
}

function isRunning(pid) {
  if (!pid) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function startService(name, command) {
  const child = spawn(command, {
    shell: true,
    detached: true,
    stdio: "inherit",
  });
  child.unref();
  return child.pid;
}

function openBrowser(url) {
  try {
    if (process.env.AURORA_NO_AUTO_OPEN === "1") {
      return;
    }
    const target = url || "http://localhost:5000";
    if (process.platform === "win32") {
      spawn("cmd", ["/c", "start", "", target], {
        detached: true,
        stdio: "ignore",
      }).unref();
    } else if (process.platform === "darwin") {
      spawn("open", [target], { detached: true, stdio: "ignore" }).unref();
    } else {
      spawn("xdg-open", [target], { detached: true, stdio: "ignore" }).unref();
    }
  } catch {
    // Non-fatal if the auto-open fails
  }
}

function stopProcess(pid) {
  if (!pid) return false;
  if (!isRunning(pid)) {
    return true; // already gone; treat as stopped so we can clean stale pids
  }
  try {
    if (process.platform === "win32") {
      execSync(`taskkill /PID ${pid} /T /F`, { stdio: "ignore" });
    } else {
      process.kill(pid, "SIGTERM");
    }
    return true;
  } catch {
    return false;
  }
}

function start() {
  const pids = loadPids();
  for (const [name, command] of Object.entries(SERVICES)) {
    if (isRunning(pids[name])) {
      console.log(`[SKIP] ${name} already running (pid ${pids[name]})`);
      continue;
    }
    const pid = startService(name, command);
    pids[name] = pid;
    console.log(`[START] ${name} (pid ${pid})`);
  }
  savePids(pids);
  openBrowser();
}

function stop() {
  const pids = loadPids();
  const remaining = {};

  for (const [name, pid] of Object.entries(pids)) {
    const stopped = stopProcess(pid);
    const status = stopped ? "STOPPED" : "NOT FOUND";
    console.log(`[${status}] ${name}${pid ? ` (pid ${pid})` : ""}`);
    if (!stopped && pid) {
      remaining[name] = pid;
    }
  }

  savePids(remaining);
}

function status() {
  const pids = loadPids();
  if (Object.keys(pids).length === 0) {
    console.log("No tracked Aurora services are running.");
    return;
  }

  for (const [name, pid] of Object.entries(pids)) {
    const running = isRunning(pid);
    const state = running ? "RUNNING" : "STOPPED";
    console.log(`[${state}] ${name}${pid ? ` (pid ${pid})` : ""}`);
  }
}

const cmd = process.argv[2];

switch (cmd) {
  case "start":
    start();
    break;
  case "stop":
    stop();
    break;
  case "status":
    status();
    break;
  default:
    console.log("Usage: x-start | x-stop | x-status");
}
