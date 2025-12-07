#!/usr/bin/env python3
"""
Aurora MCP Server - Model Context Protocol Server
Supports both HTTP REST API (for ChatGPT) and WebSocket (for MCP clients)
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
from contextlib import asynccontextmanager
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [MCP] %(message)s')
logger = logging.getLogger(__name__)

# Import FastAPI and related
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import websockets for MCP protocol
import websockets


# ============================================================
# Pydantic Models for HTTP API
# ============================================================

class FileReadRequest(BaseModel):
    path: str


class FileWriteRequest(BaseModel):
    path: str
    content: str


class FileListRequest(BaseModel):
    path: str = "."
    recursive: bool = False


class CommandRunRequest(BaseModel):
    command: str
    timeout: int = 30


class CommandExecRequest(BaseModel):
    program: str
    args: List[str] = []
    cwd: Optional[str] = None


# ============================================================
# WebSocket MCP Server (from user's code)
# ============================================================

async def ws_send(ws, msg):
    await ws.send(json.dumps(msg))

async def ws_handle_request(ws, req):
    method = req.get("method")
    id = req.get("id")

    # File read
    if method == "fs/read":
        path = req["params"]["path"]
        try:
            with open(path, "r") as f:
                data = f.read()
            return {"id": id, "result": {"content": data}}
        except Exception as e:
            return {"id": id, "error": {"message": str(e)}}

    # File write
    if method == "fs/write":
        path = req["params"]["path"]
        content = req["params"]["content"]
        try:
            with open(path, "w") as f:
                f.write(content)
            return {"id": id, "result": {"success": True}}
        except Exception as e:
            return {"id": id, "error": {"message": str(e)}}

    # File list
    if method == "fs/list":
        path = req["params"]["path"]
        try:
            items = os.listdir(path)
            return {"id": id, "result": {"items": items}}
        except Exception as e:
            return {"id": id, "error": {"message": str(e)}}

    # Run a process
    if method == "process/run":
        cmd = req["params"]["cmd"]
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {
                "id": id,
                "result": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            }
        except Exception as e:
            return {"id": id, "error": {"message": str(e)}}

    # Unknown method
    return {
        "id": id,
        "error": {"message": f"Unknown method: {method}"}
    }


async def ws_handler(ws):
    async for message in ws:
        req = json.loads(message)

        if req.get("method") == "initialize":
            await ws_send(ws, {
                "id": req["id"],
                "result": {
                    "protocolVersion": "2024-02-01",
                    "capabilities": {
                        "tools": {
                            "fs/read": {},
                            "fs/write": {},
                            "fs/list": {},
                            "process/run": {}
                        }
                    }
                }
            })
            continue

        response = await ws_handle_request(ws, req)
        if response:
            await ws_send(ws, response)


async def run_websocket_server():
    """Run the WebSocket MCP server on port 9000"""
    print("MCP WebSocket Server running on ws://0.0.0.0:9000")
    async with websockets.serve(ws_handler, "0.0.0.0", 9000):
        await asyncio.Future()  # run forever


# ============================================================
# HTTP REST API Server (for ChatGPT)
# ============================================================

class MCPServer:
    """Model Context Protocol Server with HTTP REST API"""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.clients = set()
        self.request_id = 0
        
        # Define available tools
        self.tools = {
            "fs/read": {
                "name": "fs_read",
                "description": "Read the contents of a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to read"}
                    },
                    "required": ["path"]
                }
            },
            "fs/write": {
                "name": "fs_write", 
                "description": "Write content to a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to write"},
                        "content": {"type": "string", "description": "Content to write to the file"}
                    },
                    "required": ["path", "content"]
                }
            },
            "fs/list": {
                "name": "fs_list",
                "description": "List files and directories in a path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to list", "default": "."},
                        "recursive": {"type": "boolean", "description": "List recursively", "default": False}
                    }
                }
            },
            "process/run": {
                "name": "process_run",
                "description": "Run a shell command and return output",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                    },
                    "required": ["command"]
                }
            },
            "process/exec": {
                "name": "process_exec",
                "description": "Execute a command with arguments",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "program": {"type": "string", "description": "Program to execute"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments"},
                        "cwd": {"type": "string", "description": "Working directory"}
                    },
                    "required": ["program"]
                }
            }
        }
    
    def _safe_path(self, path: str) -> Path:
        """Resolve path safely within workspace"""
        resolved = (self.workspace_root / path).resolve()
        # Security: ensure path is within workspace
        if not str(resolved).startswith(str(self.workspace_root)):
            raise ValueError(f"Path {path} is outside workspace")
        return resolved
    
    async def handle_fs_read(self, path: str) -> Dict:
        """Read file contents"""
        try:
            safe_path = self._safe_path(path)
            if not safe_path.exists():
                return {"error": f"File not found: {path}"}
            if not safe_path.is_file():
                return {"error": f"Not a file: {path}"}
            
            content = safe_path.read_text(encoding='utf-8', errors='replace')
            return {"content": content, "path": str(safe_path.relative_to(self.workspace_root))}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_fs_write(self, path: str, content: str) -> Dict:
        """Write content to file"""
        try:
            safe_path = self._safe_path(path)
            
            # Create parent directories if needed
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content, encoding='utf-8')
            
            return {"success": True, "path": str(safe_path.relative_to(self.workspace_root)), "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_fs_list(self, path: str = ".", recursive: bool = False) -> Dict:
        """List directory contents"""
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return {"error": f"Path not found: {path}"}
            if not safe_path.is_dir():
                return {"error": f"Not a directory: {path}"}
            
            entries = []
            if recursive:
                for item in safe_path.rglob("*"):
                    if not any(part.startswith('.') for part in item.parts):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append({
                            "path": str(rel_path),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
            else:
                for item in safe_path.iterdir():
                    if not item.name.startswith('.'):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append({
                            "path": str(rel_path),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
            
            return {"entries": sorted(entries, key=lambda x: x["path"])[:100], "count": len(entries)}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_process_run(self, command: str, timeout: int = 30) -> Dict:
        """Run shell command"""
        try:
            if not command:
                return {"error": "No command provided"}
            
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_root)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return {
                    "stdout": stdout.decode('utf-8', errors='replace')[:10000],
                    "stderr": stderr.decode('utf-8', errors='replace')[:5000],
                    "exit_code": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_process_exec(self, program: str, args: List[str] = [], cwd: Optional[str] = None) -> Dict:
        """Execute program with arguments"""
        try:
            if not program:
                return {"error": "No program provided"}
            
            work_dir = cwd if cwd else str(self.workspace_root)
            cmd = [program] + args
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            return {
                "stdout": stdout.decode('utf-8', errors='replace')[:10000],
                "stderr": stderr.decode('utf-8', errors='replace')[:5000],
                "exit_code": proc.returncode
            }
        except Exception as e:
            return {"error": str(e)}


# Create MCP server instance
mcp = MCPServer(workspace_root=os.getcwd())

# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - also start WebSocket server in background
    logger.info("Starting Aurora MCP HTTP Server")
    
    # Start WebSocket server in a background task
    ws_task = asyncio.create_task(run_websocket_server())
    
    yield
    
    # Shutdown
    ws_task.cancel()
    logger.info("Shutting down Aurora MCP Servers")

app = FastAPI(
    title="Aurora MCP Server",
    description="Model Context Protocol Server for AI Agents - Provides filesystem and process tools",
    version="1.0.0",
    lifespan=lifespan,
    servers=[
        {"url": "https://993461dc-3757-4f77-8c01-8bec9bddf5ee-00-3su7j9cyl1vd5.picard.replit.dev", "description": "Production server"}
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Server info and available endpoints"""
    return {
        "name": "Aurora MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server for AI Agents",
        "protocols": {
            "http": "Port 8080 - REST API for ChatGPT Actions",
            "websocket": "Port 8000 - WebSocket for MCP clients"
        },
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "GET /tools": "List available tools",
            "POST /fs/read": "Read a file",
            "POST /fs/write": "Write to a file",
            "POST /fs/list": "List directory contents",
            "POST /process/run": "Run a shell command",
            "POST /process/exec": "Execute a program",
            "GET /openapi.json": "OpenAPI schema for ChatGPT"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "server": "aurora-mcp"}


@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {"tools": list(mcp.tools.values())}


@app.post("/fs/read")
async def fs_read(request: FileReadRequest):
    """Read the contents of a file"""
    result = await mcp.handle_fs_read(request.path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/fs/write")
async def fs_write(request: FileWriteRequest):
    """Write content to a file"""
    result = await mcp.handle_fs_write(request.path, request.content)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/fs/list")
async def fs_list(request: FileListRequest):
    """List files and directories"""
    result = await mcp.handle_fs_list(request.path, request.recursive)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/process/run")
async def process_run(request: CommandRunRequest):
    """Run a shell command"""
    result = await mcp.handle_process_run(request.command, request.timeout)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/process/exec")
async def process_exec(request: CommandExecRequest):
    """Execute a program with arguments"""
    result = await mcp.handle_process_exec(request.program, request.args, request.cwd)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


def main():
    """Run the MCP HTTP server (WebSocket starts automatically)"""
    port = int(os.environ.get("MCP_PORT", "9080"))
    
    # Get public URL
    replit_url = os.environ.get("REPLIT_DEV_DOMAIN", "")
    
    print("\n" + "=" * 60)
    print("AURORA MCP SERVER (Standalone)")
    print("=" * 60)
    print("\nHTTP REST API (for ChatGPT):")
    print(f"  Local:  http://0.0.0.0:{port}")
    if replit_url:
        print(f"  Public: https://{replit_url}:{port}")
    print("\nWebSocket MCP Protocol:")
    print("  Local:  ws://0.0.0.0:9000")
    if replit_url:
        print(f"  Public: wss://{replit_url}:9000")
    print("\nEndpoints:")
    print("  POST /fs/read    - Read file contents")
    print("  POST /fs/write   - Write to a file")
    print("  POST /fs/list    - List directory")
    print("  POST /process/run - Run shell command")
    print("  GET  /openapi.json - OpenAPI schema")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
