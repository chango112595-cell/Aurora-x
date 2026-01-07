#!/usr/bin/env python3
"""
Aurora MCP Server - Model Context Protocol Server with HTTP REST API + WebSocket
Exposes filesystem and process tools for external AI clients
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [MCP] %(message)s")
logger = logging.getLogger(__name__)

# Import FastAPI and related
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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
    args: list[str] = []
    cwd: str | None = None


class ConnectionManager:
    """Manages WebSocket connections for MCP protocol"""

    def __init__(self):
        self.active = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active)}")

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active)}")

    async def send_json(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending JSON: {e}")


class MCPServer:
    """Model Context Protocol Server with HTTP REST API + WebSocket"""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.request_id = 0
        self.ws_manager = ConnectionManager()

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
                    "required": ["path"],
                },
            },
            "fs/write": {
                "name": "fs_write",
                "description": "Write content to a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to write"},
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                    },
                    "required": ["path", "content"],
                },
            },
            "fs/list": {
                "name": "fs_list",
                "description": "List files and directories in a path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list",
                            "default": ".",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List recursively",
                            "default": False,
                        },
                    },
                },
            },
            "process/run": {
                "name": "process_run",
                "description": "Run a shell command and return output",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"},
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds",
                            "default": 30,
                        },
                    },
                    "required": ["command"],
                },
            },
            "process/exec": {
                "name": "process_exec",
                "description": "Execute a command with arguments",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "program": {"type": "string", "description": "Program to execute"},
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arguments",
                        },
                        "cwd": {"type": "string", "description": "Working directory"},
                    },
                    "required": ["program"],
                },
            },
        }

    def _safe_path(self, path: str) -> Path:
        """Resolve path safely within workspace"""
        resolved = (self.workspace_root / path).resolve()
        # Security: ensure path is within workspace
        if not str(resolved).startswith(str(self.workspace_root)):
            raise ValueError(f"Path {path} is outside workspace")
        return resolved

    async def handle_fs_read(self, path: str) -> dict:
        """Read file contents"""
        try:
            safe_path = self._safe_path(path)
            if not safe_path.exists():
                return {"error": f"File not found: {path}"}
            if not safe_path.is_file():
                return {"error": f"Not a file: {path}"}

            content = safe_path.read_text(encoding="utf-8", errors="replace")
            return {"content": content, "path": str(safe_path.relative_to(self.workspace_root))}
        except Exception as e:
            return {"error": str(e)}

    async def handle_fs_write(self, path: str, content: str) -> dict:
        """Write content to file"""
        try:
            safe_path = self._safe_path(path)

            # Create parent directories if needed
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content, encoding="utf-8")

            return {
                "success": True,
                "path": str(safe_path.relative_to(self.workspace_root)),
                "bytes_written": len(content),
            }
        except Exception as e:
            return {"error": str(e)}

    async def handle_fs_list(self, path: str = ".", recursive: bool = False) -> dict:
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
                    if not any(part.startswith(".") for part in item.parts):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append(
                            {
                                "path": str(rel_path),
                                "type": "directory" if item.is_dir() else "file",
                                "size": item.stat().st_size if item.is_file() else None,
                            }
                        )
            else:
                for item in safe_path.iterdir():
                    if not item.name.startswith("."):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append(
                            {
                                "path": str(rel_path),
                                "type": "directory" if item.is_dir() else "file",
                                "size": item.stat().st_size if item.is_file() else None,
                            }
                        )

            return {
                "entries": sorted(entries, key=lambda x: x["path"])[:100],
                "count": len(entries),
            }
        except Exception as e:
            return {"error": str(e)}

    async def handle_process_run(self, command: str, timeout: int = 30) -> dict:
        """Run shell command"""
        try:
            if not command:
                return {"error": "No command provided"}

            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_root),
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return {
                    "stdout": stdout.decode("utf-8", errors="replace")[:10000],
                    "stderr": stderr.decode("utf-8", errors="replace")[:5000],
                    "exit_code": proc.returncode,
                }
            except TimeoutError:
                proc.kill()
                return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}

    async def handle_process_exec(
        self, program: str, args: list[str] = [], cwd: str | None = None
    ) -> dict:
        """Execute program with arguments"""
        try:
            if not program:
                return {"error": "No program provided"}

            work_dir = cwd if cwd else str(self.workspace_root)
            cmd = [program] + args
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=work_dir
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            return {
                "stdout": stdout.decode("utf-8", errors="replace")[:10000],
                "stderr": stderr.decode("utf-8", errors="replace")[:5000],
                "exit_code": proc.returncode,
            }
        except Exception as e:
            return {"error": str(e)}

    async def handle_websocket_message(self, websocket: WebSocket, message: dict) -> dict:
        """Handle incoming WebSocket message"""
        msg_type = message.get("type")

        if msg_type == "fs_read":
            path = message.get("path")
            if not path:
                return {"type": "fs_read_error", "error": "missing_path"}
            result = await self.handle_fs_read(path)
            return {"type": "fs_read_resp", **result}

        elif msg_type == "fs_list":
            path = message.get("path", ".")
            recursive = message.get("recursive", False)
            result = await self.handle_fs_list(path, recursive)
            return {"type": "fs_list_resp", **result}

        elif msg_type == "run":
            cmd = message.get("cmd")
            if not cmd:
                return {"type": "run_error", "error": "missing_cmd"}
            timeout = message.get("timeout", 30)
            result = await self.handle_process_run(cmd, timeout)
            return {"type": "run_resp", "cmd": cmd, **result}

        elif msg_type == "fs_write":
            path = message.get("path")
            content = message.get("content", "")
            if not path:
                return {"type": "fs_write_error", "error": "missing_path"}
            result = await self.handle_fs_write(path, content)
            return {"type": "fs_write_resp", **result}

        else:
            return {"type": "error", "error": "unknown_type", "received": msg_type}


# Create MCP server instance
mcp = MCPServer(workspace_root=os.getcwd())


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Aurora MCP HTTP+WebSocket Server")
    yield
    # Shutdown
    logger.info("Shutting down Aurora MCP Server")


app = FastAPI(
    title="Aurora MCP Server",
    description="Model Context Protocol Server - HTTP REST API + WebSocket for AI Agents",
    version="2.0.0",
    lifespan=lifespan,
    servers=[
        {
            "url": "https://993461dc-3757-4f77-8c01-8bec9bddf5ee-00-3su7j9cyl1vd5.picard.replit.dev",
            "description": "Production server",
        }
    ],
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
        "version": "2.0.0",
        "description": "Model Context Protocol Server - HTTP REST API + WebSocket",
        "endpoints": {
            "HTTP": {
                "GET /": "This info",
                "GET /health": "Health check",
                "GET /tools": "List available tools",
                "POST /fs/read": "Read a file",
                "POST /fs/write": "Write to a file",
                "POST /fs/list": "List directory contents",
                "POST /process/run": "Run a shell command",
                "GET /openapi.json": "OpenAPI schema for MCP clients",
            },
            "WebSocket": {
                "WS /mcp": "WebSocket endpoint for MCP protocol - supports fs_read, fs_list, run, fs_write"
            },
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "aurora-mcp",
        "ws_connections": len(mcp.ws_manager.active),
    }


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


@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol"""
    await mcp.ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                response = await mcp.handle_websocket_message(websocket, message)
                await mcp.ws_manager.send_json(websocket, response)
            except json.JSONDecodeError:
                error_response = {"type": "error", "error": "invalid_json"}
                await mcp.ws_manager.send_json(websocket, error_response)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                error_response = {"type": "error", "error": str(e)}
                await mcp.ws_manager.send_json(websocket, error_response)
    except WebSocketDisconnect:
        mcp.ws_manager.disconnect(websocket)


def main():
    """Run the MCP HTTP+WebSocket server"""
    port = int(os.environ.get("MCP_PORT", "8080"))

    # Get public URL
    replit_url = os.environ.get("REPLIT_DEV_DOMAIN", "")

    print("\n" + "=" * 70)
    print("AURORA MCP SERVER - HTTP REST API + WebSocket")
    print("=" * 70)
    print(f"\nLocal:  http://0.0.0.0:{port}")
    if replit_url:
        print(f"Public: https://{replit_url}")
    print("\nHTTP Endpoints for MCP Actions:")
    print("  POST /fs/read    - Read file contents")
    print("  POST /fs/write   - Write to a file")
    print("  POST /fs/list    - List directory")
    print("  POST /process/run - Run shell command")
    print("  GET  /openapi.json - OpenAPI schema")
    print("\nWebSocket for MCP Clients:")
    print("  WS /mcp - Full MCP protocol support")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
