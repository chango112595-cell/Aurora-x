import type { Express } from "express";

/**
 * Luminar Nexus V2 Router
 * Proxies requests to the Luminar Nexus V2 service running on port 8000
 * Returns explicit errors when the service is unavailable (no simulated data).
 */

const LUMINAR_V2_BASE = process.env.LUMINAR_V2_URL || process.env.LUMINAR_URL || "http://0.0.0.0:8000";

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
}
