import { drizzle } from "drizzle-orm/neon-serverless";
import { Pool, neonConfig } from "@neondatabase/serverless";
import ws from "ws";
import * as schema from "../shared/schema";

neonConfig.webSocketConstructor = ws;

type DatabaseHandle = {
  db: ReturnType<typeof drizzle>;
  pool: Pool;
};

let databaseError: string | null = null;

function createDatabase(): DatabaseHandle | null {
  if (!process.env.DATABASE_URL) {
    databaseError = "DATABASE_URL is not set";
    return null;
  }

  try {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    const db = drizzle(pool, { schema });
    return { db, pool };
  } catch (error) {
    databaseError = error instanceof Error ? error.message : "Database initialization failed";
    return null;
  }
}

const database = createDatabase();

export const db = database?.db ?? null;
export const dbPool = database?.pool ?? null;
export const dbError = databaseError;

export function isDatabaseAvailable(): boolean {
  return !!db;
}

export function requireDb() {
  if (!db) {
    throw new Error(databaseError ?? "Database connection not configured");
  }
  return db;
}

export async function assertDatabaseReady(): Promise<void> {
  if (!dbPool) {
    throw new Error(databaseError ?? "Database connection not configured");
  }
  await dbPool.query("SELECT 1");
}
