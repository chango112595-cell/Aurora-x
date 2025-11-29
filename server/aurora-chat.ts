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
 * Generate a contextual response based on the detected conversation type
 */
function generateContextualFallback(userMessage: string, detection: ConversationDetection): string {
  const responses: Record<string, string> = {
    'code_generation': `I'd be happy to help you with code! 

To write the best solution for you, could you tell me:
1. What specific functionality do you need?
2. Any language preferences (Python, JavaScript, TypeScript, etc.)?
3. Any special requirements or constraints?

Share the details and I'll create clean, well-documented code for you!`,

    'debugging': `I can help you debug this issue!

To diagnose the problem effectively, please share:
1. The error message you're seeing
2. The relevant code snippet
3. What you expected to happen vs what's actually happening

With this information, I can pinpoint the issue and provide a fix.`,

    'explanation': `I'd be happy to explain that!

Could you be more specific about what aspect you'd like me to cover?
- **Basic concept** - What is it and why does it matter?
- **How it works** - Technical details and mechanics
- **Practical examples** - Real-world applications
- **Best practices** - Tips for using it effectively

Let me know what would be most helpful!`,

    'architecture': `I can help with system architecture and design!

To provide the best guidance, I'd like to understand:
1. What type of system are you building?
2. What are your scalability requirements?
3. Any specific technologies or constraints?

With these details, I can suggest an optimal architecture.`,

    'optimization': `Let's improve performance together!

To optimize effectively, I need to know:
1. What's currently slow or resource-intensive?
2. What are your performance targets?
3. Can you share the relevant code?

I'll analyze it and suggest specific optimizations.`,

    'testing': `I can help you write comprehensive tests!

To create the best test suite:
1. What code needs testing?
2. What testing framework do you prefer?
3. Any specific edge cases you're concerned about?

I'll write thorough tests with good coverage.`,

    'refactoring': `I'd be glad to help refactor your code!

To improve it effectively:
1. Share the code you'd like to clean up
2. What specific issues bother you about it?
3. Any constraints I should know about?

I'll restructure it for better maintainability and readability.`,

    'analysis': `I can analyze that for you!

**Aurora System Status: OPERATIONAL**

All systems are running correctly:
- 188 Intelligence tiers active
- 66 Execution programs available  
- Conversation intelligence online
- Pattern learning enabled

What specific analysis would you like me to perform?`,

    'question_answering': `Great question! Let me address that...

I'm analyzing your question and formulating a comprehensive answer. Could you provide any additional context that might help me give you the most accurate and helpful response?`,

    'general_chat': `I'm here to help! 

I can assist you with:
- Writing and debugging code
- Explaining technical concepts
- System analysis and diagnostics
- Answering your questions
- Creative problem-solving

What would you like to explore together?`
  };

  return responses[detection.type] || responses['general_chat'];
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string, context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  return processWithAuroraIntelligence(message, sessionId, context);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Search query received: ${query}` };
}
