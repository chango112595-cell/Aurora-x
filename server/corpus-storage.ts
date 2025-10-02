import Database from "better-sqlite3";
import { mkdirSync } from "fs";
import { dirname } from "path";
import type { CorpusEntry } from "@shared/schema";

export class CorpusStorage {
  private db: Database.Database;

  constructor(dbPath: string) {
    mkdirSync(dirname(dbPath), { recursive: true });
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

  getEntries(params: { func?: string; limit: number }): any[] {
    if (params.func) {
      return this.db
        .prepare(
          `SELECT * FROM corpus WHERE func_name = ? ORDER BY timestamp DESC LIMIT ?`
        )
        .all(params.func, params.limit);
    }
    return this.db
      .prepare(`SELECT * FROM corpus ORDER BY timestamp DESC LIMIT ?`)
      .all(params.limit);
  }

  getTopByFunc(func: string, limit: number): any[] {
    return this.db
      .prepare(
        `SELECT * FROM corpus
         WHERE func_name = ?
         ORDER BY (passed = total) DESC, score ASC, timestamp DESC
         LIMIT ?`
      )
      .all(func, limit);
  }

  getRecent(limit: number): any[] {
    return this.db
      .prepare(`SELECT * FROM corpus ORDER BY timestamp DESC LIMIT ?`)
      .all(limit);
  }

  close(): void {
    this.db.close();
  }
}

const DB_PATH = process.env.AURORA_DB_PATH || "./data/corpus.db";
export const corpusStorage = new CorpusStorage(DB_PATH);
