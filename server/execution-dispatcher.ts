import { spawn } from 'child_process';
import { conversationDetector, type ConversationDetection } from './conversation-detector';

/**
 * EXECUTION PROGRAM DISPATCHER
 * Routes conversation types to specialized execution programs
 */

export interface ExecutionProgram {
  name: string;
  toolPath: string;
  types: string[]; // conversation types this handles
  priority: number;
}

// Map conversation types to Python execution programs
const EXECUTION_PROGRAMS: ExecutionProgram[] = [
  {
    name: 'Debug Grandmaster',
    toolPath: 'tools/aurora_debug_grandmaster.py',
    types: ['debugging', 'error_analysis'],
    priority: 10
  },
  {
    name: 'Autonomous Fixer',
    toolPath: 'tools/aurora_autonomous_fixer.py',
    types: ['debugging', 'error_recovery'],
    priority: 9
  },
  {
    name: 'Self Healer',
    toolPath: 'tools/aurora_self_heal.py',
    types: ['debugging', 'optimization'],
    priority: 8
  },
  {
    name: 'Core Intelligence',
    toolPath: 'tools/aurora_core.py',
    types: ['code_generation', 'explanation', 'general_chat'],
    priority: 1 // fallback
  }
];

/**
 * Get the appropriate execution program for a conversation type
 */
function getExecutionProgram(detectionType: string): ExecutionProgram {
  const program = EXECUTION_PROGRAMS.find(p => p.types.includes(detectionType));
  return program || EXECUTION_PROGRAMS[EXECUTION_PROGRAMS.length - 1]; // fallback to core
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
  console.log(`[Dispatcher] 📍 Program: ${program.toolPath}`);
  
  return executeProgram(program.toolPath, {
    message: userMessage,
    type: detection.type,
    confidence: detection.confidence,
    executionMode: detection.executionMode,
    sessionId,
    context: context.slice(-4), // last 4 messages
    keywords: detection.keywords
  });
}

/**
 * Execute a Python program with JSON input/output
 */
function executeProgram(toolPath: string, input: any): Promise<string> {
  return new Promise((resolve, reject) => {
    const script = `
import sys
import json
sys.path.insert(0, '${process.cwd().replace(/\\/g, '/')}')

try:
    # Load the execution program module
    module_name = '${toolPath.replace(/\\.py$/, '').replace(/\\//g, '.')}' 
    module = __import__(module_name.split('.')[-1])
    
    # Execute with input
    if hasattr(module, 'execute'):
        result = module.execute(json.loads('''${JSON.stringify(input).replace(/'/g, "\\'")}'''))
    elif hasattr(module, run'):
        result = module.run(json.loads('''${JSON.stringify(input).replace(/'/g, "\\'")}'''))
    else:
        result = "Program executed"
    
    print(json.dumps({'result': result}))
except Exception as e:
    print(json.dumps({'error': str(e)}))
`;

    const python = spawn('python3', ['-c', script]);
    let output = '';
    let errors = '';

    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => errors += data.toString());

    python.on('close', (code) => {
      try {
        const jsonLine = output.split('\n').find(l => l.trim().startsWith('{'));
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine);
          if (parsed.error) {
            resolve(`Program returned error: ${parsed.error}`);
          } else {
            resolve(parsed.result || 'Execution completed');
          }
        } else {
          resolve(output.trim() || 'Program executed');
        }
      } catch (e) {
        resolve(output.trim() || `Execution completed (output parsing: ${e})`);
      }
    });

    setTimeout(() => reject(new Error('Execution timeout')), 30000);
  });
}

/**
 * List available execution programs
 */
export function listExecutionPrograms(): ExecutionProgram[] {
  return EXECUTION_PROGRAMS;
}
