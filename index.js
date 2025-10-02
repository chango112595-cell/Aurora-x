#!/usr/bin/env node
/**
 * Node.js wrapper to run Aurora-X Python application
 */

const { spawn } = require('child_process');

console.log('🚀 Starting Aurora-X Ultra - Offline Autonomous Coding Engine');
console.log('=' .repeat(50));

// Run the Python application
const python = spawn('python', ['run.py'], { 
  stdio: 'inherit',
  env: process.env 
});

python.on('error', (err) => {
  console.error('Failed to start Aurora-X:', err);
  process.exit(1);
});

python.on('exit', (code) => {
  console.log(`Aurora-X exited with code ${code}`);
  process.exit(code);
});