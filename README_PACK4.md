# PACK 4 — Agents, Memory, Quantum UI, Comm Hub, HAL

Contents:
- /agents: autonomous agents, manager, tools
- /memory: neural memory engine, vector store
- /ui/quantum_ui: single-file UI + FastAPI backend
- /comm/hub: WebRTC signaling + WebSocket fallback
- /hal: driver manager + example driver
- /tools: sandbox runner, trace recorder
- /tests: simple unit tests

Quickstart:
1. Install dependencies (optional performance libs)
   pip install fastapi uvicorn websockets psutil
   # optional: pip install sentence-transformers hnswlib faiss-cpu aiortc aiohttp

2. Start the UI backend:
   python ui/quantum_ui/backend.py

3. Start aurora core (pack1) if not already running:
   python aurora_os.py

4. Run a test:
   python tests/test_agent_run.py

Notes:
- Security: enable sandboxing (containers, resource limits) for tool executors.
- Memory: replace SimpleEmbedder with real embedding model (sentence-transformers).
- WebRTC: to enable, install aiortc and aiohttp; configure TURN/STUN for NAT traversal.
