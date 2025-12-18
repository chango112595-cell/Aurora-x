/**
 * Aurora Memory Fabric v2 Client - TypeScript interface to Python Memory Fabric v2 service
 */

import fetch from 'node-fetch';

export interface MemoryEntry {
  id: string;
  content: string;
  role: string;
  timestamp: string;
  layer: string;
  importance: number;
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface MemoryStats {
  shortTermCount: number;
  midTermCount: number;
  longTermCount: number;
  semanticCount: number;
  factCount: number;
  eventCount: number;
  totalMemories: number;
  activeProject: string;
  sessionId: string;
}

export interface MemoryEvent {
  timestamp: string;
  type?: string;
  event?: string;
  detail?: Record<string, unknown>;
  project?: string;
}

export interface MemoryFabricStatus {
  success: boolean;
  stats?: MemoryStats;
  facts?: Record<string, unknown>;
  shortTerm?: MemoryEntry[];
  midTerm?: MemoryEntry[];
  longTerm?: MemoryEntry[];
  semantic?: MemoryEntry[];
  events?: MemoryEvent[];
  conversations?: string[];
  error?: string;
}

export class MemoryFabricClient {
  private baseUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 5004) {
    this.baseUrl = `http://127.0.0.1:${port}`;
  }

  async checkStatus(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json() as MemoryFabricStatus;
        this.enabled = data.success === true;
        return this.enabled;
      }
      return false;
    } catch (error) {
      this.enabled = false;
      return false;
    }
  }

  async getStatus(): Promise<MemoryFabricStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        return await response.json() as MemoryFabricStatus;
      }
      return { success: false, error: 'Failed to get status' };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async getFacts(): Promise<{ success: boolean; facts?: Record<string, unknown>; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/facts`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      return await response.json() as { success: boolean; facts?: Record<string, unknown>; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async getContext(): Promise<{ success: boolean; context?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/context`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      return await response.json() as { success: boolean; context?: string; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async getIntegrity(): Promise<{ success: boolean; integrity?: Record<string, string>; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/integrity`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      return await response.json() as { success: boolean; integrity?: Record<string, string>; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async getConversation(conversationId: string): Promise<{ success: boolean; messages?: MemoryEntry[]; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/conversation/${conversationId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      return await response.json() as { success: boolean; messages?: MemoryEntry[]; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async saveMessage(
    role: string,
    content: string,
    importance: number = 0.5,
    tags: string[] = []
  ): Promise<{ success: boolean; entry?: MemoryEntry; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role, content, importance, tags })
      });

      return await response.json() as { success: boolean; entry?: MemoryEntry; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async saveFact(
    key: string,
    value: unknown,
    category: string = 'general'
  ): Promise<{ success: boolean; key?: string; value?: unknown; category?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/fact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value, category })
      });

      return await response.json() as { success: boolean; key?: string; value?: unknown; category?: string; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async recallFact(key: string): Promise<{ success: boolean; key?: string; value?: unknown; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/recall`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key })
      });

      return await response.json() as { success: boolean; key?: string; value?: unknown; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async search(
    query: string,
    topK: number = 5
  ): Promise<{ success: boolean; results?: MemoryEntry[]; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
      });

      return await response.json() as { success: boolean; results?: MemoryEntry[]; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async setProject(name: string): Promise<{ success: boolean; project?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });

      return await response.json() as { success: boolean; project?: string; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async newConversation(): Promise<{ success: boolean; conversationId?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/conversation/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      return await response.json() as { success: boolean; conversationId?: string; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async backup(): Promise<{ success: boolean; backupPath?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/backup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      return await response.json() as { success: boolean; backupPath?: string; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async logEvent(
    type: string,
    detail: Record<string, unknown> = {}
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, detail })
      });

      return await response.json() as { success: boolean; error?: string };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let memoryFabricClient: MemoryFabricClient | null = null;

export function getMemoryFabricClient(): MemoryFabricClient {
  if (!memoryFabricClient) {
    memoryFabricClient = new MemoryFabricClient(5004);
  }
  return memoryFabricClient;
}

export default MemoryFabricClient;
