import express, { type Request, Response, NextFunction } from "express";
import { createServer } from "http";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import AuroraCore from "./aurora-core";
import { registerLuminarRoutes } from "./luminar-routes";
import { registerNexusV3Routes } from "./nexus-v3-routes";

// Initialize Aurora Core Intelligence with 188 power units
const aurora = AuroraCore.getInstance();
console.log("[AURORA] ✅ Aurora initialized with 188 power units");
console.log(`[AURORA] Status: ${JSON.stringify(aurora.getStatus(), null, 2)}`);

const app = express();
const server = createServer(app);

// Enable trust proxy for Replit environment (handles X-Forwarded-For correctly)
// Use 1 for single proxy hop (Replit) to avoid express-rate-limit conflicts
app.set('trust proxy', 1);

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  // Register application routes
  registerRoutes(app);

  // Luminar Nexus V2 enabled for ML conversation learning
  registerLuminarRoutes(app);

  // Aurora Nexus V3 routes (port 5002 bridge)
  registerNexusV3Routes(app);

  // Aurora API Routes - Phase 2 Implementation (must be before Vite setup)
  // Route 1: GET /api/aurora/status
  app.get('/api/aurora/status', (_req: Request, res: Response) => {
    res.json(aurora.getStatus());
  });

  // Route 2: POST /api/aurora/analyze
  app.post('/api/aurora/analyze', async (req: Request, res: Response) => {
    try {
      const { input, context } = req.body;
      if (!input) {
        return res.status(400).json({ error: 'Input is required' });
      }
      const result = await aurora.analyze(input, context);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  // Route 3: POST /api/aurora/execute
  app.post('/api/aurora/execute', async (req: Request, res: Response) => {
    try {
      const { command, parameters } = req.body;
      if (!command) {
        return res.status(400).json({ error: 'Command is required' });
      }
      const result = await aurora.execute(command, parameters);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  // Route 4: POST /api/aurora/fix
  app.post('/api/aurora/fix', async (req: Request, res: Response) => {
    try {
      const { code, issue } = req.body;
      if (!code || !issue) {
        return res.status(400).json({ error: 'Code and issue are required' });
      }
      const result = await aurora.fix(code, issue);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // ALWAYS serve the app on the port specified in the environment variable PORT
  // Other ports are firewalled. Default to 5000 if not specified.
  // this serves both the API and the client.
  // It is the only port that is not firewalled.
  const PORT = parseInt(process.env.PORT || "5000", 10);
  const HOST = "0.0.0.0";

  // Ensure clean server startup
  server.on('error', (err: any) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`Port ${PORT} is already in use`);
      process.exit(1);
    } else {
      console.error('Server error:', err);
    }
  });

  // Handle process termination
  process.on('SIGTERM', () => {
    console.log('SIGTERM received, closing server...');
    aurora.shutdown();
    server.close(() => {
      console.log('Server closed');
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    console.log('SIGINT received, closing server...');
    aurora.shutdown();
    server.close(() => {
      console.log('Server closed');
      process.exit(0);
    });
  });

  server.listen(PORT, HOST, () => {
    log(`serving on port ${PORT}`);
    log(`environment: ${app.get("env")}`);
    log(`access at: http://${HOST}:${PORT}`);
    log(`vite hmr ready on wss://${process.env.REPL_SLUG}.${process.env.REPL_OWNER}.repl.co`);
  });
})();