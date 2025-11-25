import { WebSocket, WebSocketServer } from 'ws';

// Aurora's chat WebSocket server
export function setupAuroraChatWebSocket(server: any) {
  const wss = new WebSocketServer({ 
    server,
    path: '/aurora/chat'
  });

  wss.on('connection', (ws: WebSocket) => {
    console.log('[Aurora] New chat connection established');
    
    // Welcome message
    ws.send(JSON.stringify({
      message: 'Aurora online. All 27 mastery tiers active. How may I assist?'
    }));

    ws.on('message', async (data: Buffer) => {
      try {
        const { message, sessionId } = JSON.parse(data.toString());
        console.log('[Aurora] Received:', message);
        
        // Aurora processes the message using her omniscient knowledge
        const response = await processWithAuroraIntelligence(message, sessionId || 'websocket');
        
        ws.send(JSON.stringify({
          message: response
        }));
      } catch (error) {
        console.error('[Aurora] Error:', error);
        ws.send(JSON.stringify({
          message: 'Error processing request'
        }));
      }
    });

    ws.on('close', () => {
      console.log('[Aurora] Chat connection closed');
    });
  });

  console.log('[Aurora] Chat WebSocket server ready on /aurora/chat');
}

async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default'): Promise<string> {
  // Route through Aurora Core with 188 power units
  const { AuroraCore } = await import('./aurora-core');
  const aurora = AuroraCore.getInstance();
  
  try {
    // Use Aurora's analyze method which routes through Nexus V3
    const result = await aurora.analyze(userMessage, sessionId);
    const response = result.response || result.analysis || 'Aurora processed your request successfully.';
    // Aurora's autonomous type safety: ensure string response
    return typeof response === 'string' ? response : JSON.stringify(response);
  } catch (error: any) {
    console.error('[Aurora Chat] Intelligence error:', error);
    
    // Fallback: Try Python bridge directly
    try {
      const pythonResult = await aurora.callAuroraPython('analyze', {
        input: userMessage,
        context: 'chat'
      });
      const response = pythonResult.response || pythonResult.analysis || 'Aurora is thinking...';
      // Aurora's autonomous type safety
      return typeof response === 'string' ? response : JSON.stringify(response);
    } catch (pythonError) {
      console.error('[Aurora Chat] Python bridge error:', pythonError);
      return `I'm Aurora with 188 power units. I received: "${userMessage}". My intelligence system is connecting. Please try again.`;
    }
  }
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string): Promise<string> {
  return processWithAuroraIntelligence(message, sessionId);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Searching for: ${query}` };
}
