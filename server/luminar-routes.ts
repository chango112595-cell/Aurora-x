
import type { Express } from "express";

/**
 * Luminar Nexus Router
 * Proxies requests to Luminar Nexus V2 (port 5005) and V3 (port 5031) services
 * Also provides unified status endpoints for the Aurora Bridge integration
 */
export function registerLuminarRoutes(app: Express) {
  const LUMINAR_V2_BASE = process.env.LUMINAR_NEXUS_V2_URL || "http://0.0.0.0:5005";
  const LUMINAR_V3_BASE = process.env.LUMINAR_NEXUS_V3_URL || "http://0.0.0.0:5031";
  const AURORA_BRIDGE_BASE = process.env.AURORA_BRIDGE_URL || "http://0.0.0.0:5001";

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

  // ════════════════════════════════════════════════════════════════════════════
  // LUMINAR NEXUS V3 ROUTES - Universal Consciousness System
  // ════════════════════════════════════════════════════════════════════════════

  // Health check for Luminar Nexus V3
  app.get("/api/luminar-nexus/v3/health", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V3_BASE}/api/nexus/status`);
      const data = await response.json();
      res.json({ ok: true, status: data, version: "3.0.0" });
    } catch (error: any) {
      res.status(503).json({ 
        ok: false, 
        error: "Luminar Nexus V3 not available",
        message: error.message,
        version: "3.0.0"
      });
    }
  });

  // Get comprehensive V3 system status
  app.get("/api/luminar-nexus/v3/status", async (req, res) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${LUMINAR_V3_BASE}/api/nexus/status`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`V3 returned ${response.status}`);
      }
      const data = await response.json();
      res.json({
        version: "3.0.0",
        active: true,
        ...data
      });
    } catch (error: any) {
      res.status(503).json({ 
        error: "Luminar Nexus V3 unavailable",
        message: error.message,
        version: "3.0.0",
        active: false
      });
    }
  });

  // V3 Port management
  app.get("/api/luminar-nexus/v3/ports", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V3_BASE}/api/nexus/ports`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "V3 Port info unavailable",
        message: error.message 
      });
    }
  });

  // V3 Services list
  app.get("/api/luminar-nexus/v3/services", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V3_BASE}/api/services`);
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        error: "V3 Services list unavailable",
        message: error.message 
      });
    }
  });

  // V3 Service details
  app.get("/api/luminar-nexus/v3/services/:serviceName", async (req, res) => {
    try {
      const { serviceName } = req.params;
      const response = await fetch(`${LUMINAR_V3_BASE}/api/services/${serviceName}`);
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

  // ════════════════════════════════════════════════════════════════════════════
  // UNIFIED STATUS AND BRIDGE ROUTES
  // ════════════════════════════════════════════════════════════════════════════

  // Unified status for all Luminar Nexus versions and Aurora Bridge
  app.get("/api/luminar-nexus/unified/status", async (req, res) => {
    const status = {
      v2: { active: false, version: "2.0.0", status: null as any, error: null as any },
      v3: { active: false, version: "3.0.0", status: null as any, error: null as any },
      bridge: { active: false, status: null as any, error: null as any },
      timestamp: new Date().toISOString()
    };

    // Check V2
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const v2Response = await fetch(`${LUMINAR_V2_BASE}/api/nexus/status`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (v2Response.ok) {
        status.v2.active = true;
        status.v2.status = await v2Response.json();
      }
    } catch (error: any) {
      status.v2.error = error.message;
    }

    // Check V3
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const v3Response = await fetch(`${LUMINAR_V3_BASE}/api/nexus/status`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (v3Response.ok) {
        status.v3.active = true;
        status.v3.status = await v3Response.json();
      }
    } catch (error: any) {
      status.v3.error = error.message;
    }

    // Check Aurora Bridge
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const bridgeResponse = await fetch(`${AURORA_BRIDGE_BASE}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (bridgeResponse.ok) {
        status.bridge.active = true;
        status.bridge.status = await bridgeResponse.json();
      }
    } catch (error: any) {
      status.bridge.error = error.message;
    }

    res.json(status);
  });

  // Route chat through the best available service
  app.post("/api/luminar-nexus/chat", async (req, res) => {
    const { message, session_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    const sessionId = session_id || 'api-default';

    // Try V2 first (AI orchestration)
    try {
      const v2Response = await fetch(`${LUMINAR_V2_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
        signal: AbortSignal.timeout(5000)
      });
      if (v2Response.ok) {
        const data = await v2Response.json();
        return res.json({
          ...data,
          source: 'luminar-nexus-v2'
        });
      }
    } catch (error) {
      console.log('[Luminar Routes] V2 chat unavailable');
    }

    // Try V3 (universal consciousness)
    try {
      const v3Response = await fetch(`${LUMINAR_V3_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
        signal: AbortSignal.timeout(5000)
      });
      if (v3Response.ok) {
        const data = await v3Response.json();
        return res.json({
          ...data,
          source: 'luminar-nexus-v3'
        });
      }
    } catch (error) {
      console.log('[Luminar Routes] V3 chat unavailable');
    }

    // Try Aurora Bridge
    try {
      const bridgeResponse = await fetch(`${AURORA_BRIDGE_BASE}/api/bridge/nl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: message, session_id: sessionId }),
        signal: AbortSignal.timeout(10000)
      });
      if (bridgeResponse.ok) {
        const data = await bridgeResponse.json();
        return res.json({
          response: data.response || data.result || data.message,
          source: 'aurora-bridge',
          session_id: sessionId
        });
      }
    } catch (error) {
      console.log('[Luminar Routes] Bridge chat unavailable');
    }

    // All services unavailable
    res.status(503).json({
      error: "All Luminar Nexus services unavailable",
      message: "Please ensure Luminar Nexus V2 (port 5005), V3 (port 5031), or Aurora Bridge (port 5001) is running",
      session_id: sessionId
    });
  });

  console.log("✅ Luminar Nexus V2 routes registered");
  console.log("✅ Luminar Nexus V3 routes registered");
  console.log("✅ Unified status and chat routes registered");
}
