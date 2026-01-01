
===============================
AURORA MCP SERVER BUNDLE
===============================

This bundle contains a complete MCP-compatible FastAPI + WebSocket server.

INCLUDED FILES:
- mcp_server.py
- requirements.txt
- README_RUN.txt

INSTRUCTIONS (REPLIT):

1. Upload the bundle into your Replit project
2. Install dependencies:
   python3 -m pip install -r requirements.txt

3. Start the server:
   uvicorn mcp_server:app --host 0.0.0.0 --port $PORT

4. Access URLs (example):
   HTTP:  https://<your-repl>.replit.dev/
   WS:    wss://<your-repl>.replit.dev/mcp

Only YOU have access to this MCP server.
It uses your unique Replit subdomain.
