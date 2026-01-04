// @ts-nocheck
import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, real, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const knowledgeDocuments = pgTable("knowledge_documents", {
  id: varchar("id", { length: 255 }).primaryKey(),
  text: text("text").notNull(),
  embedding: real("embedding").array().notNull(),
  source: varchar("source", { length: 255 }),
  category: varchar("category", { length: 100 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertKnowledgeDocumentSchema = createInsertSchema(knowledgeDocuments).omit({
  createdAt: true,
});

export type InsertKnowledgeDocument = z.infer<typeof insertKnowledgeDocumentSchema>;
export type KnowledgeDocument = typeof knowledgeDocuments.$inferSelect;

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
  offset: z.coerce.number().int().min(0).default(0),
  perfectOnly: z.coerce.boolean().default(false),
  minScore: z.coerce.number().optional(),
  maxScore: z.coerce.number().optional(),
  startDate: z.string().datetime().optional(),
  endDate: z.string().datetime().optional(),
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

export const similarityQuerySchema = z.object({
  targetSigKey: z.string(),
  targetPostBow: z.array(z.string()),
  limit: z.coerce.number().int().min(1).max(20).default(5),
});

export type SimilarityQuery = z.infer<typeof similarityQuerySchema>;

export type SimilarityResult = {
  entry: CorpusEntry;
  similarity: number;
  breakdown: {
    returnMatch: number;
    argMatch: number;
    jaccardScore: number;
    perfectBonus: number;
  };
};

export const runMetaSchema = z.object({
  run_id: z.string(),
  timestamp: z.string().datetime(),
  seed_bias: z.number().min(0).max(0.5),
  seeding_enabled: z.boolean(),
  max_iters: z.number().int().positive(),
  beam: z.number().int().positive().optional(),
  notes: z.string().optional(),
});

export type RunMeta = z.infer<typeof runMetaSchema>;

export const usedSeedSchema = z.object({
  run_id: z.string(),
  function: z.string(),
  source_id: z.string().optional(),
  reason: z.record(z.any()).optional(),
  score: z.number().optional(),
  passed: z.number().int().optional(),
  total: z.number().int().optional(),
  snippet: z.string().optional(),
  timestamp: z.string().datetime(),
});

export type UsedSeed = z.infer<typeof usedSeedSchema>;
/* @ts-nocheck */
