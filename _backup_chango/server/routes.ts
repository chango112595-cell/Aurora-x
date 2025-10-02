import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { corpusStorage } from "./corpus-storage";
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
  // TELEMETRY DISABLED - Uncomment to re-enable Aurora-X data ingestion
  // app.post("/api/corpus", (req, res) => {
  //   const auth = req.header("x-api-key") ?? "";
  //   if (auth !== AURORA_API_KEY) {
  //     return res.status(401).json({ error: "unauthorized" });
  //   }

  //   try {
  //     const entry = corpusEntrySchema.parse(req.body);
  //     corpusStorage.insertEntry(entry);
  //     return res.json({ ok: true, id: entry.id });
  //   } catch (e: any) {
  //     return res.status(400).json({
  //       error: "bad_request",
  //       details: e?.message ?? String(e),
  //     });
  //   }
  // });

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

  // TELEMETRY DISABLED - Uncomment to re-enable Aurora-X telemetry
  // app.post("/api/run-meta", (req, res) => {
  //   const auth = req.header("x-api-key") ?? "";
  //   if (auth !== AURORA_API_KEY) {
  //     return res.status(401).json({ error: "unauthorized" });
  //   }

  //   try {
  //     const meta = runMetaSchema.parse(req.body);
  //     corpusStorage.insertRunMeta(meta);
  //     return res.json({ ok: true, run_id: meta.run_id });
  //   } catch (e: any) {
  //     return res.status(400).json({
  //       error: "bad_request",
  //       details: e?.message ?? String(e),
  //     });
  //   }
  // });

  // app.get("/api/run-meta/latest", (req, res) => {
  //   try {
  //     const meta = corpusStorage.getLatestRunMeta();
  //     return res.json({ meta });
  //   } catch (e: any) {
  //     return res.status(500).json({
  //       error: "internal_error",
  //       details: e?.message ?? String(e),
  //     });
  //   }
  // });

  // app.post("/api/used-seeds", (req, res) => {
  //   const auth = req.header("x-api-key") ?? "";
  //   if (auth !== AURORA_API_KEY) {
  //     return res.status(401).json({ error: "unauthorized" });
  //   }

  //   try {
  //     const seed = usedSeedSchema.parse(req.body);
  //     const id = corpusStorage.insertUsedSeed(seed);
  //     return res.json({ ok: true, id });
  //   } catch (e: any) {
  //     return res.status(400).json({
  //       error: "bad_request",
  //       details: e?.message ?? String(e),
  //     });
  //   }
  // });

  // app.get("/api/used-seeds", (req, res) => {
  //   try {
  //     const run_id = req.query.run_id as string | undefined;
  //     const limit = req.query.limit ? parseInt(req.query.limit as string) : 200;
  //     const seeds = corpusStorage.getUsedSeeds({ run_id, limit });
  //     return res.json({ seeds });
  //   } catch (e: any) {
  //     return res.status(500).json({
  //       error: "internal_error",
  //       details: e?.message ?? String(e),
  //     });
  //   }
  // });

  const httpServer = createServer(app);

  return httpServer;
}
