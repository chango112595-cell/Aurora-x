#!/usr/bin/env node
// installer/node_wrapper.js
const { spawnSync } = require("child_process");
const args = process.argv.slice(2);
function callPython(...a) {
  const p = spawnSync("python3", a, { stdio: "inherit" });
  if (p.error) console.error("Python call failed:", p.error);
  return p.status;
}
if (args[0] === "install") {
  callPython("installer/aurora_installer.py", "install", "--pack", args[1]);
} else {
  console.log("Node installer wrapper: args", args);
}
