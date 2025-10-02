import { sql } from "drizzle-orm";
import { pgTable, text, varchar } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export const corpusEntrySchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
  spec_id: z.string().min(1),
  spec_hash: z.string().length(64),
  func_name: z.string().min(1),
  func_signature: z.string().min(1),
  passed: z.number().int().nonnegative(),
  total: z.number().int().positive(),
  score: z.number(),
  failing_tests: z.array(z.string()).default([]),
  snippet: z.string().min(1),
  complexity: z.number().int().optional(),
  iteration: z.number().int().optional(),
  calls_functions: z.array(z.string()).optional(),
  sig_key: z.string().optional(),
  post_bow: z.array(z.string()).optional(),
  duration_ms: z.number().int().optional(),
  synthesis_method: z.string().optional(),
});

export type CorpusEntry = z.infer<typeof corpusEntrySchema>;

export const corpusQuerySchema = z.object({
  func: z.string().optional(),
  limit: z.coerce.number().int().min(1).max(200).default(50),
});

export type CorpusQuery = z.infer<typeof corpusQuerySchema>;

export const topQuerySchema = z.object({
  func: z.string(),
  limit: z.coerce.number().int().min(1).max(50).default(10),
});

export type TopQuery = z.infer<typeof topQuerySchema>;

export const recentQuerySchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(50),
});

export type RecentQuery = z.infer<typeof recentQuerySchema>;
