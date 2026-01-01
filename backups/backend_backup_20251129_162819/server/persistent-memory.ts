/**
 * Persistent Cross-Session Memory for Aurora
 * Stores conversation history and user preferences in the database
 */

import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'data', 'aurora-memory.db');
const db = new Database(DB_PATH);

// Enable WAL mode for better concurrency
db.pragma('journal_mode = WAL');

// Create tables for persistent memory
db.exec(`
  CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id TEXT,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp INTEGER NOT NULL DEFAULT (unixepoch()),
    metadata TEXT DEFAULT '{}'
  );

  CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id, timestamp);
  CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation_history(user_id, timestamp);

  CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT PRIMARY KEY,
    preferences TEXT NOT NULL DEFAULT '{}',
    created_at INTEGER NOT NULL DEFAULT (unixepoch()),
    updated_at INTEGER NOT NULL DEFAULT (unixepoch())
  );

  CREATE TABLE IF NOT EXISTS user_context (
    user_id TEXT PRIMARY KEY,
    context_summary TEXT,
    interests TEXT DEFAULT '[]',
    expertise_level TEXT DEFAULT 'intermediate',
    preferred_languages TEXT DEFAULT '[]',
    last_active INTEGER NOT NULL DEFAULT (unixepoch()),
    interaction_count INTEGER DEFAULT 0
  );
`);

console.log('[Persistent Memory] 🧠 Database initialized at:', DB_PATH);

// ══════════════════════════════════════════════════════════════
// Conversation History
// ══════════════════════════════════════════════════════════════

export interface ConversationMessage {
  id?: number;
  session_id: string;
  user_id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
  metadata?: Record<string, any>;
}

export function saveMessage(message: ConversationMessage): void {
  const stmt = db.prepare(`
    INSERT INTO conversation_history (session_id, user_id, role, content, metadata)
    VALUES (?, ?, ?, ?, ?)
  `);

  stmt.run(
    message.session_id,
    message.user_id || null,
    message.role,
    message.content,
    JSON.stringify(message.metadata || {})
  );
}

export function getConversationHistory(
  sessionId: string,
  limit: number = 20
): ConversationMessage[] {
  const stmt = db.prepare(`
    SELECT * FROM conversation_history
    WHERE session_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
  `);

  const rows = stmt.all(sessionId, limit) as any[];
  
  return rows.reverse().map(row => ({
    id: row.id,
    session_id: row.session_id,
    user_id: row.user_id,
    role: row.role,
    content: row.content,
    timestamp: row.timestamp,
    metadata: JSON.parse(row.metadata)
  }));
}

export function getUserConversations(
  userId: string,
  limit: number = 50
): ConversationMessage[] {
  const stmt = db.prepare(`
    SELECT * FROM conversation_history
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
  `);

  const rows = stmt.all(userId, limit) as any[];
  
  return rows.map(row => ({
    id: row.id,
    session_id: row.session_id,
    user_id: row.user_id,
    role: row.role,
    content: row.content,
    timestamp: row.timestamp,
    metadata: JSON.parse(row.metadata)
  }));
}

export function clearOldConversations(daysToKeep: number = 30): number {
  const cutoffTimestamp = Math.floor(Date.now() / 1000) - (daysToKeep * 24 * 60 * 60);
  
  const stmt = db.prepare(`
    DELETE FROM conversation_history
    WHERE timestamp < ?
  `);

  const result = stmt.run(cutoffTimestamp);
  return result.changes;
}

// ══════════════════════════════════════════════════════════════
// User Preferences & Context
// ══════════════════════════════════════════════════════════════

export interface UserPreferences {
  theme?: 'light' | 'dark';
  language?: string;
  notifications?: boolean;
  [key: string]: any;
}

export function saveUserPreferences(userId: string, preferences: UserPreferences): void {
  const stmt = db.prepare(`
    INSERT INTO user_preferences (user_id, preferences, updated_at)
    VALUES (?, ?, unixepoch())
    ON CONFLICT(user_id) DO UPDATE SET
      preferences = excluded.preferences,
      updated_at = unixepoch()
  `);

  stmt.run(userId, JSON.stringify(preferences));
}

export function getUserPreferences(userId: string): UserPreferences | null {
  const stmt = db.prepare(`
    SELECT preferences FROM user_preferences WHERE user_id = ?
  `);

  const row = stmt.get(userId) as any;
  return row ? JSON.parse(row.preferences) : null;
}

export interface UserContext {
  user_id: string;
  context_summary?: string;
  interests?: string[];
  expertise_level?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  preferred_languages?: string[];
  last_active?: number;
  interaction_count?: number;
}

export function updateUserContext(context: UserContext): void {
  const stmt = db.prepare(`
    INSERT INTO user_context (
      user_id, context_summary, interests, expertise_level, 
      preferred_languages, last_active, interaction_count
    )
    VALUES (?, ?, ?, ?, ?, unixepoch(), COALESCE(?, 0) + 1)
    ON CONFLICT(user_id) DO UPDATE SET
      context_summary = COALESCE(excluded.context_summary, context_summary),
      interests = COALESCE(excluded.interests, interests),
      expertise_level = COALESCE(excluded.expertise_level, expertise_level),
      preferred_languages = COALESCE(excluded.preferred_languages, preferred_languages),
      last_active = unixepoch(),
      interaction_count = interaction_count + 1
  `);

  stmt.run(
    context.user_id,
    context.context_summary || null,
    JSON.stringify(context.interests || []),
    context.expertise_level || 'intermediate',
    JSON.stringify(context.preferred_languages || []),
    context.interaction_count || 0
  );
}

export function getUserContext(userId: string): UserContext | null {
  const stmt = db.prepare(`
    SELECT * FROM user_context WHERE user_id = ?
  `);

  const row = stmt.get(userId) as any;
  
  if (!row) return null;

  return {
    user_id: row.user_id,
    context_summary: row.context_summary,
    interests: JSON.parse(row.interests),
    expertise_level: row.expertise_level,
    preferred_languages: JSON.parse(row.preferred_languages),
    last_active: row.last_active,
    interaction_count: row.interaction_count
  };
}

// Clean up database on exit
process.on('exit', () => {
  db.close();
});
