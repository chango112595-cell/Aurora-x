// @ts-nocheck
import type { Express } from "express";
import { getAuroraAI } from "./aurora";

/**
 * Luminar Nexus Router
 * Proxies requests to Luminar Nexus V2 (port 5005) and V3 (port 5031) services
 * Also provides unified status endpoints for the Aurora Bridge integration
 */
const LUMINAR_V2_BASE = process.env.LUMINAR_V2_URL || process.env.LUMINAR_URL || "http://127.0.0.1:8000";
const LUMINAR_V3_BASE = process.env.LUMINAR_NEXUS_V3_URL || "http://0.0.0.0:5031";
const AURORA_BRIDGE_BASE = process.env.AURORA_BRIDGE_URL || "http://0.0.0.0:5001";

async function requestV2(path: string, options: RequestInit = {}) {
  const res = await fetch(`${LUMINAR_V2_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }

  return res.json();
}

function respondUnavailable(res: any, error: unknown, path: string) {
  const message = error instanceof Error ? error.message : "Luminar Nexus V2 unavailable";
  res.status(503).json({
    available: false,
    error: message,
    path
  });
}

export function registerLuminarRoutes(app: Express) {
  app.get("/api/luminar-nexus/v2/health", async (_req, res) => {
    try {
      const data = await requestV2("/api/nexus/status");
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, "/api/nexus/status");
    }
  });

  app.get("/api/luminar-nexus/v2/status", async (_req, res) => {
    try {
      const data = await requestV2("/api/nexus/status");
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, "/api/nexus/status");
    }
  });

  app.get("/api/luminar-nexus/v2/services/:serviceName", async (req, res) => {
    const { serviceName } = req.params;
    try {
      const data = await requestV2(`/api/nexus/health/${encodeURIComponent(serviceName)}`);
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, `/api/nexus/health/${serviceName}`);
    }
  });

  app.post("/api/luminar-nexus/v2/services/:serviceName/restart", async (req, res) => {
    const { serviceName } = req.params;
    try {
      const data = await requestV2(`/api/nexus/restart/${encodeURIComponent(serviceName)}`, {
        method: "POST"
      });
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, `/api/nexus/restart/${serviceName}`);
    }
  });

  app.post("/api/luminar-nexus/v2/services/:serviceName/scale", async (req, res) => {
    const { serviceName } = req.params;
    try {
      const data = await requestV2(`/api/nexus/scale/${encodeURIComponent(serviceName)}`, {
        method: "POST"
      });
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, `/api/nexus/scale/${serviceName}`);
    }
  });

  app.get("/api/luminar-nexus/v2/logs/:serviceName", async (req, res) => {
    const { serviceName } = req.params;
    try {
      const data = await requestV2(`/api/nexus/logs/${encodeURIComponent(serviceName)}`);
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, `/api/nexus/logs/${serviceName}`);
    }
  });

  app.get("/api/luminar-nexus/v2/quantum", async (_req, res) => {
    try {
      const data = await requestV2("/api/nexus/quantum");
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, "/api/nexus/quantum");
    }
  });

  app.get("/api/luminar-nexus/v2/ai/insights", async (_req, res) => {
    try {
      const data = await requestV2("/api/nexus/ai/insights");
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, "/api/nexus/ai/insights");
    }
  });

  app.get("/api/luminar-nexus/v2/security/status", async (_req, res) => {
    try {
      const data = await requestV2("/api/nexus/security/status");
      res.json({ ...data, available: true });
    } catch (error) {
      respondUnavailable(res, error, "/api/nexus/security/status");
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

    // Prefer Aurora AI direct response (diagnostics/performance-aware)
    try {
      const auroraAI = getAuroraAI();
      const response = await auroraAI.handleChat(message);
      return res.json({
        ok: true,
        response,
        message: response,
        session_id: sessionId,
        ai_powered: true,
        source: 'aurora_ai'
      });
    } catch (err: any) {
      console.warn('[Luminar Routes] Aurora AI handler failed, falling back to Luminar/Bridge:', err?.message || err);
    }

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
/* @ts-nocheck */
