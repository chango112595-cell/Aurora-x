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
      console.log('[WebSocket] New client connected from:', req.socket.remoteAddress);

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

      ws.on('pong', () => {
        console.log('[WebSocket] Received pong from client');
      });

      // Send initial connection confirmation
      ws.send(JSON.stringify({
        type: 'connected',
        message: 'Connected to synthesis progress WebSocket',
        timestamp: new Date().toISOString()
      }));
    });

    this.wss.on('error', (error) => {
      console.error('[WebSocket] WebSocketServer error:', error);
    });

    // Heartbeat to keep connections alive
    const heartbeat = setInterval(() => {
      this.wss.clients.forEach((ws) => {
        // Check if the client is still in our map (it might have been removed by 'close' or 'error' handlers)
        if (this.clients.has(ws as WebSocket) && (ws as WebSocket).readyState === WebSocket.OPEN) {
          (ws as WebSocket).ping();
        }
      });
    }, 30000); // Send ping every 30 seconds

    // Ensure heartbeat interval is cleared when the server closes
    this.wss.on('close', () => {
      clearInterval(heartbeat);
      console.log('[WebSocket] WebSocket server closed');
    });

    console.log('[WebSocket] WebSocket server initialized on /ws/synthesis');
  }


  private handleMessage(ws: WebSocket, data: any): void {
    const client = this.clients.get(ws);
    if (!client) {
      console.warn('[WebSocket] Received message from unknown client, closing connection.');
      ws.close(1008, 'Unknown client'); // 1008: Policy Violation
      return;
    }

    switch (data.type) {
      case 'subscribe':
        if (data.synthesisId) {
          client.synthesisIds.add(data.synthesisId);
          console.log(`[WebSocket] Client subscribed to synthesis: ${data.synthesisId}`);

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
        } else {
          ws.send(JSON.stringify({ type: 'error', error: 'Missing synthesisId for subscribe' }));
        }
        break;

      case 'unsubscribe':
        if (data.synthesisId) {
          client.synthesisIds.delete(data.synthesisId);
          console.log(`[WebSocket] Client unsubscribed from synthesis: ${data.synthesisId}`);
        } else {
          ws.send(JSON.stringify({ type: 'error', error: 'Missing synthesisId for unsubscribe' }));
        }
        break;

      case 'ping':
        // Respond to ping with pong to keep connection alive
        ws.send(JSON.stringify({ type: 'pong' }));
        break;

      default:
        console.warn(`[WebSocket] Received unknown message type: ${data.type} from client`);
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
        client.ws.send(message, (error) => {
          if (error) {
            console.error(`[WebSocket] Error sending progress to client for synthesis ${progress.id}:`, error);
            // Optionally, could trigger client cleanup here if send fails consistently
          }
        });
      }
    });
  }

  // Send message to specific synthesis subscribers
  sendToSynthesisSubscribers(synthesisId: string, message: any): void {
    const messageStr = JSON.stringify(message);

    this.clients.forEach((client) => {
      if (client.synthesisIds.has(synthesisId) && client.ws.readyState === WebSocket.OPEN) {
        client.ws.send(messageStr, (error) => {
          if (error) {
            console.error(`[WebSocket] Error sending message to client for synthesis ${synthesisId}:`, error);
          }
        });
      }
    });
  }
}

// Export a function to create and attach the WebSocket server
export function createWebSocketServer(httpServer: Server): SynthesisWebSocketServer {
  return new SynthesisWebSocketServer(httpServer);
}