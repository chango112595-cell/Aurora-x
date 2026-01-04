"""
Aurora Pack 12: Toolforge

Production-ready tool creation and management system.
Provides dynamic tool generation, registration, and execution.

Author: Aurora AI System
Version: 2.0.0
"""

import os
import json
import inspect
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading

PACK_ID = "pack12"
PACK_NAME = "Toolforge"
PACK_VERSION = "2.0.0"


class ToolCategory(Enum):
    SYSTEM = "system"
    DATA = "data"
    NETWORK = "network"
    SECURITY = "security"
    AI = "ai"
    UTILITY = "utility"
    CUSTOM = "custom"


class ToolStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


@dataclass
class ToolParameter:
    name: str
    param_type: str
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class ToolDefinition:
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: str = "Any"
    status: ToolStatus = ToolStatus.ACTIVE
    version: str = "1.0.0"
    author: str = "Aurora"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


@dataclass
class ToolExecution:
    execution_id: str
    tool_id: str
    parameters: Dict[str, Any]
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = False


class ToolRegistry:
    def __init__(self, registry_path: str = "/tmp/aurora_toolforge"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.tools: Dict[str, ToolDefinition] = {}
        self.implementations: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        
        self._load_registry()
        self._register_builtin_tools()
    
    def _load_registry(self):
        registry_file = self.registry_path / "tools.json"
        if registry_file.exists():
            data = json.loads(registry_file.read_text())
            for tool_id, tool_data in data.items():
                tool_data["category"] = ToolCategory(tool_data.get("category", "custom"))
                tool_data["status"] = ToolStatus(tool_data.get("status", "active"))
                tool_data["parameters"] = [
                    ToolParameter(**p) for p in tool_data.get("parameters", [])
                ]
                self.tools[tool_id] = ToolDefinition(**tool_data)
    
    def _save_registry(self):
        registry_file = self.registry_path / "tools.json"
        data = {}
        for tool_id, tool in self.tools.items():
            data[tool_id] = {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": [
                    {
                        "name": p.name,
                        "param_type": p.param_type,
                        "required": p.required,
                        "default": p.default,
                        "description": p.description
                    }
                    for p in tool.parameters
                ],
                "returns": tool.returns,
                "status": tool.status.value,
                "version": tool.version,
                "author": tool.author,
                "created_at": tool.created_at,
                "tags": tool.tags
            }
        registry_file.write_text(json.dumps(data, indent=2))
    
    def _register_builtin_tools(self):
        self.register_tool(
            ToolDefinition(
                tool_id="echo",
                name="Echo",
                description="Returns the input unchanged",
                category=ToolCategory.UTILITY,
                parameters=[ToolParameter("message", "str", True, None, "Message to echo")],
                returns="str"
            ),
            lambda message: message
        )
        
        self.register_tool(
            ToolDefinition(
                tool_id="hash",
                name="Hash Generator",
                description="Generates SHA256 hash of input",
                category=ToolCategory.SECURITY,
                parameters=[ToolParameter("data", "str", True, None, "Data to hash")],
                returns="str"
            ),
            lambda data: hashlib.sha256(data.encode()).hexdigest()
        )
        
        self.register_tool(
            ToolDefinition(
                tool_id="timestamp",
                name="Timestamp",
                description="Returns current ISO timestamp",
                category=ToolCategory.UTILITY,
                parameters=[],
                returns="str"
            ),
            lambda: datetime.now().isoformat()
        )
        
        self.register_tool(
            ToolDefinition(
                tool_id="json_validate",
                name="JSON Validator",
                description="Validates if input is valid JSON",
                category=ToolCategory.DATA,
                parameters=[ToolParameter("text", "str", True, None, "JSON text to validate")],
                returns="dict"
            ),
            self._validate_json
        )
        
        self.register_tool(
            ToolDefinition(
                tool_id="file_info",
                name="File Info",
                description="Returns file metadata",
                category=ToolCategory.SYSTEM,
                parameters=[ToolParameter("path", "str", True, None, "File path")],
                returns="dict"
            ),
            self._get_file_info
        )
    
    def _validate_json(self, text: str) -> Dict[str, Any]:
        try:
            data = json.loads(text)
            return {"valid": True, "data": data}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}
    
    def _get_file_info(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {"exists": False, "path": path}
        
        stat = p.stat()
        return {
            "exists": True,
            "path": str(p.absolute()),
            "name": p.name,
            "size_bytes": stat.st_size,
            "is_file": p.is_file(),
            "is_dir": p.is_dir(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def register_tool(self, definition: ToolDefinition, implementation: Callable) -> bool:
        with self._lock:
            self.tools[definition.tool_id] = definition
            self.implementations[definition.tool_id] = implementation
            self._save_registry()
        return True
    
    def unregister_tool(self, tool_id: str) -> bool:
        with self._lock:
            if tool_id in self.tools:
                del self.tools[tool_id]
                if tool_id in self.implementations:
                    del self.implementations[tool_id]
                self._save_registry()
                return True
        return False
    
    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        return self.tools.get(tool_id)
    
    def list_tools(self, category: Optional[ToolCategory] = None,
                   status: Optional[ToolStatus] = None) -> List[ToolDefinition]:
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        if status:
            tools = [t for t in tools if t.status == status]
        
        return tools
    
    def search_tools(self, query: str) -> List[ToolDefinition]:
        query_lower = query.lower()
        return [
            t for t in self.tools.values()
            if query_lower in t.name.lower() or 
               query_lower in t.description.lower() or
               any(query_lower in tag.lower() for tag in t.tags)
        ]


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history: List[ToolExecution] = []
        self._lock = threading.Lock()
        self._execution_counter = 0
    
    def execute(self, tool_id: str, **kwargs) -> ToolExecution:
        with self._lock:
            self._execution_counter += 1
            execution_id = f"exec-{self._execution_counter:08d}"
        
        execution = ToolExecution(
            execution_id=execution_id,
            tool_id=tool_id,
            parameters=kwargs
        )
        
        tool = self.registry.get_tool(tool_id)
        if not tool:
            execution.error = f"Tool not found: {tool_id}"
            execution.success = False
            self._record_execution(execution)
            return execution
        
        if tool.status == ToolStatus.DISABLED:
            execution.error = f"Tool is disabled: {tool_id}"
            execution.success = False
            self._record_execution(execution)
            return execution
        
        implementation = self.registry.implementations.get(tool_id)
        if not implementation:
            execution.error = f"No implementation for tool: {tool_id}"
            execution.success = False
            self._record_execution(execution)
            return execution
        
        validation_error = self._validate_parameters(tool, kwargs)
        if validation_error:
            execution.error = validation_error
            execution.success = False
            self._record_execution(execution)
            return execution
        
        start_time = datetime.now()
        try:
            result = implementation(**kwargs)
            execution.result = result
            execution.success = True
        except Exception as e:
            execution.error = str(e)
            execution.success = False
        
        execution.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self._record_execution(execution)
        
        return execution
    
    def _validate_parameters(self, tool: ToolDefinition, 
                              params: Dict[str, Any]) -> Optional[str]:
        for param in tool.parameters:
            if param.required and param.name not in params:
                if param.default is None:
                    return f"Missing required parameter: {param.name}"
        return None
    
    def _record_execution(self, execution: ToolExecution):
        with self._lock:
            self.execution_history.append(execution)
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
    
    def get_execution(self, execution_id: str) -> Optional[ToolExecution]:
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution
        return None
    
    def get_execution_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.execution_history)
            successful = sum(1 for e in self.execution_history if e.success)
            
            if self.execution_history:
                avg_duration = sum(e.duration_ms for e in self.execution_history) / total
            else:
                avg_duration = 0
            
            return {
                "total_executions": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_duration_ms": avg_duration
            }


class ToolBuilder:
    def __init__(self):
        self.tool_id: Optional[str] = None
        self.name: Optional[str] = None
        self.description: str = ""
        self.category: ToolCategory = ToolCategory.CUSTOM
        self.parameters: List[ToolParameter] = []
        self.returns: str = "Any"
        self.tags: List[str] = []
        self.implementation: Optional[Callable] = None
    
    def with_id(self, tool_id: str) -> 'ToolBuilder':
        self.tool_id = tool_id
        return self
    
    def with_name(self, name: str) -> 'ToolBuilder':
        self.name = name
        return self
    
    def with_description(self, description: str) -> 'ToolBuilder':
        self.description = description
        return self
    
    def with_category(self, category: ToolCategory) -> 'ToolBuilder':
        self.category = category
        return self
    
    def with_parameter(self, name: str, param_type: str, required: bool = True,
                       default: Any = None, description: str = "") -> 'ToolBuilder':
        self.parameters.append(ToolParameter(name, param_type, required, default, description))
        return self
    
    def with_returns(self, returns: str) -> 'ToolBuilder':
        self.returns = returns
        return self
    
    def with_tags(self, *tags: str) -> 'ToolBuilder':
        self.tags.extend(tags)
        return self
    
    def with_implementation(self, func: Callable) -> 'ToolBuilder':
        self.implementation = func
        return self
    
    def build(self) -> tuple:
        if not self.tool_id:
            self.tool_id = hashlib.md5(
                f"{self.name}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
        
        if not self.name:
            self.name = self.tool_id
        
        definition = ToolDefinition(
            tool_id=self.tool_id,
            name=self.name,
            description=self.description,
            category=self.category,
            parameters=self.parameters,
            returns=self.returns,
            tags=self.tags
        )
        
        return definition, self.implementation


class Toolforge:
    def __init__(self, base_dir: str = "/tmp/aurora_toolforge"):
        self.registry = ToolRegistry(base_dir)
        self.executor = ToolExecutor(self.registry)
    
    def register(self, definition: ToolDefinition, implementation: Callable) -> bool:
        return self.registry.register_tool(definition, implementation)
    
    def create_tool(self) -> ToolBuilder:
        return ToolBuilder()
    
    def execute(self, tool_id: str, **kwargs) -> ToolExecution:
        return self.executor.execute(tool_id, **kwargs)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        cat = ToolCategory(category) if category else None
        tools = self.registry.list_tools(category=cat)
        return [
            {
                "id": t.tool_id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "status": t.status.value
            }
            for t in tools
        ]
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        tools = self.registry.search_tools(query)
        return [
            {
                "id": t.tool_id,
                "name": t.name,
                "description": t.description
            }
            for t in tools
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self.registry.tools),
            "categories": {
                cat.value: len([t for t in self.registry.tools.values() 
                               if t.category == cat])
                for cat in ToolCategory
            },
            "execution_stats": self.executor.get_execution_stats()
        }


def get_pack_info():
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "status": "production",
        "components": [
            "ToolRegistry",
            "ToolExecutor",
            "ToolBuilder",
            "Toolforge"
        ],
        "features": [
            "Dynamic tool registration",
            "Fluent tool builder API",
            "Parameter validation",
            "Execution history tracking",
            "Category-based organization",
            "Built-in utility tools"
        ]
    }
