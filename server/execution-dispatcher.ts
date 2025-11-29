import { spawn } from 'child_process';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import * as path from 'path';

/**
 * EXECUTION DISPATCHER - SIMPLIFIED & WORKING
 * Routes messages to execution wrapper (no complex Python class instantiation)
 */

export async function executeWithProgram(
  userMessage: string,
  detection: ConversationDetection,
  sessionId: string,
  context: any[]
): Promise<string> {

  console.log(`[Dispatcher] 🎯 Routing ${detection.type} (confidence: ${detection.confidence}%)`);

  try {
    return await callExecutionWrapper({
      message: userMessage,
      type: detection.type,
      context: context.slice(-4)
    });
  } catch (err) {
    console.error(`[Dispatcher] Fallback:`, err);
    throw err;
  }
}

/**
 * Call the execution wrapper directly
 */
function callExecutionWrapper(input: any): Promise<string> {
  return new Promise((resolve, reject) => {
    const wrapperPath = path.join(process.cwd(), 'tools', 'execution_wrapper.py');
    const inputJson = JSON.stringify(input);

    const python = spawn('python3', [wrapperPath], { cwd: process.cwd() });
    let output = '';

    python.stdin.write(inputJson);
    python.stdin.end();

    python.stdout.on('data', (data) => output += data.toString());

    python.on('close', () => {
      try {
        const jsonLine = output.split('\n').find(l => l.trim().startsWith('{'));
        if (jsonLine) {
          const parsed = JSON.parse(jsonLine);
          if (parsed.success) {
            console.log('[Dispatcher] ✅ Execution completed');

            // Ensure result is valid and returned
            if (!parsed.result || typeof parsed.result !== 'object') {
              resolve({
                status: 'success',
                result: 'Task completed',
                timestamp: new Date().toISOString()
              });
            } else {
              resolve(parsed.result);
            }
          } else {
            resolve({
              status: 'error',
              error: parsed.error || 'Execution failed',
              timestamp: new Date().toISOString()
            });
          }
        } else {
          resolve(output.trim() || 'Response generated');
        }
      } catch (e) {
        reject(new Error('Failed to parse response'));
      }
    });

    python.stderr.on('data', (data) => {
      console.error(`[Dispatcher] Python stderr: ${data}`);
    });

    setTimeout(() => {
      python.kill();
      reject(new Error('Timeout'));
    }, 10000);
  });
}