/**
 * Aurora-X Authentication Integration
 * 
 * This file shows how to integrate authentication into server/index.ts
 * 
 * Add this code to server/index.ts BEFORE the registerRoutes() call:
 */

// ══════════════════════════════════════════════════════════════
// Step 1: Import authentication routes at the top of server/index.ts
// ══════════════════════════════════════════════════════════════

import authRoutes from "./auth-routes";

// ══════════════════════════════════════════════════════════════
// Step 2: Mount auth routes BEFORE registerRoutes()
// ══════════════════════════════════════════════════════════════

// Add this right after: app.use(express.urlencoded({ extended: false }));

// Mount authentication routes
app.use("/api/auth", authRoutes);
console.log("[Auth] Authentication routes mounted at /api/auth");

// ══════════════════════════════════════════════════════════════
// Step 3: (Optional) Protect existing routes
// ══════════════════════════════════════════════════════════════

// Example: Protect synthesis endpoint
import { requireAuth } from "./auth";

// In server/routes.ts, wrap protected routes:
// app.post("/api/nl/compile_full", requireAuth, (req, res) => { ... });
// app.post("/api/corpus", requireAuth, (req, res) => { ... });

// ══════════════════════════════════════════════════════════════
// Complete Integration Example
// ══════════════════════════════════════════════════════════════

/*
import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import authRoutes from "./auth-routes";  // <-- ADD THIS

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Mount authentication routes
app.use("/api/auth", authRoutes);  // <-- ADD THIS
console.log("[Auth] Authentication routes mounted at /api/auth");

// Logging middleware
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
  const server = await registerRoutes(app);

  // Error handler
  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";
    res.status(status).json({ message });
    throw err;
  });

  // Setup Vite or serve static
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const port = parseInt(process.env.PORT || '5000', 10);
  
  server.listen(port, "0.0.0.0", () => {
    log(`serving on port ${port}`);
  });
})();
*/

// ══════════════════════════════════════════════════════════════
// Testing Authentication
// ══════════════════════════════════════════════════════════════

/*
# 1. Register new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. Get profile (replace TOKEN with access token from login)
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TOKEN"

# 4. Admin: List users
curl http://localhost:5000/api/auth/users \
  -H "Authorization: Bearer ADMIN_TOKEN"
*/

// ══════════════════════════════════════════════════════════════
// Environment Variables
// ══════════════════════════════════════════════════════════════

/*
# Add to .env file:
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_EXPIRES_IN=7d
BCRYPT_ROUNDS=12
*/

// ══════════════════════════════════════════════════════════════
// Protecting Existing Routes (Optional)
// ══════════════════════════════════════════════════════════════

// Example from server/routes.ts:
/*
import { requireAuth, requireAdmin, AuthRequest } from "./auth";

// Protect synthesis endpoint (require any authenticated user)
app.post("/api/nl/compile_full", requireAuth, (req: AuthRequest, res) => {
  console.log(`[Synthesis] User ${req.user?.username} starting synthesis...`);
  // ... existing code
});

// Protect corpus write (require authentication)
app.post("/api/corpus", requireAuth, (req: AuthRequest, res) => {
  console.log(`[Corpus] User ${req.user?.username} adding corpus entry...`);
  // ... existing code
});

// Admin-only endpoint
app.post("/api/self-learning/start", requireAuth, requireAdmin, (req, res) => {
  console.log(`[Self-Learning] Admin ${req.user?.username} starting daemon...`);
  // ... existing code
});
*/

export default {
  // This file is for documentation purposes
  // Follow the integration steps above to add authentication to your server
};
