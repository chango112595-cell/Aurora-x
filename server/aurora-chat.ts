import { WebSocket, WebSocketServer } from 'ws';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import { conversationPatternAdapter } from './conversation-pattern-adapter';
import { spawn, execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { getMemoryFabricClient } from './memory-fabric-client';
import { getNexusV3Client, type ConsciousnessState } from './nexus-v3-client';
import { getCognitiveLoop } from './cognitive-loop';
import { resolvePythonCommand } from './python-runtime';
import type { Server } from 'http';
import { 
  executeWithOrchestrator, 
  selectExecutionMethod, 
  getSystemPromptWithCapabilities,
  getCapabilities,
  type ExecutionResult,
  type ExecutionContext
} from './aurora-execution-orchestrator';

interface ChatMessage {
  content: string;
  role?: string;
}

interface CognitiveLoopContext {
  consciousness: ConsciousnessState | null;
  facts?: Record<string, string | number | boolean>;
  memoryContext?: string;
  recentEvents?: unknown[];
}

interface ExecutionWrapperResult {
  success: boolean;
  result?: string | Record<string, unknown>;
}

const memoryClient = getMemoryFabricClient();
const nexusV3Client = getNexusV3Client();
const cognitiveLoop = getCognitiveLoop();
const PYTHON_CMD = resolvePythonCommand();

export function setupAuroraChatWebSocket(server: Server) {
  const wss = new WebSocketServer({ 
    server,
    path: '/aurora/chat'
  });

  wss.on('connection', async (ws: WebSocket) => {
    const memoryStatus = await memoryClient.checkStatus();

    let greeting = "Hello! I'm Aurora. What would you like me to do?";
    
    if (memoryStatus) {
      const factsResult = await memoryClient.getFacts();
      if (factsResult.success && factsResult.facts) {
        const userName = factsResult.facts['user_name'] as string;
        if (userName) {
          greeting = `Welcome back, ${userName}! What would you like me to do?`;
        }
      }
    }

    ws.send(JSON.stringify({ message: greeting }));

    ws.on('message', async (data: Buffer) => {
      try {
        const { message, sessionId, context } = JSON.parse(data.toString());

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
        ws.send(JSON.stringify({
          message: "Error processing request: " + (error as Error).message
        }));
      }
    });

    ws.on('close', () => {
    });
  });
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
  
  return facts;
}

async function analyzeCodebaseIssues(): Promise<string> {
  const issues: string[] = [];
  const cwd = process.cwd();
  
  try {
    const serverDir = path.join(cwd, 'server');
    const clientDir = path.join(cwd, 'client');
    
    if (fs.existsSync(serverDir)) {
      const serverFiles = fs.readdirSync(serverDir).filter(f => f.endsWith('.ts'));
      for (const file of serverFiles.slice(0, 20)) {
        try {
          const content = fs.readFileSync(path.join(serverDir, file), 'utf-8');
          
          if (content.includes('// TODO') || content.includes('// FIXME')) {
            const todoMatch = content.match(/\/\/\s*(TODO|FIXME)[:\s]+([^\n]+)/gi);
            if (todoMatch) {
              issues.push(`server/${file}: ${todoMatch.slice(0, 2).join(', ')}`);
            }
          }
          
          if (content.includes('throw new Error') && !content.includes('try {')) {
            issues.push(`server/${file}: Has unhandled throw statements`);
          }
          
          if (content.includes('any') && content.includes(': any')) {
            const anyCount = (content.match(/:\s*any/g) || []).length;
            if (anyCount > 3) {
              issues.push(`server/${file}: Uses 'any' type ${anyCount} times - reduces type safety`);
            }
          }
        } catch {
        }
      }
    }
    
    const envExample = path.join(cwd, '.env.example');
    const envFile = path.join(cwd, '.env');
    if (fs.existsSync(envExample) && !fs.existsSync(envFile)) {
      issues.push('Missing .env file (template exists at .env.example)');
    }
    
    const packageJson = path.join(cwd, 'package.json');
    if (fs.existsSync(packageJson)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf-8'));
        const deps = { ...pkg.dependencies, ...pkg.devDependencies };
        
        const outdatedPatterns = [
          { name: 'react', min: '18' },
          { name: 'typescript', min: '5' },
          { name: 'express', min: '4' },
        ];
        
        for (const { name, min } of outdatedPatterns) {
          if (deps[name]) {
            const version = deps[name].replace(/[\^~]/g, '');
            const major = parseInt(version.split('.')[0]);
            if (major < parseInt(min)) {
              issues.push(`package.json: ${name}@${version} may need upgrade (recommend v${min}+)`);
            }
          }
        }
      } catch {
      }
    }
    
    try {
      const result = execSync('npm ls 2>&1 | grep -i "UNMET\\|missing\\|invalid" | head -5', { 
        cwd, 
        encoding: 'utf-8',
        timeout: 5000 
      }).trim();
      if (result) {
        issues.push(`npm dependencies: ${result.split('\n').length} issues detected`);
      }
    } catch {
    }
    
    const checkPaths = [
      'server/anthropic-service.ts',
      'server/aurora.ts',
      'server/aurora-core.ts',
    ];
    
    for (const checkPath of checkPaths) {
      const fullPath = path.join(cwd, checkPath);
      if (fs.existsSync(fullPath)) {
        try {
          const content = fs.readFileSync(fullPath, 'utf-8');
          
          if (content.includes('process.env.') && content.includes('API_KEY')) {
            const keyMatch = content.match(/process\.env\.(\w+_API_KEY)/g);
            if (keyMatch) {
              for (const key of keyMatch) {
                const envVar = key.replace('process.env.', '');
                if (!process.env[envVar]) {
                  issues.push(`${checkPath}: ${envVar} not configured`);
                }
              }
            }
          }
          
          if (content.includes('fetch(') || content.includes('axios')) {
            const urlMatches = content.match(/(?:fetch|axios)\s*\(\s*['"`]([^'"`]+)['"`]/g);
            if (urlMatches) {
              for (const match of urlMatches) {
                if (match.includes('localhost') || match.includes('127.0.0.1')) {
                  const port = match.match(/:(\d+)/)?.[1];
                  if (port) {
                    issues.push(`${checkPath}: References localhost:${port} - may need external service`);
                  }
                }
              }
            }
          }
        } catch {
        }
      }
    }
    
  } catch (error) {
    issues.push(`Analysis error: ${(error as Error).message}`);
  }
  
  if (issues.length === 0) {
    return "**Codebase Analysis Complete**\n\nNo critical issues detected. The codebase appears to be in good shape.";
  }
  
  return `**Codebase Analysis - ${issues.length} Issues Found**\n\n${issues.map((issue, i) => `${i + 1}. ${issue}`).join('\n')}`;
}

async function analyzeIntegrationStatus(): Promise<string> {
  const status: { working: string[]; notWorking: string[]; unknown: string[] } = {
    working: [],
    notWorking: [],
    unknown: []
  };
  
  const cwd = process.cwd();
  
  if (process.env.ANTHROPIC_API_KEY) {
    status.working.push('Anthropic API (key configured)');
  } else {
    status.notWorking.push('Anthropic API (ANTHROPIC_API_KEY not set)');
  }
  
  if (process.env.OPENAI_API_KEY) {
    status.working.push('OpenAI API (key configured)');
  } else {
    status.unknown.push('OpenAI API (key not set - may not be needed)');
  }
  
  if (process.env.DATABASE_URL || process.env.PGHOST) {
    status.working.push('PostgreSQL Database (configured)');
  } else {
    status.unknown.push('PostgreSQL Database (no DATABASE_URL - using memory storage)');
  }
  
  const services = [
    { name: 'Memory Fabric', port: 5004 },
    { name: 'Memory Bridge', port: 5003 },
    { name: 'Luminar Nexus V2', port: 8000 },
    { name: 'Nexus V3', port: 5002 },
  ];
  
  for (const service of services) {
    try {
      const response = await fetch(`http://127.0.0.1:${service.port}/`, { 
        method: 'GET',
        signal: AbortSignal.timeout(500) 
      });
      if (response.ok || response.status < 500) {
        status.working.push(`${service.name} (port ${service.port})`);
      } else {
        status.notWorking.push(`${service.name} (port ${service.port} - error ${response.status})`);
      }
    } catch {
      status.notWorking.push(`${service.name} (port ${service.port} - not responding)`);
    }
  }
  
  const checkFiles = [
    { path: 'server/routes.ts', name: 'Express Routes' },
    { path: 'server/storage.ts', name: 'Storage Layer' },
    { path: 'client/src/App.tsx', name: 'React Frontend' },
    { path: 'shared/schema.ts', name: 'Data Schema' },
  ];
  
  for (const file of checkFiles) {
    const fullPath = path.join(cwd, file.path);
    if (fs.existsSync(fullPath)) {
      status.working.push(`${file.name} (${file.path})`);
    } else {
      status.notWorking.push(`${file.name} (${file.path} missing)`);
    }
  }
  
  let report = '**Integration Status Report**\n\n';
  
  if (status.working.length > 0) {
    report += `**Working (${status.working.length}):**\n${status.working.map(s => `- ${s}`).join('\n')}\n\n`;
  }
  
  if (status.notWorking.length > 0) {
    report += `**Not Working (${status.notWorking.length}):**\n${status.notWorking.map(s => `- ${s}`).join('\n')}\n\n`;
  }
  
  if (status.unknown.length > 0) {
    report += `**Unknown/Optional (${status.unknown.length}):**\n${status.unknown.map(s => `- ${s}`).join('\n')}\n`;
  }
  
  return report;
}

async function executeFileOperation(message: string): Promise<string | null> {
  const cwd = process.cwd();
  const msgLower = message.toLowerCase();
  
  const listMatch = msgLower.match(/(?:list|show|what)\s+(?:files?|are)\s+(?:in|inside)?\s*(.+)?/);
  if (listMatch || msgLower.includes('list files') || msgLower.includes('show files')) {
    const dirPath = listMatch?.[1]?.trim() || '.';
    const targetPath = path.join(cwd, dirPath.replace(/^\//, ''));
    
    if (fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory()) {
      const files = fs.readdirSync(targetPath).slice(0, 50);
      return `**Files in ${dirPath}:**\n\n${files.map(f => {
        const stat = fs.statSync(path.join(targetPath, f));
        return `- ${f}${stat.isDirectory() ? '/' : ''}`;
      }).join('\n')}`;
    }
  }
  
  const readMatch = message.match(/(?:read|show|display|cat|open)\s+(?:file\s+)?([^\s]+\.[a-z]+)/i);
  if (readMatch) {
    const filePath = readMatch[1];
    const fullPath = path.join(cwd, filePath);
    
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf-8');
      const lines = content.split('\n');
      const preview = lines.slice(0, 50).join('\n');
      return `**${filePath}** (${lines.length} lines):\n\n\`\`\`\n${preview}\n${lines.length > 50 ? '\n... (truncated)' : ''}\n\`\`\``;
    } else {
      return `File not found: ${filePath}`;
    }
  }
  
  const searchMatch = message.match(/(?:search|find|grep)\s+(?:for\s+)?['"]?([^'"]+)['"]?\s+(?:in\s+)?(.+)?/i);
  if (searchMatch) {
    const pattern = searchMatch[1].trim();
    const searchPath = searchMatch[2]?.trim() || '.';
    
    try {
      const result = execSync(
        `grep -rn --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" "${pattern}" ${searchPath} 2>/dev/null | head -20`,
        { cwd, encoding: 'utf-8', timeout: 5000 }
      ).trim();
      
      if (result) {
        return `**Search results for "${pattern}":**\n\n\`\`\`\n${result}\n\`\`\``;
      } else {
        return `No matches found for "${pattern}"`;
      }
    } catch {
      return `No matches found for "${pattern}"`;
    }
  }
  
  return null;
}

async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default', context: ChatMessage[] = []): Promise<{ response: string; detection: ConversationDetection; aemUsed?: { id: number; name: string } }> {
  let memoryContext = '';
  let userName: string | null = null;
  let consciousnessState: ConsciousnessState | null = null;
  let cognitiveContext: CognitiveLoopContext | null = null;
  
  try {
    const { context: loopContext, events } = await cognitiveLoop.processMessage(userMessage, sessionId, 'chat');
    cognitiveContext = loopContext as CognitiveLoopContext;
    consciousnessState = loopContext.consciousness;
    
    if (loopContext.facts) {
      const facts = loopContext.facts;
      if (facts['user_name']) {
        userName = facts['user_name'] as string;
        memoryContext += `User's name: ${userName}\n`;
      }
    }
  } catch {
  }
  
  const previousMessages = context
    .filter((msg: ChatMessage) => typeof msg === 'object' && 'content' in msg)
    .slice(-4)
    .map((msg: ChatMessage) => msg.content)
    .filter(Boolean);

  const detection = conversationDetector.detect(userMessage, previousMessages);
  conversationDetector.addMessageToHistory(userMessage);

  conversationPatternAdapter.sendPatternToV2(detection, userMessage, previousMessages.join(' ')).catch(() => {});
  memoryClient.saveMessage('user', userMessage, 0.7, [detection.type]).catch(() => {});
  
  const extractedFacts = extractFacts(userMessage);
  for (const fact of extractedFacts) {
    memoryClient.saveFact(fact.key, fact.value, fact.category).catch(() => {});
  }

  const selectedAEM = selectExecutionMethod(userMessage);
  console.log(`[Aurora] Selected AEM #${selectedAEM.id}: ${selectedAEM.name} for request`);

  const executionContext: ExecutionContext = {
    sessionId,
    userName: userName || undefined,
    capabilities: getCapabilities(),
    recentMessages: previousMessages
  };

  let response = '';
  let aemUsed = { id: selectedAEM.id, name: selectedAEM.name };
  const msgLower = userMessage.toLowerCase();

  if (msgLower.includes('not working') || msgLower.includes('not integrated') || 
      msgLower.includes('what\'s broken') || msgLower.includes("what is broken") ||
      msgLower.includes('issues') || msgLower.includes('problems') ||
      (msgLower.includes('tell me') && (msgLower.includes('not') || msgLower.includes('broken') || msgLower.includes('issues')))) {
    response = await analyzeIntegrationStatus();
    const codeIssues = await analyzeCodebaseIssues();
    response += '\n\n' + codeIssues;
  }
  else if (msgLower.includes('status') || msgLower.includes('integration')) {
    response = await analyzeIntegrationStatus();
  }
  else if (msgLower.includes('analyze') && (msgLower.includes('code') || msgLower.includes('codebase'))) {
    response = await analyzeCodebaseIssues();
  }
  else if (msgLower.includes('list files') || msgLower.includes('show files') || 
           msgLower.includes('read file') || msgLower.includes('search for') ||
           msgLower.includes('find ') || msgLower.includes('grep ')) {
    const fileResult = await executeFileOperation(userMessage);
    if (fileResult) {
      response = fileResult;
    }
  }
  else if (msgLower.match(/^(hi|hello|hey|greetings)/)) {
    response = userName 
      ? `Hello ${userName}! What would you like me to do?` 
      : "Hello! What would you like me to do?";
  }
  else if (msgLower.includes('who are you') || msgLower.includes('what are you')) {
    response = "I'm Aurora, an AI assistant integrated into this codebase. I can analyze your code, check integration status, search files, and help with development tasks. Try asking me 'what is not working' or 'analyze the codebase'.";
  }
  else if (msgLower.includes('help') || msgLower.includes('what can you do')) {
    response = `**Available Commands:**

1. **"What is not working?"** - Analyze integration status and find issues
2. **"Analyze the codebase"** - Check for code quality issues
3. **"List files in [directory]"** - Show files in a directory
4. **"Read file [path]"** - Display file contents
5. **"Search for [pattern]"** - Find text in code files
6. **"Status"** - Check service integrations

What would you like me to do?`;
  }

  if (!response) {
    const orchestratorResult = await executeWithOrchestrator(userMessage, executionContext);
    
    if (orchestratorResult.success && orchestratorResult.output) {
      aemUsed = { id: orchestratorResult.aemUsed, name: orchestratorResult.aemName };
      
      if (orchestratorResult.metadata?.requiresLLM) {
        try {
          const wrapperPath = path.join(process.cwd(), 'tools', 'execution_wrapper.py');
          if (fs.existsSync(wrapperPath)) {
            const result = await callExecutionWrapperDirect(userMessage, detection.type, context);
            if (result && result.length > 10 && !result.includes('would you like')) {
              response = `**[AEM #${aemUsed.id}: ${aemUsed.name}]**\n\n${result}`;
            }
          }
        } catch {
          response = orchestratorResult.output;
        }
      } else {
        response = `**[AEM #${aemUsed.id}: ${aemUsed.name}]**\n\n${orchestratorResult.output}`;
      }
    }
  }

  if (!response) {
    const caps = getCapabilities();
    response = `**[AEM #66: General Assistant]**

I have **${caps.aems} Advanced Execution Methods (hands)** ready to help you. Here's what I can do:

**Code Operations:**
- "Write code for [description]" - Code Generation (AEM #7)
- "Debug [issue]" - Debug Analysis (AEM #9)
- "Review this code" - Code Review (AEM #8)

**File Operations:**
- "Read file [path]" - File Read (AEM #10)
- "List files in [directory]" - Directory List (AEM #13)
- "Search for [pattern]" - File Search (AEM #12)

**Analysis:**
- "Status" or "How are you" - System Status (AEM #14)
- "Analyze codebase" - Codebase Analysis (AEM #15)
- "Check integrations" - Integration Check (AEM #16)

**Security & Performance:**
- "Security check" - Adversarial Analysis (AEM #4)
- "Optimize [component]" - Performance Analysis (AEM #24)

What would you like me to execute?`;
    aemUsed = { id: 66, name: 'General Assistant' };
  }

  if (cognitiveContext) {
    cognitiveLoop.completeCycle(userMessage, response, cognitiveContext, true).catch(() => {});
  }

  return { response, detection, aemUsed };
}

function callExecutionWrapperDirect(message: string, msgType: string, context: ChatMessage[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const wrapperPath = path.join(process.cwd(), 'tools', 'execution_wrapper.py');
    const inputData = JSON.stringify({
      message,
      type: msgType,
      context: context.slice(-4)
    });

    const python = spawn(PYTHON_CMD, [wrapperPath], { cwd: process.cwd() });
    let output = '';

    python.stdin.write(inputData);
    python.stdin.end();

    python.stdout.on('data', (data) => output += data.toString());

    python.on('close', () => {
      try {
        const lines = output.split('\n');
        const jsonLine = lines.find(l => l.trim().startsWith('{'));
        
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine.trim()) as ExecutionWrapperResult;
          if (parsed.success && parsed.result) {
            resolve(typeof parsed.result === 'string' ? parsed.result : JSON.stringify(parsed.result, null, 2));
            return;
          }
        }
        
        const cleanOutput = output.trim();
        if (cleanOutput) {
          resolve(cleanOutput);
        } else {
          reject(new Error('No output'));
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

export async function getChatResponse(message: string, sessionId: string, context: ChatMessage[] = []): Promise<{ response: string; detection: ConversationDetection; aemUsed?: { id: number; name: string } }> {
  return processWithAuroraIntelligence(message, sessionId, context);
}

interface SearchResult {
  results: unknown[];
  message: string;
}

export async function searchWeb(query: string): Promise<SearchResult> {
  return { results: [], message: `Search query received: ${query}` };
}
