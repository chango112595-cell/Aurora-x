
import type { Express } from "express";

/**
 * Luminar Nexus V2 Router
 * Proxies requests to the Luminar Nexus V2 service running on port 5005
 */
export function registerLuminarRoutes(app: Express) {
  const LUMINAR_V2_BASE = "http://0.0.0.0:5005";

  // Health check for Luminar Nexus V2
  app.get("/api/luminar-nexus/v2/health", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/status`);
      const data = await response.json();
      res.json({ ok: true, status: data });
    } catch (error: any) {
      res.status(503).json({ 
        ok: false, 
        error: "Luminar Nexus V2 not available",
        message: error.message 
      });
    }
  });

  // Get comprehensive system status
  app.get("/api/luminar-nexus/v2/status", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/status`);
      if (!response.ok) {
        throw new Error(`V2 returned ${response.status}`);
      }
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "Luminar Nexus V2 unavailable",
        message: error.message 
      });
    }
  });

  // Get service health details
  app.get("/api/luminar-nexus/v2/services/:serviceName", async (req, res) => {
    try {
      const { serviceName } = req.params;
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/health/${serviceName}`);
      if (!response.ok) {
        throw new Error(`Service not found: ${serviceName}`);
      }
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(404).json({ 
        error: "Service not found",
        message: error.message 
      });
    }
  });

  // Restart a service
  app.post("/api/luminar-nexus/v2/services/:serviceName/restart", async (req, res) => {
    try {
      const { serviceName } = req.params;
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/restart/${serviceName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(500).json({ 
        error: "Restart failed",
        message: error.message 
      });
    }
  });

  // Scale a service
  app.post("/api/luminar-nexus/v2/services/:serviceName/scale", async (req, res) => {
    try {
      const { serviceName } = req.params;
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/scale/${serviceName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(500).json({ 
        error: "Scaling failed",
        message: error.message 
      });
    }
  });

  // Get service logs
  app.get("/api/luminar-nexus/v2/logs/:serviceName", async (req, res) => {
    try {
      const { serviceName } = req.params;
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/logs/${serviceName}`);
      if (!response.ok) {
        throw new Error(`Logs not available for ${serviceName}`);
      }
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(404).json({ 
        error: "Logs not available",
        message: error.message 
      });
    }
  });

  // Get quantum mesh status
  app.get("/api/luminar-nexus/v2/quantum", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/quantum`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "Quantum mesh unavailable",
        message: error.message 
      });
    }
  });

  // Get AI insights
  app.get("/api/luminar-nexus/v2/ai/insights", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/ai/insights`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "AI insights unavailable",
        message: error.message 
      });
    }
  });

  // Get security status
  app.get("/api/luminar-nexus/v2/security/status", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/security/status`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "Security status unavailable",
        message: error.message 
      });
    }
  });

  // Get performance metrics
  app.get("/api/luminar-nexus/v2/performance/metrics", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/performance/metrics`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "Performance metrics unavailable",
        message: error.message 
      });
    }
  });

  console.log("✅ Luminar Nexus V2 routes registered");
}
