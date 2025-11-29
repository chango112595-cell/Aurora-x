import { WebSocket, WebSocketServer } from 'ws';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import { conversationPatternAdapter } from './conversation-pattern-adapter';
import { executeWithProgram } from './execution-dispatcher';

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
        const { message, sessionId, context } = JSON.parse(data.toString());
        console.log('[Aurora] Received:', message);

        // Aurora processes the message with auto-detection
        const { response, detection } = await processWithAuroraIntelligence(message, sessionId || 'websocket', context);

        ws.send(JSON.stringify({
          message: response,
          detection: {
            type: detection.type,
            confidence: detection.confidence,
            executionMode: detection.executionMode
          }
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

async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default', context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  // Auto-detect conversation type and adapt strategy
  const previousMessages = context
    .filter((msg: any) => typeof msg === 'object' && 'content' in msg)
    .slice(-4)
    .map((msg: any) => msg.content)
    .filter(Boolean);

  const detection = conversationDetector.detect(userMessage, previousMessages);
  conversationDetector.addMessageToHistory(userMessage);

  console.log(`[Aurora] 🔍 Detected: ${detection.type} (confidence: ${detection.confidence}%)`);
  console.log(`[Aurora] 📋 Format: ${detection.suggestedFormat} | Mode: ${detection.executionMode}`);

  conversationPatternAdapter.sendPatternToV2(detection, userMessage, previousMessages.join(' ')).catch(() => {});

  // Route through execution dispatcher
  try {
    const dispatchedResponse = await executeWithProgram(userMessage, detection, sessionId, context);
    return {
      response: dispatchedResponse,
      detection
    };
  } catch (dispatchError) {
    console.log('[Aurora] Dispatcher fallback to core intelligence');
  }

  // Fallback: Call Aurora's REAL Python intelligence with detection parameters
  const { spawn } = await import('child_process');

  return new Promise((resolve) => {
    // Include detection info in the Python context
    const detectionContext = JSON.stringify({
      type: detection.type,
      executionMode: detection.executionMode,
      suggestedFormat: detection.suggestedFormat,
      keywords: detection.keywords,
      tone: detection.tone
    }).replace(/'/g, "\\'");

    // Generate format instructions based on detection
    const formatInstructions = conversationDetector.generateFormatInstructions(detection);

    const script = `
import sys
import json
import os
sys.path.insert(0, '${process.cwd().replace(/\\/g, '/')}')

# Suppress ALL debug output
os.environ['AURORA_DEBUG'] = '0'

from aurora_core import AuroraCoreIntelligence

try:
    aurora = AuroraCoreIntelligence()

    # Get context FIRST
    context = aurora.get_conversation_context('${sessionId}')

    # Add detection info to context
    context['detection'] = json.loads('''${detectionContext}''')

    # Analyze message with detection awareness
    analysis = aurora.analyze_natural_language('''${userMessage.replace(/'/g, "\\'")}''', context)

    # Generate response with format instructions
    response = aurora.generate_aurora_response(analysis, context, '${sessionId}')

    # Output ONLY clean JSON
    print(json.dumps({'response': response}, ensure_ascii=False))

except Exception as e:
    # Error response
    print(json.dumps({'response': f'I encountered an error: {str(e)}. Let me try again...'}, ensure_ascii=False))
`;

    const python = spawn('python', ['-c', script]);
    let output = '';
    let errors = '';

    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => errors += data.toString());

    python.on('close', (code) => {
      try {
        // First try to find JSON response
        const jsonLine = output.split('\n').find(l => l.trim().startsWith('{"response"'));

        if (jsonLine) {
          const parsed = JSON.parse(jsonLine.trim());
          resolve({ 
            response: parsed.response,
            detection
          });
        } else {
          // Extract clean output, excluding debug lines
          const lines = output.split('\n');
          const cleanLines = lines.filter(l => {
            const trimmed = l.trim();
            // Exclude debug markers and very short lines
            return trimmed && 
                   !trimmed.startsWith('[') && 
                   !trimmed.includes('sys.path') &&
                   !trimmed.startsWith('Auto-') &&
                   !trimmed.startsWith('Intelligent') &&
                   trimmed.length > 5;
          });

          const cleanOutput = cleanLines.join('\n').trim();

          if (cleanOutput) {
            resolve({ 
              response: cleanOutput,
              detection
            });
          } else {
            // Last resort: return raw output if we got something
            const rawOutput = output.trim();
            if (rawOutput) {
              resolve({ 
                response: rawOutput,
                detection
              });
            } else {
              console.error('[Aurora] No output from Python. Stderr:', errors);
              resolve({ 
                response: `I'm processing your request: "${userMessage}"\n\nPlease try rephrasing or let me know what you need help with.`,
                detection
              });
            }
          }
        }
      } catch (e) {
        console.error('[Aurora] Parse error:', e, '\nRaw output:', output, '\nStderr:', errors);
        // Return what we have rather than a generic message
        const fallbackOutput = output.trim() || errors.trim();
        resolve({ 
          response: fallbackOutput || `Error processing your request. Please try again.`,
          detection
        });
      }
    });

    setTimeout(() => {
      python.kill();
      resolve({ 
        response: `Processing your request: "${userMessage}". Please wait...`,
        detection
      });
    }, 10000);
  });
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string, context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  return processWithAuroraIntelligence(message, sessionId, context);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Searching for: ${query}` };
}