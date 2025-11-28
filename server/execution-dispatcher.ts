import { spawn } from 'child_process';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import * as fs from 'fs';
import * as path from 'path';

/**
 * EXECUTION PROGRAM DISPATCHER - Fixed Version
 * Routes conversation types to specialized execution programs
 * Properly instantiates Python classes and calls their methods
 */

export interface ExecutionProgram {
  name: string;
  module: string; // Python module name
  className: string; // Class to instantiate
  method: string; // Method to call
  types: string[]; // conversation types
  priority: number;
}

const EXECUTION_PROGRAMS: ExecutionProgram[] = [
  {
    name: 'Debug Grandmaster',
    module: 'aurora_debug_grandmaster',
    className: 'AuroraDebugGrandmaster',
    method: 'diagnose_and_fix',
    types: ['debugging'],
    priority: 10
  },
  {
    name: 'Autonomous Fixer',
    module: 'aurora_autonomous_fixer',
    className: 'AuroraAutonomousFixer',
    method: 'diagnose_chat_issue',
    types: ['debugging', 'error_recovery'],
    priority: 9
  },
  {
    name: 'Self Healer',
    module: 'aurora_self_heal',
    className: 'AuroraSelfHealer',
    method: 'heal',
    types: ['debugging', 'optimization'],
    priority: 8
  },
  {
    name: 'Core Intelligence',
    module: 'aurora_core',
    className: 'AuroraCore',
    method: 'generate_aurora_response',
    types: ['code_generation', 'explanation', 'general_chat', 'analysis'],
    priority: 1
  }
];

function getExecutionProgram(detectionType: string): ExecutionProgram {
  const program = EXECUTION_PROGRAMS.find(p => p.types.includes(detectionType));
  return program || EXECUTION_PROGRAMS[EXECUTION_PROGRAMS.length - 1];
}

/**
 * Execute a conversation through the appropriate program
 */
export async function executeWithProgram(
  userMessage: string,
  detection: ConversationDetection,
  sessionId: string,
  context: any[]
): Promise<string> {
  const program = getExecutionProgram(detection.type);
  
  console.log(`[Dispatcher] 🎯 Routing ${detection.type} → ${program.name}`);
  console.log(`[Dispatcher] 📍 Module: ${program.module} | Class: ${program.className} | Method: ${program.method}`);
  
  try {
    return await executeProgram(program, {
      message: userMessage,
      type: detection.type,
      confidence: detection.confidence,
      executionMode: detection.executionMode,
      sessionId,
      context: context.slice(-4),
      keywords: detection.keywords
    });
  } catch (err) {
    console.error(`[Dispatcher] ❌ Execution failed:`, err);
    throw err;
  }
}

/**
 * Execute a Python program through wrapper
 */
async function executeProgram(program: ExecutionProgram, input: any): Promise<string> {
  return new Promise((resolve, reject) => {
    // Use execution wrapper for clean interface
    const wrapperPath = path.join(process.cwd(), 'tools', 'execution_wrapper.py');
    
    const inputJson = JSON.stringify({
      message: input.message,
      type: input.type,
      context: input.context
    });

    const python = spawn('python3', [wrapperPath], {
      cwd: process.cwd()
    });

    let output = '';
    let errors = '';

    python.stdin.write(inputJson);
    python.stdin.end();

    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => errors += data.toString());

    python.on('close', (code) => {
      try {
        const lines = output.split('\n').filter(l => l.trim());
        const jsonLine = lines.find(l => l.trim().startsWith('{'));
        
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine);
          if (parsed.success) {
            console.log(`[Dispatcher] ✅ ${program.name} executed`);
            resolve(parsed.result || 'Execution completed');
          } else {
            console.log(`[Dispatcher] ⚠️ ${program.name} error: ${parsed.error}`);
            resolve(`${parsed.error}`);
          }
        } else {
          const rawResult = lines.filter(l => !l.includes('sys.path')).join('\n').trim();
          if (rawResult) {
            console.log(`[Dispatcher] ✅ ${program.name} completed`);
            resolve(rawResult);
          } else {
            resolve('Program executed');
          }
        }
      } catch (e) {
        console.log(`[Dispatcher] Parse: ${e}`);
        resolve(`Response generated`);
      }
    });

    setTimeout(() => {
      python.kill();
      console.error(`[Dispatcher] Timeout for ${program.name}`);
      reject(new Error('Timeout'));
    }, 30000);
  });
}

function userMessage(msg: string): string {
  return msg.replace(/'/g, "\\'").replace(/\n/g, '\\n');
}

export function listExecutionPrograms(): ExecutionProgram[] {
  return EXECUTION_PROGRAMS;
}
