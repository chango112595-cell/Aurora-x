/**
 * RAG (Retrieval Augmented Generation) System
 * Uses Pinecone for vector storage and OpenAI for embeddings
 */

import { Pinecone } from '@pinecone-database/pinecone';

let pinecone: Pinecone | null = null;
let index: any = null;

const OPENAI_API_KEY = process.env.AI_INTEGRATIONS_OPENAI_API_KEY || process.env.OPENAI_API_KEY;
const OPENAI_BASE_URL = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL || 'https://api.openai.com/v1';

// Initialize Pinecone if API key is provided
if (process.env.PINECONE_API_KEY) {
  try {
    pinecone = new Pinecone({
      apiKey: process.env.PINECONE_API_KEY,
    });
    
    const indexName = process.env.PINECONE_INDEX || 'aurora-knowledge';
    index = pinecone.index(indexName);
    
    console.log('[RAG] Pinecone vector database connected:', indexName);
  } catch (error: any) {
    console.error('[RAG] Pinecone initialization failed:', error.message);
  }
} else {
  console.log('[RAG] Pinecone not configured (set PINECONE_API_KEY for vector search)');
}

// Log OpenAI embeddings status
if (OPENAI_API_KEY) {
  console.log('[RAG] OpenAI embeddings configured');
} else {
  console.log('[RAG] OpenAI not configured - using fallback embeddings (set OPENAI_API_KEY for production)');
}

/**
 * Generate embeddings for text using OpenAI's text-embedding-3-small model
 * Falls back to a simple hash-based embedding if OpenAI is not configured
 */
async function generateEmbedding(text: string): Promise<number[]> {
  if (OPENAI_API_KEY) {
    try {
      const response = await fetch(`${OPENAI_BASE_URL}/embeddings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'text-embedding-3-small',
          input: text.substring(0, 8000),
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[RAG] OpenAI embedding error:', errorText);
        throw new Error(`OpenAI API error: ${response.status}`);
      }

      const data = await response.json() as { data: Array<{ embedding: number[] }> };
      return data.data[0].embedding;
    } catch (error: any) {
      console.error('[RAG] OpenAI embedding failed, using fallback:', error.message);
      return generateFallbackEmbedding(text);
    }
  }
  
  return generateFallbackEmbedding(text);
}

function generateFallbackEmbedding(text: string): number[] {
  const hash = simpleHash(text);
  return new Array(1536).fill(0).map((_, i) => 
    Math.sin(hash * (i + 1)) * 0.1
  );
}

function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash = hash & hash;
  }
  return hash;
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
  if (!index) {
    console.warn('[RAG] Cannot store document - Pinecone not configured');
    return false;
  }

  try {
    const embedding = await generateEmbedding(text);
    
    await index.upsert([{
      id,
      values: embedding,
      metadata: {
        ...metadata,
        text,
        timestamp: metadata.timestamp || Date.now()
      }
    }]);

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
  if (!index) {
    console.warn('[RAG] Cannot search - Pinecone not configured');
    return [];
  }

  try {
    const embedding = await generateEmbedding(query);
    
    const results = await index.query({
      vector: embedding,
      topK,
      includeMetadata: true,
      filter
    });

    return results.matches.map((match: any) => ({
      id: match.id,
      score: match.score,
      metadata: match.metadata
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
    .map((result, i) => `[Context ${i + 1}] ${result.metadata.text}`)
    .join('\n\n');

  return `\nRelevant Context:\n${context}\n`;
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
  if (!index) {
    console.warn('[RAG] Cannot delete - Pinecone not configured');
    return false;
  }

  try {
    await index.deleteMany(ids);
    console.log(`[RAG] Deleted ${ids.length} documents`);
    return true;
  } catch (error: any) {
    console.error('[RAG] Delete error:', error.message);
    return false;
  }
}

export function isRAGAvailable(): boolean {
  return index !== null;
}

export function isEmbeddingsAvailable(): boolean {
  return !!OPENAI_API_KEY;
}
