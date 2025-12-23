# Aurora-X WASM Runtime (Local Pyodide Build)

This is a **production-ready local WASM wrapper** for running Aurora Python logic
in the browser using a local Pyodide distribution. It does **not** fetch anything
from the internet and can run fully offline.

## 1) Prepare Pyodide locally

Download or vendor Pyodide **outside of this script** and place it in:

```
installers/wasm/pyodide/
  pyodide.js
  pyodide.wasm
  python_stdlib.zip
```

> This is intentionally manual to keep the installer offline and deterministic.

## 2) Start the local WASM host

```bash
./start-wasm-host.sh
```

Then open: `http://localhost:8123`

## 3) What the demo does

- Boots Pyodide from local assets
- Runs a small Python snippet (no network calls)
- Shows status output in the browser

## 4) Production notes

- Serve via your own static host behind HTTPS.
- Bundle the `pyodide/` folder into your deployment artifact.
- If you need API access, proxy requests through your own backend.
