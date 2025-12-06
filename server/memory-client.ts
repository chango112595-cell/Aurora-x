/**
 * Aurora Memory Client - TypeScript interface to Python memory system
 */

import fetch from 'node-fetch';

export interface MemoryRecord {
  id: string;
  text: string;
  meta: Record<string, any>;
  score?: number;
}

export interface MemoryWriteResult {
  success: boolean;
  id?: string;
  longterm?: boolean;
  error?: string;
}

export interface MemoryQueryResult {
  success: boolean;
  results?: MemoryRecord[];
  error?: string;
}

export interface MemoryStatus {
  success: boolean;
  status?: string;
  short_term_count?: number;
  long_term_count?: number;
  error?: string;
}

export class MemoryClient {
  private baseUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 5003) {
    this.baseUrl = `http://127.0.0.1:${port}`;
  }

  /**
   * Check if memory service is available
   */
  async checkStatus(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json() as MemoryStatus;
        this.enabled = data.success === true;
        return this.enabled;
      }
      return false;
    } catch (error) {
      this.enabled = false;
      return false;
    }
  }

  /**
   * Write to memory (short-term by default)
   */
  async write(text: string, meta?: Record<string, any>, longterm: boolean = false): Promise<MemoryWriteResult> {
    if (!this.enabled) {
      return { success: false, error: 'Memory service not available' };
    }

    try {
      const response = await fetch(`${this.baseUrl}/memory/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, meta: meta || {}, longterm })
      });

      return await response.json() as MemoryWriteResult;
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  /**
   * Query memory (searches both short-term and long-term)
   */
  async query(queryText: string, topK: number = 5): Promise<MemoryQueryResult> {
    if (!this.enabled) {
      return { success: false, error: 'Memory service not available' };
    }

    try {
      const response = await fetch(`${this.baseUrl}/memory/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, top_k: topK })
      });

      return await response.json() as MemoryQueryResult;
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  /**
   * Get memory service status
   */
  async getStatus(): Promise<MemoryStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      return await response.json() as MemoryStatus;
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  /**
   * Check if memory service is enabled
   */
  isEnabled(): boolean {
    return this.enabled;
  }
}

export default MemoryClient;
