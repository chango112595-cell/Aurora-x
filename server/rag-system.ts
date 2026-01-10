// @ts-nocheck
/**
 * Self-Contained RAG (Retrieval Augmented Generation) System
 * Aurora's autonomous knowledge system - production-ready with PostgreSQL persistence
 * Uses local embeddings with database-backed vector storage
 */

import { isDatabaseAvailable, requireDb } from "./db";
import { knowledgeDocuments } from "../shared/schema";
import { eq } from "drizzle-orm";

console.log('[RAG] Production knowledge system initialized');
console.log('[RAG] Using local embeddings with PostgreSQL persistence');

/**
 * Generate embeddings using enhanced local algorithm with optional Memory Fabric integration
 * Falls back to improved TF-IDF inspired hashing if Memory Fabric unavailable
 * No external APIs required - fully self-contained
 */
async function generateLocalEmbedding(text: string): Promise<number[]> {
  // Try to use Memory Fabric embedder if available
  try {
    const memoryFabricUrl = process.env.AURORA_MEMORY_FABRIC_URL || 'http://127.0.0.1:8002';
    const response = await fetch(`${memoryFabricUrl}/api/embed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (response.ok) {
      const data = await response.json();
      if (data.embedding && Array.isArray(data.embedding)) {
        return data.embedding;
      }
    }
  } catch (error) {
    // Fall back to local embedding
    console.log('[RAG] Memory Fabric unavailable, using local embedding');
  }

  // Enhanced local embedding with improved TF-IDF inspired hashing
  const normalized = text.toLowerCase().trim();
  const tokens = normalized.split(/\s+/).filter(t => t.length > 2);
  const embedding = new Array(384).fill(0);

  // Improved token weighting with position and frequency awareness
  const tokenFreq: Record<string, number> = {};
  for (const token of tokens) {
    tokenFreq[token] = (tokenFreq[token] || 0) + 1;
  }

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    const hash = hashToken(token);
    const position = Math.abs(hash) % embedding.length;
    const tf = tokenFreq[token] / tokens.length; // Term frequency
    const idf = Math.log((tokens.length + 1) / (tokenFreq[token] + 1)); // Inverse document frequency
    const weight = (tf * idf) / Math.sqrt(i + 1);

    embedding[position] += weight;
    embedding[(position + 1) % embedding.length] += weight * 0.5;
    embedding[(position + 2) % embedding.length] += weight * 0.25;

    // Character-level features for better semantic understanding
    for (let j = 0; j < token.length; j++) {
      const charHash = (hash * (j + 1) + token.charCodeAt(j)) % embedding.length;
      embedding[Math.abs(charHash)] += weight * 0.1;
    }
  }

  const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0)) || 1;
  return embedding.map(val => val / magnitude);
}

function hashToken(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) ^ str.charCodeAt(i);
  }
  return hash;
}

function cosineSimilarity(a: number[], b: number[]): number {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  const denominator = Math.sqrt(normA) * Math.sqrt(normB);
  return denominator === 0 ? 0 : dotProduct / denominator;
}

export interface DocumentMetadata {
  text: string;
  source?: string;
  category?: string;
  timestamp?: number;
  [key: string]: any;
}

export async function storeDocument(
  id: string,
  text: string,
  metadata: DocumentMetadata = { text }
): Promise<boolean> {
  try {
    const db = requireDb();
    const embedding = await generateLocalEmbedding(text);

    await db.insert(knowledgeDocuments)
      .values({
        id,
        text,
        embedding,
        source: metadata.source || null,
        category: metadata.category || null,
      })
      .onConflictDoUpdate({
        target: knowledgeDocuments.id,
        set: {
          text,
          embedding,
          source: metadata.source || null,
          category: metadata.category || null,
        }
      });

    console.log('[RAG] Document stored:', id);
    return true;
  } catch (error: any) {
    console.error('[RAG] Store error:', error.message);
    return false;
  }
}

export interface SearchResult {
  id: string;
  score: number;
  metadata: DocumentMetadata;
}

export async function semanticSearch(
  query: string,
  topK: number = 5,
  filter?: Record<string, any>
): Promise<SearchResult[]> {
  try {
    const db = requireDb();
    const queryEmbedding = await generateLocalEmbedding(query);

    const docs = await db.select().from(knowledgeDocuments);

    const results: Array<{ doc: typeof docs[0]; score: number }> = [];

    for (const doc of docs) {
      if (filter) {
        if (filter.category && doc.category !== filter.category) continue;
        if (filter.source && doc.source !== filter.source) continue;
      }

      const docEmbedding = doc.embedding as number[];
      const score = cosineSimilarity(queryEmbedding, docEmbedding);
      results.push({ doc, score });
    }

    results.sort((a, b) => b.score - a.score);

    return results.slice(0, topK).map(r => ({
      id: r.doc.id,
      score: r.score,
      metadata: {
        text: r.doc.text,
        source: r.doc.source || undefined,
        category: r.doc.category || undefined,
        timestamp: r.doc.createdAt.getTime(),
      }
    }));
  } catch (error: any) {
    console.error('[RAG] Search error:', error.message);
    return [];
  }
}

export async function getRAGContext(
  query: string,
  topK: number = 3
): Promise<string> {
  const results = await semanticSearch(query, topK);

  if (results.length === 0) {
    return '';
  }

  const context = results
    .filter(r => r.score > 0.1)
    .map((result, i) => `[Context ${i + 1}] ${result.metadata.text}`)
    .join('\n\n');

  return context ? `\nRelevant Context:\n${context}\n` : '';
}

export async function addToKnowledgeBase(
  documents: Array<{ id: string; text: string; metadata?: DocumentMetadata }>
): Promise<number> {
  let successCount = 0;

  for (const doc of documents) {
    const success = await storeDocument(
      doc.id,
      doc.text,
      doc.metadata || { text: doc.text }
    );

    if (success) successCount++;
  }

  console.log(`[RAG] Added ${successCount}/${documents.length} documents to knowledge base`);
  return successCount;
}

export async function deleteFromKnowledgeBase(ids: string[]): Promise<boolean> {
  try {
    const db = requireDb();
    for (const id of ids) {
      await db.delete(knowledgeDocuments).where(eq(knowledgeDocuments.id, id));
    }
    console.log(`[RAG] Deleted ${ids.length} documents`);
    return true;
  } catch (error: any) {
    console.error('[RAG] Delete error:', error.message);
    return false;
  }
}

export function isRAGAvailable(): boolean {
  return isDatabaseAvailable();
}

export function isEmbeddingsAvailable(): boolean {
  return true;
}

export async function getKnowledgeBaseStats(): Promise<{ documentCount: number; categories: string[] }> {
  try {
    const db = requireDb();
    const docs = await db.select().from(knowledgeDocuments);
    const categories = new Set<string>();
    for (const doc of docs) {
      if (doc.category) {
        categories.add(doc.category);
      }
    }
    return {
      documentCount: docs.length,
      categories: Array.from(categories)
    };
  } catch (error) {
    return { documentCount: 0, categories: [] };
  }
}
/* @ts-nocheck */
