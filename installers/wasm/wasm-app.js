const status = document.getElementById("status");
const output = document.getElementById("output");

async function main() {
  try {
    status.textContent = "Loading local Pyodide...";
    const pyodide = await loadPyodide({
      indexURL: "./pyodide/",
    });

    status.textContent = "Running Aurora-X WASM demo...";
    const code = `
import time
result = {
    "status": "ok",
    "message": "Aurora-X WASM runtime initialized",
    "timestamp": time.time(),
}
result
    `;
    const result = pyodide.runPython(code);
    output.textContent = JSON.stringify(result, null, 2);
    status.textContent = "Ready";
  } catch (error) {
    status.textContent = "Failed to load Pyodide";
    output.textContent = error.toString();
  }
}

await main();
