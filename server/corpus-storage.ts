import Database from 'better-sqlite3';
import { randomUUID } from 'crypto';
import * as fs from "fs";
import * as path from "path";
import type {
  CorpusEntry,
  RunMeta,
  UsedSeed,
  CorpusQuery,
} from "../shared/schema";

interface ParsedCorpusEntry {
  id: string;
  timestamp: string;
  spec_id: string;
  spec_hash: string;
  func_name: string;
  func_signature: string;
  passed: number;
  total: number;
  score: number;
  snippet: string;
  complexity: number | null;
  iteration: number | null;
  sig_key: string | null;
  duration_ms: number | null;
  synthesis_method: string | null;
  failing_tests: string[];
  calls_functions: string[];
  post_bow: string[];
}

interface CorpusRow {
  id: string;
  timestamp: string;
  spec_id: string;
  spec_hash: string;
  func_name: string;
  func_signature: string;
  passed: number;
  total: number;
  score: number;
  failing_tests: string;
  snippet: string;
  complexity: number | null;
  iteration: number | null;
  calls_functions: string;
  sig_key: string | null;
  post_bow: string;
  duration_ms: number | null;
  synthesis_method: string | null;
}

interface RunMetaRow {
  run_id: string;
  timestamp: string;
  seed_bias: number;
  seeding_enabled: number;
  max_iters: number;
  beam: number | null;
  notes: string | null;
}

interface UsedSeedRow {
  id: string;
  run_id: string;
  function: string;
  source_id: string | null;
  reason_json: string | null;
  score: number | null;
  passed: number | null;
  total: number | null;
  snippet: string | null;
  timestamp: string;
}

interface SimilarityResult {
  entry: ParsedCorpusEntry;
  similarity: number;
  breakdown: {
    returnMatch: number;
    argMatch: number;
    jaccardScore: number;
    perfectBonus: number;
  };
}

interface GetEntriesParams {
  func?: string;
  limit: number;
  offset?: number;
  perfectOnly?: boolean;
  minScore?: number;
  maxScore?: number;
  startDate?: string;
  endDate?: string;
}

interface InsertRunMetaInput {
  run_id: string;
  timestamp: string;
  seed_bias: number;
  seeding_enabled: boolean;
  max_iters: number;
  beam?: number | null;
  notes?: string | null;
}

interface InsertUsedSeedInput {
  run_id: string;
  function: string;
  source_id?: string | null;
  reason?: Record<string, unknown>;
  score?: number | null;
  passed?: number | null;
  total?: number | null;
  snippet?: string | null;
  timestamp: string;
}

interface ParsedUsedSeed extends Omit<UsedSeedRow, 'reason_json'> {
  reason: Record<string, unknown> | null;
}

export class CorpusStorage {
  private db: Database.Database;

  constructor(dbPath: string) {
    const dataDir = path.dirname(dbPath);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    this.db = new Database(dbPath);
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("foreign_keys = ON");
    this.initSchema();
  }

  private initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS corpus(
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        spec_id TEXT NOT NULL,
        spec_hash TEXT NOT NULL,
        func_name TEXT NOT NULL,
        func_signature TEXT NOT NULL,
        passed INTEGER NOT NULL,
        total INTEGER NOT NULL,
        score REAL NOT NULL,
        failing_tests TEXT NOT NULL,
        snippet TEXT NOT NULL,
        complexity INTEGER,
        iteration INTEGER,
        calls_functions TEXT,
        sig_key TEXT,
        post_bow TEXT,
        duration_ms INTEGER,
        synthesis_method TEXT
      );
      CREATE INDEX IF NOT EXISTS idx_spec_fn ON corpus(spec_id, func_name);
      CREATE INDEX IF NOT EXISTS idx_sigkey ON corpus(sig_key);
      CREATE INDEX IF NOT EXISTS idx_time ON corpus(timestamp);
      CREATE INDEX IF NOT EXISTS idx_best_fn ON corpus(func_name, score, passed, total);

      CREATE TABLE IF NOT EXISTS run_meta(
        run_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        seed_bias REAL NOT NULL,
        seeding_enabled INTEGER NOT NULL,
        max_iters INTEGER NOT NULL,
        beam INTEGER,
        notes TEXT
      );
      CREATE INDEX IF NOT EXISTS idx_run_meta_ts ON run_meta(timestamp DESC);

      CREATE TABLE IF NOT EXISTS used_seeds(
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        function TEXT NOT NULL,
        source_id TEXT,
        reason_json TEXT,
        score REAL,
        passed INTEGER,
        total INTEGER,
        snippet TEXT,
        timestamp TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_used_seeds_run ON used_seeds(run_id, timestamp DESC);
    `);
  }

  insertEntry(entry: CorpusEntry): void {
    const failing = JSON.stringify(entry.failing_tests ?? []);
    const calls = JSON.stringify(entry.calls_functions ?? []);
    const bow = JSON.stringify(entry.post_bow ?? []);

    const stmt = this.db.prepare(`
      INSERT OR IGNORE INTO corpus(
        id, timestamp, spec_id, spec_hash, func_name, func_signature, passed, total, score,
        failing_tests, snippet, complexity, iteration, calls_functions, sig_key, post_bow,
        duration_ms, synthesis_method
      ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    `);

    stmt.run(
      entry.id,
      entry.timestamp,
      entry.spec_id,
      entry.spec_hash,
      entry.func_name,
      entry.func_signature,
      entry.passed,
      entry.total,
      entry.score,
      failing,
      entry.snippet,
      entry.complexity ?? null,
      entry.iteration ?? null,
      calls,
      entry.sig_key ?? null,
      bow,
      entry.duration_ms ?? null,
      entry.synthesis_method ?? null
    );
  }

  private parseEntry(row: CorpusRow): ParsedCorpusEntry {
    return {
      ...row,
      failing_tests: row.failing_tests ? JSON.parse(row.failing_tests) : [],
      calls_functions: row.calls_functions ? JSON.parse(row.calls_functions) : [],
      post_bow: row.post_bow ? JSON.parse(row.post_bow) : [],
    };
  }

  getEntries(params: GetEntriesParams): ParsedCorpusEntry[] {
    const conditions: string[] = [];
    const values: (string | number)[] = [];

    if (params.func) {
      conditions.push("func_name = ?");
      values.push(params.func);
    }

    if (params.perfectOnly) {
      conditions.push("passed = total");
    }

    if (params.minScore !== undefined) {
      conditions.push("score >= ?");
      values.push(params.minScore);
    }

    if (params.maxScore !== undefined) {
      conditions.push("score <= ?");
      values.push(params.maxScore);
    }

    if (params.startDate) {
      conditions.push("timestamp >= ?");
      values.push(params.startDate);
    }

    if (params.endDate) {
      conditions.push("timestamp <= ?");
      values.push(params.endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
    const offset = params.offset ?? 0;

    const sql = `SELECT * FROM corpus ${whereClause} ORDER BY timestamp DESC LIMIT ? OFFSET ?`;
    values.push(params.limit, offset);

    const rows = this.db.prepare(sql).all(...values) as CorpusRow[];
    return rows.map((row: CorpusRow) => this.parseEntry(row));
  }

  getTopByFunc(func: string, limit: number): ParsedCorpusEntry[] {
    const rows = this.db
      .prepare(
        `SELECT * FROM corpus
         WHERE func_name = ?
         ORDER BY (passed = total) DESC, score ASC, timestamp DESC
         LIMIT ?`
      )
      .all(func, limit) as CorpusRow[];
    return rows.map((row: CorpusRow) => this.parseEntry(row));
  }

  getRecent(limit: number = 10): ParsedCorpusEntry[] {
    const query = `
      SELECT * FROM corpus
      WHERE id IS NOT NULL
      ORDER BY timestamp DESC
      LIMIT ?
    `;

    const rows = this.db.prepare(query).all(limit) as CorpusRow[];
    return rows.map(row => this.parseEntry(row));
  }

  private bowTokens(s: string): string[] {
    const words = s.match(/[A-Za-z_][A-Za-z0-9_]*/g) || [];
    const stopwords = new Set(["and", "or", "not", "ret", "true", "false", "none"]);
    return words
      .map((w) => w.toLowerCase())
      .filter((w) => !stopwords.has(w));
  }

  private jaccard(a: string[], b: string[]): number {
    if (a.length === 0 && b.length === 0) return 0;
    const setA = new Set(a);
    const setB = new Set(b);
    const intersection = new Set(Array.from(setA).filter((x) => setB.has(x)));
    const union = new Set(Array.from(setA).concat(Array.from(setB)));
    return union.size > 0 ? intersection.size / union.size : 0;
  }

  getSimilar(
    targetSigKey: string,
    targetPostBow: string[],
    limit: number
  ): SimilarityResult[] {
    const rows = this.db
      .prepare(`SELECT * FROM corpus ORDER BY timestamp DESC LIMIT 2000`)
      .all() as CorpusRow[];

    const results: SimilarityResult[] = [];

    let targetName = "";
    let targetArgs = "";
    let targetRet = "";
    try {
      const parts = targetSigKey.split("|");
      targetName = parts[0] || "";
      targetArgs = parts[1] || "";
      targetRet = parts[2] || "";
    } catch {
    }

    for (const row of rows) {
      const entry = this.parseEntry(row);
      if (!entry.snippet) continue;

      let name = "";
      let args = "";
      let ret = "";
      try {
        const parts = (entry.sig_key || "||").split("|");
        name = parts[0] || "";
        args = parts[1] || "";
        ret = parts[2] || "";
      } catch {
      }

      const returnMatch = ret === targetRet && ret !== "" ? 1.0 : 0.0;
      const argMatch = args === targetArgs && args !== "" ? 1.0 : 0.0;

      const bow = entry.post_bow || [];
      const jaccardScore = this.jaccard(bow, targetPostBow);

      const signatureScore = 0.3 * returnMatch + 0.3 * argMatch;
      let similarity = 0.6 * signatureScore + 0.4 * jaccardScore;
      const perfectBonus = entry.passed === entry.total ? 0.1 : 0;
      similarity += perfectBonus;

      results.push({
        entry,
        similarity,
        breakdown: {
          returnMatch,
          argMatch,
          jaccardScore,
          perfectBonus,
        },
      });
    }

    results.sort((a, b) => b.similarity - a.similarity);

    const seen = new Set<string>();
    const unique: SimilarityResult[] = [];
    for (const result of results) {
      if (!seen.has(result.entry.snippet)) {
        seen.add(result.entry.snippet);
        unique.push(result);
      }
      if (unique.length >= limit) break;
    }

    return unique;
  }

  insertRunMeta(meta: InsertRunMetaInput): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO run_meta(
        run_id, timestamp, seed_bias, seeding_enabled, max_iters, beam, notes
      ) VALUES (?,?,?,?,?,?,?)
    `);

    stmt.run(
      meta.run_id,
      meta.timestamp,
      meta.seed_bias,
      meta.seeding_enabled ? 1 : 0,
      meta.max_iters,
      meta.beam ?? null,
      meta.notes ?? null
    );
  }

  getLatestRunMeta(): (Omit<RunMetaRow, 'seeding_enabled'> & { seeding_enabled: boolean }) | null {
    const row = this.db
      .prepare(`SELECT * FROM run_meta ORDER BY timestamp DESC LIMIT 1`)
      .get() as RunMetaRow | undefined;
    if (!row) return null;
    return {
      ...row,
      seeding_enabled: Boolean(row.seeding_enabled),
    };
  }

  insertUsedSeed(seed: InsertUsedSeedInput): string {
    const id = randomUUID();
    const stmt = this.db.prepare(`
      INSERT INTO used_seeds(
        id, run_id, function, source_id, reason_json, score, passed, total, snippet, timestamp
      ) VALUES (?,?,?,?,?,?,?,?,?,?)
    `);

    stmt.run(
      id,
      seed.run_id,
      seed.function,
      seed.source_id ?? null,
      seed.reason ? JSON.stringify(seed.reason) : null,
      seed.score ?? null,
      seed.passed ?? null,
      seed.total ?? null,
      seed.snippet ?? null,
      seed.timestamp
    );

    return id;
  }

  getUsedSeeds(params: { run_id?: string; limit?: number }): ParsedUsedSeed[] {
    const limit = params.limit ?? 200;

    if (params.run_id) {
      const rows = this.db
        .prepare(`SELECT * FROM used_seeds WHERE run_id = ? ORDER BY timestamp DESC LIMIT ?`)
        .all(params.run_id, limit) as UsedSeedRow[];
      return rows.map((row: UsedSeedRow) => ({
        ...row,
        reason: row.reason_json ? JSON.parse(row.reason_json) : null,
      }));
    } else {
      const rows = this.db
        .prepare(`SELECT * FROM used_seeds ORDER BY timestamp DESC LIMIT ?`)
        .all(limit) as UsedSeedRow[];
      return rows.map((row: UsedSeedRow) => ({
        ...row,
        reason: row.reason_json ? JSON.parse(row.reason_json) : null,
      }));
    }
  }

  close(): void {
    this.db.close();
  }
}

const DB_PATH = process.env.AURORA_DB_PATH || "./data/corpus.db";
export const corpusStorage = new CorpusStorage(DB_PATH);
