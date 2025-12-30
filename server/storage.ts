// @ts-nocheck
import { type User, type InsertUser, users } from "../shared/schema";
import { requireDb, isDatabaseAvailable } from "./db";
import { eq } from "drizzle-orm";
import Database from "better-sqlite3";
import type { Database as SQLiteDatabase, Statement } from "better-sqlite3";
import * as fs from "fs";
import * as path from "path";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
}

type StorageProvider = "postgres" | "sqlite" | "memory";

type StorageStatus = {
  provider: StorageProvider;
  ready: boolean;
  details?: string;
  sqlitePath?: string;
};

export class DatabaseStorage implements IStorage {
  async getUser(id: string): Promise<User | undefined> {
    const db = requireDb();
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const db = requireDb();
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const db = requireDb();
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }
}

class SQLiteStorage implements IStorage {
  private db: SQLiteDatabase;
  private getUserStmt: Statement;
  private getUserByUsernameStmt: Statement;
  private insertUserStmt: Statement;

  constructor(dbPath: string) {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
    this.db = new Database(dbPath);
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
      );
    `);
    this.getUserStmt = this.db.prepare(
      "SELECT id, username, password FROM users WHERE id = ? LIMIT 1"
    );
    this.getUserByUsernameStmt = this.db.prepare(
      "SELECT id, username, password FROM users WHERE username = ? LIMIT 1"
    );
    this.insertUserStmt = this.db.prepare(
      "INSERT INTO users (id, username, password) VALUES (?, ?, ?)"
    );
  }

  async getUser(id: string): Promise<User | undefined> {
    const row = this.getUserStmt.get(id) as User | undefined;
    return row;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const row = this.getUserByUsernameStmt.get(username) as User | undefined;
    return row;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    this.insertUserStmt.run(id, insertUser.username, insertUser.password);
    return { id, ...insertUser };
  }
}

class MemoryStorage implements IStorage {
  private users = new Map<string, User>();

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    for (const user of this.users.values()) {
      if (user.username === username) {
        return user;
      }
    }
    return undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const user: User = { id: randomUUID(), ...insertUser };
    this.users.set(user.id, user);
    return user;
  }
}

const SQLITE_PATH = path.join(process.cwd(), "data", "aurora-users.db");

let storageProvider: StorageProvider = "memory";
let storageDetails: string | undefined;

let storage: IStorage;
if (isDatabaseAvailable()) {
  storage = new DatabaseStorage();
  storageProvider = "postgres";
} else {
  try {
    storage = new SQLiteStorage(SQLITE_PATH);
    storageProvider = "sqlite";
  } catch (error) {
    storage = new MemoryStorage();
    storageProvider = "memory";
    storageDetails = error instanceof Error ? error.message : "SQLite initialization failed";
  }
}

export function getStorageStatus(): StorageStatus {
  return {
    provider: storageProvider,
    ready: storageProvider !== "memory",
    details: storageDetails,
    sqlitePath: storageProvider === "sqlite" ? SQLITE_PATH : undefined,
  };
}

export { storage };
/* @ts-nocheck */
