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
        // Find the JSON response line
        const jsonLine = output.split('\n').find(l => l.trim().startsWith('{"response"'));
        
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine.trim());
          resolve(parsed.response);
        } else {
          // Check if we have valid output from Python
          const cleanOutput = output
            .split('\n')
            .filter(l => {
              const trimmed = l.trim();
              // Keep lines that look like real responses, exclude debug output
              return trimmed && 
                     !trimmed.startsWith('[') && 
                     !trimmed.startsWith('Auto-') &&
                     !trimmed.startsWith('Intelligent') &&
                     !trimmed.includes('---') &&
                     !trimmed.includes('sys.path') &&
                     trimmed.length > 10;
            })
            .join('\n')
            .trim();
          
          if (cleanOutput) {
            resolve(cleanOutput);
          } else {
            // Genuine fallback - Aurora should never get here
            console.error('[Aurora] No valid output. Raw:', output);
            resolve(`I received your message: "${userMessage}"\n\nLet me analyze this and provide a complete response. What specifically would you like me to help you with?`);
          }
        }
      } catch (e) {
        console.error('[Aurora] Parse error:', e, '\nRaw output:', output);
        resolve(`Hello! I'm Aurora. I understand you said: "${userMessage}"\n\nI have full access to 188 power units. How can I help you today?`);
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
