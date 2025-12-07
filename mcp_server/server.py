#!/usr/bin/env python3
"""
Aurora MCP Server - Model Context Protocol WebSocket Server
Exposes filesystem and process tools for external AI agents like ChatGPT
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [MCP] %(message)s')
logger = logging.getLogger(__name__)

# Import websockets
import websockets


class MCPServer:
    """Model Context Protocol Server with WebSocket transport"""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.clients = set()
        self.request_id = 0
        
        # Define available tools
        self.tools = {
            "fs/read": {
                "name": "fs/read",
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
                "name": "fs/write", 
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
                "name": "fs/list",
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
                "name": "process/run",
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
                "name": "process/exec",
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
    
    async def handle_fs_read(self, params: Dict) -> Dict:
        """Read file contents"""
        try:
            path = self._safe_path(params.get("path", ""))
            if not path.exists():
                return {"error": f"File not found: {params.get('path')}"}
            if not path.is_file():
                return {"error": f"Not a file: {params.get('path')}"}
            
            content = path.read_text(encoding='utf-8', errors='replace')
            return {"content": content, "path": str(path.relative_to(self.workspace_root))}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_fs_write(self, params: Dict) -> Dict:
        """Write content to file"""
        try:
            path = self._safe_path(params.get("path", ""))
            content = params.get("content", "")
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return {"success": True, "path": str(path.relative_to(self.workspace_root)), "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_fs_list(self, params: Dict) -> Dict:
        """List directory contents"""
        try:
            path = self._safe_path(params.get("path", "."))
            recursive = params.get("recursive", False)
            
            if not path.exists():
                return {"error": f"Path not found: {params.get('path')}"}
            if not path.is_dir():
                return {"error": f"Not a directory: {params.get('path')}"}
            
            entries = []
            if recursive:
                for item in path.rglob("*"):
                    if not any(part.startswith('.') for part in item.parts):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append({
                            "path": str(rel_path),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
            else:
                for item in path.iterdir():
                    if not item.name.startswith('.'):
                        rel_path = item.relative_to(self.workspace_root)
                        entries.append({
                            "path": str(rel_path),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
            
            return {"entries": sorted(entries, key=lambda x: x["path"]), "count": len(entries)}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_process_run(self, params: Dict) -> Dict:
        """Run shell command"""
        try:
            command = params.get("command", "")
            timeout = params.get("timeout", 30)
            
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
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "exit_code": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_process_exec(self, params: Dict) -> Dict:
        """Execute program with arguments"""
        try:
            program = params.get("program", "")
            args = params.get("args", [])
            cwd = params.get("cwd", str(self.workspace_root))
            
            if not program:
                return {"error": "No program provided"}
            
            cmd = [program] + args
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "exit_code": proc.returncode
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_request(self, message: Dict) -> Dict:
        """Handle incoming MCP request"""
        method = message.get("method", "")
        params = message.get("params", {})
        request_id = message.get("id")
        
        logger.info(f"Request: {method}")
        
        # MCP Protocol methods
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "aurora-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            
            handlers = {
                "fs/read": self.handle_fs_read,
                "fs/write": self.handle_fs_write,
                "fs/list": self.handle_fs_list,
                "process/run": self.handle_process_run,
                "process/exec": self.handle_process_exec
            }
            
            if tool_name in handlers:
                result = await handlers[tool_name](tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    
    async def handle_connection(self, websocket):
        """Handle WebSocket connection"""
        client_addr = websocket.remote_address
        logger.info(f"Client connected: {client_addr}")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.handle_request(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": str(e)}
                    }
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        finally:
            self.clients.discard(websocket)
    
    async def start(self, host: str = "0.0.0.0", port: int = 8765):
        """Start the MCP WebSocket server"""
        logger.info(f"Starting MCP Server on ws://{host}:{port}")
        
        # Get the public URL for Replit
        replit_url = os.environ.get("REPLIT_DEV_DOMAIN", "")
        repl_slug = os.environ.get("REPL_SLUG", "")
        repl_owner = os.environ.get("REPL_OWNER", "")
        
        if replit_url:
            # Use the dev domain directly (Replit proxies through port 443)
            public_url = f"wss://{replit_url}"
        elif repl_slug and repl_owner:
            public_url = f"wss://{repl_slug}.{repl_owner}.repl.co"
        else:
            public_url = f"ws://{host}:{port}"
        
        print("\n" + "=" * 60)
        print("AURORA MCP SERVER STARTED")
        print("=" * 60)
        print(f"\nLocal:  ws://{host}:{port}")
        print(f"Public: {public_url}")
        print("\nAvailable Tools:")
        for tool in self.tools.values():
            print(f"  - {tool['name']}: {tool['description']}")
        print("\n" + "=" * 60 + "\n")
        
        async with websockets.serve(self.handle_connection, host, port):
            await asyncio.Future()  # Run forever


async def main():
    # Use port 8080 for MCP server (publicly accessible on Replit)
    port = int(os.environ.get("MCP_PORT", "8080"))
    server = MCPServer(workspace_root=os.getcwd())
    await server.start(port=port)


if __name__ == "__main__":
    asyncio.run(main())
