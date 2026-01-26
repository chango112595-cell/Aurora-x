// @ts-nocheck
import express, { type Request, Response, NextFunction } from "express";
import { createServer } from "http";
import dotenv from "dotenv";
import { registerRoutes, setWebSocketServer } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import AuroraCore from "./aurora-core";
import { registerLuminarRoutes } from "./luminar-routes";
import { registerNexusV3Routes } from "./nexus-v3-routes";
import { createWebSocketServer } from "./websocket-server";
import { getAuroraAI } from "./aurora";
import { bootstrapAuxServices, stopAuxServices } from "./service-bootstrap";
import { enforceSecurityAtStartup } from "./security-validator";
import type { ChildProcess } from "child_process";
import { spawn } from "child_process";

// Load environment variables early (prefer .env.local, then fallback to .env)
dotenv.config({ path: ".env.local" });
dotenv.config();
import os from "os";

interface ServerError extends Error {
  code?: string;
  status?: number;
  statusCode?: number;
}

interface AnalyzeRequest {
  input: string;
  context?: Record<string, unknown>;
}

interface ExecuteRequest {
  command: string;
  parameters?: Record<string, unknown>;
}

interface FixRequest {
  code: string;
  issue: string;
}

interface ChatRequest {
  message: string;
}

interface SynthesizeRequest {
  spec: Record<string, unknown>;
}

const aurora = AuroraCore.getInstance();

const auroraAI = getAuroraAI();
let auxProcesses: ChildProcess[] = [];

const app = express();
const server = createServer(app);

app.set('trust proxy', 1);

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Lightweight health endpoint to satisfy UI pings even if other routers fail
app.get("/api/status", (_req, res) => {
  res.json({ ok: true, message: "Aurora backend online" });
});

// Request logging middleware - log only method/path/status/duration (no response body to prevent secret leakage)
app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      // Only log method, path, status, and duration - never log response body
      // Response bodies can contain tokens, keys, and other sensitive data
      log(`${req.method} ${path} ${res.statusCode} ${duration}ms`);
    }
  });

  next();
});

(async () => {
  // Security validation - will exit with code 1 in production if insecure defaults detected
  enforceSecurityAtStartup();

  const autoStart = process.env.AURORA_AUTO_START !== "0" && process.env.AURORA_AUTO_START !== "false";
  if (autoStart) {
    auxProcesses = await bootstrapAuxServices();
  }

  registerRoutes(app);

  registerLuminarRoutes(app);

  registerNexusV3Routes(app);

  app.get("/api/hardware", (_req: Request, res: Response) => {
    const cpuInfo = os.cpus()?.[0];
    res.json({
      arch: os.arch(),
      platform: os.platform(),
      totalMem: os.totalmem(),
      freeMem: os.freemem(),
      loadAvg: os.loadavg(),
      cpus: {
        count: os.cpus()?.length || 0,
        model: cpuInfo?.model || "unknown",
        speedMHz: cpuInfo?.speed || 0,
      },
    });
  });

  app.get('/api/aurora/status', (_req: Request, res: Response) => {
    res.json(aurora.getStatus());
  });

  app.post('/api/aurora/analyze', async (req: Request, res: Response) => {
    try {
      const { input, context } = req.body as AnalyzeRequest;
      if (!input) {
        return res.status(400).json({ error: 'Input is required' });
      }
      const result = await aurora.analyze(input, context ? JSON.stringify(context) : undefined);
      res.json(result);
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/aurora/execute', async (req: Request, res: Response) => {
    try {
      const { command, parameters } = req.body as ExecuteRequest;
      if (!command) {
        return res.status(400).json({ error: 'Command is required' });
      }
      const result = await aurora.execute(command, parameters);
      res.json(result);
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/aurora/fix', async (req: Request, res: Response) => {
    try {
      const { code, issue } = req.body as FixRequest;
      if (!code || !issue) {
        return res.status(400).json({ error: 'Code and issue are required' });
      }
      const result = await aurora.fix(code, issue);
      res.json(result);
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  app.get('/api/auroraai/status', async (_req: Request, res: Response) => {
    try {
      const status = await auroraAI.getStatus();
      res.json(status);
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/auroraai/chat', async (req: Request, res: Response) => {
    try {
      const { message } = req.body as ChatRequest;
      if (!message) {
        return res.status(400).json({ error: 'Message is required' });
      }
      const response = await auroraAI.handleChat(message);
      res.json({ response, timestamp: new Date().toISOString() });
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  app.post('/api/auroraai/synthesize', async (req: Request, res: Response) => {
    try {
      const { spec } = req.body as SynthesizeRequest;
      if (!spec) {
        return res.status(400).json({ error: 'Spec is required' });
      }
      const result = await auroraAI.synthesize(spec);
      res.json({ result, timestamp: new Date().toISOString() });
    } catch (error: unknown) {
      const err = error as Error;
      res.status(500).json({ error: err.message });
    }
  });

  const wsServer = createWebSocketServer(server);
  setWebSocketServer(wsServer);

  app.use((err: ServerError, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    // Log error safely without exposing sensitive details
    console.error('[Error Middleware]', {
      status,
      message,
      path: _req.path,
      method: _req.method,
      // Don't log full error object to avoid leaking stack traces in production
      ...(process.env.NODE_ENV === 'development' ? { stack: err.stack } : {})
    });

    // Don't send response if headers already sent
    if (res.headersSent) {
      return;
    }

    res.status(status).json({ message });
    // Removed throw err - this was causing server crashes
  });

  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const PORT = parseInt(process.env.PORT || "5000", 10);
  const HOST = "0.0.0.0";

  server.on('error', (err: ServerError) => {
    if (err.code === 'EADDRINUSE') {
      process.exit(1);
    } else {
    }
  });

  process.on('SIGTERM', () => {
    aurora.shutdown();
    auroraAI.shutdown();
    stopAuxServices(auxProcesses);
    server.close(() => {
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    aurora.shutdown();
    auroraAI.shutdown();
    stopAuxServices(auxProcesses);
    server.close(() => {
      process.exit(0);
    });
  });

  server.listen(PORT, HOST, () => {
    log(`serving on port ${PORT}`);
    log(`environment: ${app.get("env")}`);
    log(`access at: http://${HOST}:${PORT}`);
  });
})();
/* @ts-nocheck */
