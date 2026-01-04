/// <reference types="vite/client" />

// API Configuration for Aurora dual-backend architecture
export const API_CONFIG = {
  // Express gateway (main backend)
  EXPRESS_BASE: (import.meta.env?.VITE_API_BASE as string) || 'http://0.0.0.0:5000',

  // Aurora AI backend (intelligence service)
  AI_BASE: (import.meta.env?.VITE_AI_BASE as string) || 'http://0.0.0.0:8000',

  // WebSocket endpoints
  WS_CHAT: ((import.meta.env?.VITE_WS_BASE as string) || 'ws://0.0.0.0:8000') + '/ws/chat',

  // Timeout settings
  TIMEOUT: 30000,
  WS_RECONNECT_DELAY: 3000,
};

export default API_CONFIG;
