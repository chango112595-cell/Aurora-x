import type { Express } from "express";

const NEXUS_V3_BASE = "http://0.0.0.0:5002";

export function registerNexusV3Routes(app: Express) {
  
  app.get("/api/nexus-v3/health", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/health`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json({ ok: true, ...data });
    } catch (error: any) {
      res.status(503).json({ 
        ok: false, 
        error: "Aurora Nexus V3 not available",
        message: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/status", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/status`, {
        signal: AbortSignal.timeout(5000)
      });
      if (!response.ok) {
        throw new Error(`Nexus V3 returned ${response.status}`);
      }
      const data = await response.json();
      res.json({ connected: true, ...data });
    } catch (error: any) {
      res.status(503).json({ 
        connected: false,
        error: "Aurora Nexus V3 unavailable",
        message: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/modules", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/modules`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        modules: [],
        count: 0,
        error: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/capabilities", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/capabilities`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        workers: 0,
        tiers: 0,
        aems: 0,
        modules: 0,
        error: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/packs", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/packs`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        total_packs: 0,
        loaded_packs: 0,
        packs: {},
        error: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/manifest", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/manifest`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        tiers: 0,
        aems: 0,
        modules: 0,
        error: error.message 
      });
    }
  });

  app.get("/api/nexus-v3/activity", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/activity`, {
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        activities: [],
        workers: null,
        system: null,
        error: error.message 
      });
    }
  });

  app.post("/api/nexus-v3/activity/log", async (req, res) => {
    try {
      const response = await fetch(`${NEXUS_V3_BASE}/api/activity/log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req.body),
        signal: AbortSignal.timeout(3000)
      });
      const data = await response.json();
      res.json(data);
    } catch (error: any) {
      res.status(503).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  app.get("/api/nexus/status", async (req, res) => {
    try {
      const [v2Response, v3Response] = await Promise.allSettled([
        fetch("http://0.0.0.0:8000/api/nexus/status", { signal: AbortSignal.timeout(3000) }),
        fetch(`${NEXUS_V3_BASE}/api/status`, { signal: AbortSignal.timeout(3000) })
      ]);

      let v2Data: any = null;
      let v3Data: any = null;

      if (v2Response.status === "fulfilled" && v2Response.value.ok) {
        v2Data = await v2Response.value.json();
      }

      if (v3Response.status === "fulfilled" && v3Response.value.ok) {
        v3Data = await v3Response.value.json();
      }

      res.json({
        v2: v2Data ? { connected: true, port: 8000, ...v2Data } : { connected: false, port: 8000 },
        v3: v3Data ? { connected: true, port: 5002, ...v3Data } : { connected: false, port: 5002 },
        unified: {
          anyConnected: !!(v2Data || v3Data),
          allConnected: !!(v2Data && v3Data),
          timestamp: new Date().toISOString()
        }
      });
    } catch (error: any) {
      res.status(500).json({ 
        error: "Failed to fetch nexus status",
        message: error.message 
      });
    }
  });

  console.log("✅ Aurora Nexus V3 routes registered (port 5002 bridge)");
}
