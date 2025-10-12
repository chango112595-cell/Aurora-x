import { WebSocketServer, WebSocket } from 'ws';
import { Server } from 'http';
import { progressStore, type ProgressEntry } from './progress-store';

interface WSClient {
  ws: WebSocket;
  synthesisIds: Set<string>;
}

export class SynthesisWebSocketServer {
  private wss: WebSocketServer;
  private clients: Map<WebSocket, WSClient> = new Map();
  
  constructor(server: Server) {
    this.wss = new WebSocketServer({ 
      server,
      path: '/ws/synthesis'
    });

    this.setupWebSocketServer();
    
    // Cleanup old progress entries every 30 minutes
    setInterval(() => progressStore.cleanup(), 30 * 60 * 1000);
  }

  private setupWebSocketServer(): void {
    this.wss.on('connection', (ws: WebSocket, req) => {
      console.log('[WebSocket] New client connected');
      
      const client: WSClient = {
        ws,
        synthesisIds: new Set()
      };
      
      this.clients.set(ws, client);

      ws.on('message', (message: Buffer) => {
        try {
          const data = JSON.parse(message.toString());
          this.handleMessage(ws, data);
        } catch (error) {
          console.error('[WebSocket] Error parsing message:', error);
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid message format'
          }));
        }
      });

      ws.on('close', () => {
        console.log('[WebSocket] Client disconnected');
        this.clients.delete(ws);
      });

      ws.on('error', (error) => {
        console.error('[WebSocket] WebSocket error:', error);
        this.clients.delete(ws);
      });

      // Send initial connection confirmation
      ws.send(JSON.stringify({
        type: 'connected',
        message: 'Connected to synthesis progress WebSocket'
      }));
    });
  }

  private handleMessage(ws: WebSocket, data: any): void {
    const client = this.clients.get(ws);
    if (!client) return;

    switch (data.type) {
      case 'subscribe':
        if (data.synthesisId) {
          client.synthesisIds.add(data.synthesisId);
          
          // Send current progress immediately
          const progress = progressStore.getProgress(data.synthesisId);
          if (progress) {
            ws.send(JSON.stringify({
              type: 'progress',
              data: progress
            }));
          } else {
            ws.send(JSON.stringify({
              type: 'error',
              error: `Synthesis ${data.synthesisId} not found`
            }));
          }
        }
        break;
        
      case 'unsubscribe':
        if (data.synthesisId) {
          client.synthesisIds.delete(data.synthesisId);
        }
        break;
        
      case 'ping':
        ws.send(JSON.stringify({ type: 'pong' }));
        break;
        
      default:
        ws.send(JSON.stringify({
          type: 'error',
          error: `Unknown message type: ${data.type}`
        }));
    }
  }

  // Broadcast progress update to all subscribed clients
  broadcastProgress(progress: ProgressEntry): void {
    const message = JSON.stringify({
      type: 'progress',
      data: progress
    });

    this.clients.forEach((client) => {
      if (client.synthesisIds.has(progress.id) && client.ws.readyState === WebSocket.OPEN) {
        client.ws.send(message);
      }
    });
  }

  // Send message to specific synthesis subscribers
  sendToSynthesisSubscribers(synthesisId: string, message: any): void {
    const messageStr = JSON.stringify(message);
    
    this.clients.forEach((client) => {
      if (client.synthesisIds.has(synthesisId) && client.ws.readyState === WebSocket.OPEN) {
        client.ws.send(messageStr);
      }
    });
  }
}

// Export a function to create and attach the WebSocket server
export function createWebSocketServer(httpServer: Server): SynthesisWebSocketServer {
  return new SynthesisWebSocketServer(httpServer);
}