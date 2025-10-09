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
