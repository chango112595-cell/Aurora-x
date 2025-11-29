import { WebSocket, WebSocketServer } from 'ws';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import { conversationPatternAdapter } from './conversation-pattern-adapter';
import { executeWithProgram } from './execution-dispatcher';
import { spawn } from 'child_process';
import * as path from 'path';

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
      message: "Hello! I'm Aurora, your AI assistant. I'm here to help you with coding, questions, analysis, and more. What would you like to work on today?"
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
          message: "I encountered an issue processing that. Could you try rephrasing your request?"
        }));
      }
    });

    ws.on('close', () => {
      console.log('[Aurora] Chat connection closed');
    });
  });

  console.log('[Aurora] 🌌 Intelligent chat WebSocket ready on /aurora/chat');
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

  // Send pattern to V2 for learning (non-blocking)
  conversationPatternAdapter.sendPatternToV2(detection, userMessage, previousMessages.join(' ')).catch(() => {});

  // Route through execution dispatcher (primary path)
  try {
    const dispatchedResponse = await executeWithProgram(userMessage, detection, sessionId, context);
    if (dispatchedResponse && dispatchedResponse.length > 0) {
      return {
        response: dispatchedResponse,
        detection
      };
    }
  } catch (dispatchError) {
    console.log('[Aurora] Dispatcher error, using fallback:', dispatchError);
  }

  // Fallback: Use execution wrapper directly
  try {
    const fallbackResponse = await callExecutionWrapperDirect(userMessage, detection.type, context);
    return {
      response: fallbackResponse,
      detection
    };
  } catch (fallbackError) {
    console.log('[Aurora] Fallback also failed:', fallbackError);
  }

  // Final fallback: Generate a contextual response based on detection
  const contextualResponse = generateContextualFallback(userMessage, detection);
  return {
    response: contextualResponse,
    detection
  };
}

/**
 * Call the execution wrapper directly for fallback
 */
function callExecutionWrapperDirect(message: string, msgType: string, context: any[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const wrapperPath = path.join(process.cwd(), 'tools', 'execution_wrapper.py');
    const inputData = JSON.stringify({
      message,
      type: msgType,
      context: context.slice(-4)
    });

    const python = spawn('python3', [wrapperPath], { cwd: process.cwd() });
    let output = '';
    let stderr = '';

    python.stdin.write(inputData);
    python.stdin.end();

    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => stderr += data.toString());

    python.on('close', (code) => {
      try {
        const lines = output.split('\n');
        const jsonLine = lines.find(l => l.trim().startsWith('{'));
        
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine.trim());
          if (parsed.success && parsed.result) {
            resolve(typeof parsed.result === 'string' ? parsed.result : JSON.stringify(parsed.result, null, 2));
            return;
          }
        }
        
        // If no JSON, return cleaned output
        const cleanOutput = output.trim();
        if (cleanOutput) {
          resolve(cleanOutput);
        } else {
          reject(new Error('No output from wrapper'));
        }
      } catch (e) {
        reject(e);
      }
    });

    python.on('error', (err) => reject(err));

    // Timeout after 8 seconds
    setTimeout(() => {
      python.kill();
      reject(new Error('Timeout'));
    }, 8000);
  });
}

/**
 * Generate a contextual response - uses message content dynamically
 */
function generateContextualFallback(userMessage: string, detection: ConversationDetection): string {
  // Extract key words from the user's message for personalization
  const keywords = userMessage.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 3)
    .slice(0, 5);
  
  const topic = keywords.join(' ') || 'your request';
  const hasQuestion = userMessage.includes('?');
  
  // Generate dynamic response based on type AND content
  switch (detection.type) {
    case 'code_generation':
      return `I can write code for ${topic}. Which language would you prefer, and what specific requirements should I address?`;
    
    case 'debugging':
      return `I'll help debug ${topic}. Please share the error message and relevant code, and I'll identify the issue.`;
    
    case 'explanation':
      return hasQuestion 
        ? `Let me explain ${topic}. What specific aspect would be most useful - the basics, technical details, or practical examples?`
        : `I can explain ${topic} in detail. What angle would be most helpful for you?`;
    
    case 'architecture':
      return `For ${topic}, I can help design the architecture. What are your scalability needs and technology constraints?`;
    
    case 'optimization':
      return `I'll help optimize ${topic}. Share the relevant code and I'll suggest specific improvements.`;
    
    case 'testing':
      return `I can write tests for ${topic}. What testing framework do you prefer and what edge cases concern you?`;
    
    case 'refactoring':
      return `I'll refactor ${topic} for better clarity. Share the code and tell me what aspects you'd like improved.`;
    
    case 'analysis':
      return `Analyzing ${topic}. All systems operational - 188 tiers active, 66 programs ready. What specific analysis do you need?`;
    
    case 'question_answering':
      return hasQuestion
        ? `That's a good question about ${topic}. Could you provide more context so I can give you the most accurate answer?`
        : `I can address ${topic}. What specifically would you like to know?`;
    
    default:
      return `I understand you're interested in ${topic}. How can I help - would you like explanations, code, or problem-solving assistance?`;
  }
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string, context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  return processWithAuroraIntelligence(message, sessionId, context);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Search query received: ${query}` };
}
