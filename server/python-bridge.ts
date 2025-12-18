/**
 * Python bridge for calling Aurora-X Python modules from TypeScript
 */

import { spawn } from 'child_process';
import { resolvePythonCommand } from './python-runtime';

export async function callPythonSolver(text: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonCmd = resolvePythonCommand();
    const pythonScript = `
import sys
import json
sys.path.insert(0, '.')
from aurora_x.generators.solver import solve_text

text = """${text.replace(/"/g, '\\"')}"""
result = solve_text(text)
print(json.dumps(result))
`;

    const python = spawn(pythonCmd, ['-c', pythonScript]);
    let output = '';
    let error = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${error}`));
      } else {
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${output}`));
        }
      }
    });
  });
}
