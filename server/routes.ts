import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { corpusStorage } from "./corpus-storage";
import * as path from "path";
import * as fs from "fs";
import {
  corpusEntrySchema,
  corpusQuerySchema,
  topQuerySchema,
  recentQuerySchema,
  similarityQuerySchema,
  runMetaSchema,
  usedSeedSchema,
} from "@shared/schema";

const AURORA_API_KEY = process.env.AURORA_API_KEY || "dev-key-change-in-production";

export async function registerRoutes(app: Express): Promise<Server> {
  // Aurora-X Adaptive Learning Stats endpoints
  app.get("/api/adaptive_stats", (req, res) => {
    try {
      // Import and access the global scheduler if available
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({
          summary: _global_adaptive_scheduler.summary(),
          iteration: _global_adaptive_scheduler.iteration
        });
      } else {
        return res.json({ summary: {}, iteration: 0 });
      }
    } catch (e) {
      return res.json({ summary: {}, iteration: 0 });
    }
  });

  app.get("/api/seed_bias/history", (req, res) => {
    try {
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({ history: _global_adaptive_scheduler.history });
      } else {
        return res.json({ history: [] });
      }
    } catch (e) {
      return res.json({ history: [] });
    }
  });

  app.get("/api/seed_bias", (req, res) => {
    try {
      const { get_seed_store } = require("../aurora_x/learn");
      const seed_store = get_seed_store();
      const summary = seed_store.get_summary();
      
      return res.json({
        summary: {
          total_seeds: summary["total_seeds"],
          avg_bias: Math.round(summary["avg_bias"] * 10000) / 10000,
          max_bias: Math.round(summary["max_bias"] * 10000) / 10000,
          min_bias: Math.round(summary["min_bias"] * 10000) / 10000,
          total_updates: summary["total_updates"],
          config: summary["config"]
        },
        top_biases: (summary["top_biases"] || []).map(([key, bias]) => ({
          seed_key: key,
          bias: Math.round(bias * 10000) / 10000
        }))
      });
    } catch (e: any) {
      return res.status(500).json({ error: "Internal error", details: e?.message ?? String(e) });
    }
  });
  app.post("/api/corpus", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const entry = corpusEntrySchema.parse(req.body);
      corpusStorage.insertEntry(entry);
      return res.json({ ok: true, id: entry.id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus", (req, res) => {
    try {
      const query = corpusQuerySchema.parse(req.query);
      const items = corpusStorage.getEntries({
        func: query.func,
        limit: query.limit,
        offset: query.offset,
        perfectOnly: query.perfectOnly,
        minScore: query.minScore,
        maxScore: query.maxScore,
        startDate: query.startDate,
        endDate: query.endDate,
      });
      return res.json({ items, hasMore: items.length === query.limit });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/top", (req, res) => {
    try {
      const query = topQuerySchema.parse(req.query);
      const items = corpusStorage.getTopByFunc(query.func, query.limit);
      return res.json({ items });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/recent", (req, res) => {
    try {
      const query = recentQuerySchema.parse(req.query);
      const items = corpusStorage.getRecent(query.limit);
      return res.json({ items });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/corpus/similar", (req, res) => {
    try {
      const query = similarityQuerySchema.parse(req.body);
      const results = corpusStorage.getSimilar(
        query.targetSigKey,
        query.targetPostBow,
        query.limit
      );
      return res.json({ results });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/run-meta", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const meta = runMetaSchema.parse(req.body);
      corpusStorage.insertRunMeta(meta);
      return res.json({ ok: true, run_id: meta.run_id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/run-meta/latest", (req, res) => {
    try {
      const meta = corpusStorage.getLatestRunMeta();
      return res.json({ meta });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/used-seeds", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const seed = usedSeedSchema.parse(req.body);
      const id = corpusStorage.insertUsedSeed(seed);
      return res.json({ ok: true, id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/used-seeds", (req, res) => {
    try {
      const run_id = req.query.run_id as string | undefined;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 200;
      const seeds = corpusStorage.getUsedSeeds({ run_id, limit });
      return res.json({ seeds });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  // Chat endpoint for Aurora-X synthesis requests
  app.post("/api/chat", async (req, res) => {
    try {
      const { message } = req.body;
      
      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      // Parse the user's request to determine synthesis parameters
      const lowerMessage = message.toLowerCase();
      
      // Determine the type of code to generate
      let responseMessage = "I'll synthesize that code for you using Aurora-X. ";
      let code = "";
      let language = "python";

      // Example responses based on keywords - in production this would call Aurora-X
      if (lowerMessage.includes("rest") || lowerMessage.includes("api")) {
        responseMessage += "Here's a RESTful API implementation with CRUD operations:";
        code = `from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# Data model
class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    completed: bool = False

# In-memory storage
tasks_db = {}

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    task.id = str(uuid.uuid4())
    tasks_db[task.id] = task
    return task

@app.get("/tasks/", response_model=List[Task])
async def read_tasks():
    return list(tasks_db.values())

@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task.id = task_id
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"detail": "Task deleted"}`;
      } else if (lowerMessage.includes("auth") || lowerMessage.includes("jwt")) {
        responseMessage += "Here's a secure JWT authentication system:";
        code = `import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)
        
        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=7)
        
        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None`;
      } else if (lowerMessage.includes("websocket") || lowerMessage.includes("real-time")) {
        responseMessage += "Here's a WebSocket server implementation with room management:";
        language = "javascript";
        code = `const WebSocket = require('ws');

class WebSocketServer {
  constructor() {
    this.wss = new WebSocket.Server({ port: 8080 });
    this.rooms = new Map();
    this.clients = new Map();
    
    this.wss.on('connection', (ws) => this.handleConnection(ws));
  }

  handleConnection(ws) {
    const clientId = this.generateId();
    this.clients.set(ws, { id: clientId, room: null });

    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        this.handleMessage(ws, data);
      } catch (err) {
        ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
      }
    });

    ws.on('close', () => this.handleDisconnect(ws));
    ws.send(JSON.stringify({ type: 'connected', clientId }));
  }

  handleMessage(ws, data) {
    const client = this.clients.get(ws);
    
    switch (data.type) {
      case 'join':
        this.joinRoom(ws, data.room);
        break;
      case 'leave':
        this.leaveRoom(ws);
        break;
      case 'message':
        this.broadcastToRoom(client.room, {
          type: 'message',
          from: client.id,
          content: data.content,
          timestamp: new Date().toISOString()
        }, ws);
        break;
    }
  }

  joinRoom(ws, roomId) {
    this.leaveRoom(ws); // Leave current room if any
    
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, new Set());
    }
    
    this.rooms.get(roomId).add(ws);
    const client = this.clients.get(ws);
    client.room = roomId;
    
    // Notify others in the room
    this.broadcastToRoom(roomId, {
      type: 'user_joined',
      userId: client.id,
      room: roomId
    }, ws);
    
    ws.send(JSON.stringify({
      type: 'joined',
      room: roomId,
      users: this.getRoomUsers(roomId)
    }));
  }

  leaveRoom(ws) {
    const client = this.clients.get(ws);
    if (!client.room) return;
    
    const room = this.rooms.get(client.room);
    if (room) {
      room.delete(ws);
      if (room.size === 0) {
        this.rooms.delete(client.room);
      } else {
        this.broadcastToRoom(client.room, {
          type: 'user_left',
          userId: client.id
        }, ws);
      }
    }
    
    client.room = null;
  }

  broadcastToRoom(roomId, message, exclude = null) {
    const room = this.rooms.get(roomId);
    if (!room) return;
    
    const data = JSON.stringify(message);
    room.forEach(client => {
      if (client !== exclude && client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  }

  getRoomUsers(roomId) {
    const room = this.rooms.get(roomId);
    if (!room) return [];
    
    return Array.from(room).map(ws => {
      const client = this.clients.get(ws);
      return client ? client.id : null;
    }).filter(Boolean);
  }

  handleDisconnect(ws) {
    this.leaveRoom(ws);
    this.clients.delete(ws);
  }

  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
}

// Start server
const server = new WebSocketServer();
console.log('WebSocket server running on port 8080');`;
      } else {
        // Default response for general requests
        responseMessage += "Let me generate a solution for your request:";
        code = `# Aurora-X Synthesis Result
# Specification: ${message}

def synthesized_function():
    """
    This function was synthesized based on your requirements.
    Aurora-X analyzes the specification and generates optimal code.
    """
    # Implementation would be generated here based on the specification
    # The actual synthesis engine would analyze requirements and produce
    # working code that meets the specified constraints
    
    result = {
        'status': 'synthesized',
        'specification': '''${message}''',
        'confidence': 0.95,
        'test_coverage': 1.0
    }
    
    return result

# Example usage
if __name__ == "__main__":
    output = synthesized_function()
    print(f"Synthesis complete: {output}")`;
      }

      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 800));

      return res.json({
        message: responseMessage,
        code: code,
        language: language,
        synthesis_id: `aurora-${Date.now()}`,
        timestamp: new Date().toISOString()
      });
    } catch (error: any) {
      console.error("Chat API error:", error);
      return res.status(500).json({
        error: "Failed to process synthesis request",
        details: error?.message
      });
    }
  });

  // Serve the tracker visual HTML
  app.get("/tracker-visual", (req, res) => {
    const trackerPath = path.join(process.cwd(), "tracker_visual.html");
    if (fs.existsSync(trackerPath)) {
      res.sendFile(trackerPath);
    } else {
      res.status(404).send("Tracker visual not found");
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
