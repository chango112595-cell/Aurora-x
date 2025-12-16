import { drizzle } from "drizzle-orm/neon-serverless";
import { Pool, neonConfig } from "@neondatabase/serverless";
import ws from "ws";
import * as schema from "../shared/schema";

neonConfig.webSocketConstructor = ws;

function createDatabase() {
  if (!process.env.DATABASE_URL) {
    return null;
  }

  try {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    return drizzle(pool, { schema });
  } catch (error) {
    return null;
  }
}

export const db = createDatabase();
