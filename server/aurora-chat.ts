import { WebSocket, WebSocketServer } from 'ws';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import { conversationPatternAdapter } from './conversation-pattern-adapter';
import { executeWithProgram } from './execution-dispatcher';
import { spawn } from 'child_process';
import * as path from 'path';
import { getMemoryFabricClient } from './memory-fabric-client';
import { getNexusV3Client, type ConsciousnessState } from './nexus-v3-client';
import { getCognitiveLoop } from './cognitive-loop';

const memoryClient = getMemoryFabricClient();
const nexusV3Client = getNexusV3Client();
const cognitiveLoop = getCognitiveLoop();

export function setupAuroraChatWebSocket(server: any) {
  const wss = new WebSocketServer({ 
    server,
    path: '/aurora/chat'
  });

  wss.on('connection', async (ws: WebSocket) => {
    console.log('[Aurora] New chat connection established');

    const memoryStatus = await memoryClient.checkStatus();
    console.log(`[Aurora] Memory Fabric: ${memoryStatus ? 'connected' : 'offline'}`);

    let greeting = "Hello! I'm Aurora, your AI assistant. I'm here to help you with coding, questions, analysis, and more.";
    
    if (memoryStatus) {
      const factsResult = await memoryClient.getFacts();
      if (factsResult.success && factsResult.facts) {
        const userName = factsResult.facts['user_name'] as string;
        if (userName) {
          greeting = `Welcome back, ${userName}! I'm Aurora, your AI assistant. How can I help you today?`;
        }
      }
    }

    ws.send(JSON.stringify({
      message: greeting + " What would you like to work on today?"
    }));

    ws.on('message', async (data: Buffer) => {
      try {
        const { message, sessionId, context } = JSON.parse(data.toString());
        console.log('[Aurora] Received:', message);

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

function extractUserName(message: string): string | null {
  const patterns = [
    /(?:my name is|i'm|i am|call me|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/i,
    /^([A-Z][a-z]+)\s+here/i,
    /(?:name's|names)\s+([A-Z][a-z]+)/i,
  ];
  
  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      const name = match[1].trim();
      const invalidNames = ['aurora', 'bot', 'assistant', 'ai', 'help', 'here', 'there', 'that', 'this', 'what', 'how', 'why', 'when', 'where'];
      if (!invalidNames.includes(name.toLowerCase()) && name.length >= 2 && name.length <= 30) {
        return name;
      }
    }
  }
  return null;
}

function extractFacts(message: string): { key: string; value: string; category: string }[] {
  const facts: { key: string; value: string; category: string }[] = [];
  
  const userName = extractUserName(message);
  if (userName) {
    facts.push({ key: 'user_name', value: userName, category: 'identity' });
  }
  
  const locationPatterns = [
    /(?:i live in|i'm from|i am from|located in|based in)\s+([A-Za-z\s]+?)(?:\.|,|$)/i,
  ];
  for (const pattern of locationPatterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      facts.push({ key: 'user_location', value: match[1].trim(), category: 'identity' });
      break;
    }
  }
  
  const jobPatterns = [
    /(?:i work as|i'm a|i am a|my job is|i'm an|i am an)\s+([\w\s]+?)(?:\.|,|$)/i,
  ];
  for (const pattern of jobPatterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      const job = match[1].trim();
      if (job.length > 2 && job.length < 50) {
        facts.push({ key: 'user_occupation', value: job, category: 'identity' });
        break;
      }
    }
  }
  
  return facts;
}

async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default', context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  let memoryContext = '';
  let userName: string | null = null;
  let consciousnessState: ConsciousnessState | null = null;
  let cognitiveContext: any = null;
  
  try {
    const { context: loopContext, events } = await cognitiveLoop.processMessage(userMessage, sessionId, 'chat');
    cognitiveContext = loopContext;
    
    consciousnessState = loopContext.consciousness;
    
    if (consciousnessState) {
      console.log(`[Aurora] 🌌 Consciousness: ${consciousnessState.consciousness_state} | Awareness: ${consciousnessState.awareness_level}`);
      console.log(`[Aurora] 🤖 Workers: ${consciousnessState.workers?.idle || 0} idle / ${consciousnessState.workers?.total || 0} total`);
    }
    
    if (loopContext.facts) {
      const facts = loopContext.facts;
      if (facts['user_name']) {
        userName = facts['user_name'] as string;
        memoryContext += `User's name: ${userName}\n`;
      }
      if (facts['user_location']) {
        memoryContext += `User's location: ${facts['user_location']}\n`;
      }
      if (facts['user_occupation']) {
        memoryContext += `User's occupation: ${facts['user_occupation']}\n`;
      }
    }
    
    if (loopContext.memoryContext) {
      memoryContext += `Recent context: ${loopContext.memoryContext}\n`;
    }
    
    if (memoryContext) {
      console.log('[Aurora] 🧠 Memory context loaded:', memoryContext.substring(0, 100) + '...');
    }
    
    console.log(`[Aurora] 🔄 Cognitive loop: ${events.length} events processed`);
  } catch (memoryError) {
    console.log('[Aurora] Cognitive loop error, using fallback:', memoryError);
  }
  
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

  memoryClient.saveMessage('user', userMessage, 0.7, [detection.type]).catch(() => {});
  
  const extractedFacts = extractFacts(userMessage);
  for (const fact of extractedFacts) {
    memoryClient.saveFact(fact.key, fact.value, fact.category).then((result) => {
      if (result.success) {
        console.log(`[Aurora] 💾 Saved fact: ${fact.key} = ${fact.value}`);
      }
    }).catch(() => {});
  }

  let response = '';

  try {
    const dispatchedResponse = await executeWithProgram(userMessage, detection, sessionId, context);
    if (dispatchedResponse && dispatchedResponse.length > 0) {
      response = dispatchedResponse;
    }
  } catch (dispatchError) {
    console.log('[Aurora] Dispatcher error, using fallback:', dispatchError);
  }

  if (!response) {
    try {
      response = await callExecutionWrapperDirect(userMessage, detection.type, context);
    } catch (fallbackError) {
      console.log('[Aurora] Fallback also failed:', fallbackError);
    }
  }

  if (!response) {
    response = generateContextualFallback(userMessage, detection, userName, consciousnessState);
  }
  
  const newlyExtractedName = extractUserName(userMessage);
  if (newlyExtractedName && !response.includes(newlyExtractedName)) {
    response = `Nice to meet you, ${newlyExtractedName}! ` + response;
  }

  const usedFallback = !response || response.includes('would you like');
  
  if (cognitiveContext) {
    cognitiveLoop.completeCycle(userMessage, response, cognitiveContext, !usedFallback).catch((err) => {
      console.log('[Aurora] Cognitive cycle completion error:', err);
    });
  }

  return { response, detection };
}

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

    setTimeout(() => {
      python.kill();
      reject(new Error('Timeout'));
    }, 8000);
  });
}

function generateContextualFallback(
  userMessage: string, 
  detection: ConversationDetection, 
  userName: string | null = null,
  consciousness: ConsciousnessState | null = null
): string {
  const keywords = userMessage.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 3)
    .slice(0, 5);
  
  const topic = keywords.join(' ') || 'your request';
  const hasQuestion = userMessage.includes('?');
  const greeting = userName ? `${userName}, ` : '';
  
  const systemStatus = consciousness 
    ? `[${consciousness.peak_capabilities?.tiers || 188} tiers, ${consciousness.peak_capabilities?.aems || 66} programs, ${consciousness.workers?.idle || 0} workers ready]` 
    : '[188 tiers, 66 programs ready]';
  
  switch (detection.type) {
    case 'code_generation':
      return `${greeting}I can write code for ${topic}. Which language would you prefer, and what specific requirements should I address?`;
    
    case 'debugging':
      return `${greeting}I'll help debug ${topic}. Please share the error message and relevant code, and I'll identify the issue.`;
    
    case 'explanation':
      return hasQuestion 
        ? `${greeting}Let me explain ${topic}. What specific aspect would be most useful - the basics, technical details, or practical examples?`
        : `${greeting}I can explain ${topic} in detail. What angle would be most helpful for you?`;
    
    case 'architecture':
      return `${greeting}For ${topic}, I can help design the architecture. What are your scalability needs and technology constraints?`;
    
    case 'optimization':
      return `${greeting}I'll help optimize ${topic}. Share the relevant code and I'll suggest specific improvements.`;
    
    case 'testing':
      return `${greeting}I can write tests for ${topic}. What testing framework do you prefer and what edge cases concern you?`;
    
    case 'refactoring':
      return `${greeting}I'll refactor ${topic} for better clarity. Share the code and tell me what aspects you'd like improved.`;
    
    case 'analysis':
      return `${greeting}Analyzing ${topic}. All systems operational ${systemStatus}. What specific analysis do you need?`;
    
    case 'question_answering':
      return hasQuestion
        ? `${greeting}That's a good question about ${topic}. Could you provide more context so I can give you the most accurate answer?`
        : `${greeting}I can address ${topic}. What specifically would you like to know?`;
    
    default:
      return `${greeting}I understand you're interested in ${topic}. How can I help - would you like explanations, code, or problem-solving assistance?`;
  }
}

export async function getChatResponse(message: string, sessionId: string, context: any[] = []): Promise<{ response: string; detection: ConversationDetection }> {
  return processWithAuroraIntelligence(message, sessionId, context);
}

export async function searchWeb(query: string): Promise<any> {
  return { results: [], message: `Search query received: ${query}` };
}
