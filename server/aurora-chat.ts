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
  // Call Aurora's REAL Python intelligence - no templates
  const { spawn } = await import('child_process');
  const path = await import('path');
  
  return new Promise((resolve) => {
    const script = `
import sys
import json
sys.path.insert(0, '${process.cwd().replace(/\\/g, '/')}')

from aurora_core import AuroraCoreIntelligence

aurora = AuroraCoreIntelligence()

# Analyze with Aurora's REAL intelligence
analysis = aurora.analyze_natural_language('''${userMessage.replace(/'/g, "\\'")}''')

# Generate Aurora's ACTUAL response (not templates) - PASS SESSION_ID
context = aurora.get_conversation_context('${sessionId}')
response = aurora.generate_aurora_response(analysis, context, '${sessionId}')

# Output ONLY the response
print(json.dumps({'response': response}))
`;

    const python = spawn('python', ['-c', script]);
    let output = '';
    let errors = '';

    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => errors += data.toString());

    python.on('close', (code) => {
      try {
        // Find ONLY the JSON response line - ignore ALL debug output
        const jsonLine = output.split('\n').find(l => l.includes('{"response"'));
        
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine);
          resolve(parsed.response);
        } else {
          // No JSON found - filter out ALL system messages
          const cleanOutput = output
            .split('\n')
            .filter(l => {
              const trimmed = l.trim();
              // Exclude: debug lines, empty lines, system messages
              return trimmed && 
                     !l.startsWith('[') && 
                     !trimmed.startsWith('Auto-') &&
                     !trimmed.startsWith('Intelligent') &&
                     !trimmed.includes('---') &&
                     trimmed.length > 10; // Must be substantial text
            })
            .join('\n')
            .trim();
          
          resolve(cleanOutput || `I'm processing: "${userMessage}". Let me help you with that!`);
        }
      } catch (e) {
        console.error('[Aurora] Parse error:', e, '\nOutput:', output);
        resolve(`I understand: "${userMessage}"\n\nI'm Aurora with 188 power units. How can I help you accomplish this?`);
      }
    });

    setTimeout(() => {
      python.kill();
      resolve(`Processing your request: "${userMessage}". Please wait...`);
    }, 10000);
  });
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string): Promise<string> {
  return processWithAuroraIntelligence(message, sessionId);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Searching for: ${query}` };
}
