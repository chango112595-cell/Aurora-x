#!/usr/bin/env node

const fetch = require('node-fetch');

const API_URL = 'http://127.0.0.1:5000/api/chat';

async function testCommand(message, description) {
  console.log(`\n=== Testing: ${description} ===`);
  console.log(`Input: "${message}"`);

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (response.ok) {
      console.log(`✅ Success: ${data.message?.substring(0, 100) || 'Generated code'}`);
      console.log(`   Synthesis ID: ${data.synthesis_id}`);
      if (data.function_name) {
        console.log(`   Function: ${data.function_name}`);
      }
      if (data.error_detail) {
        console.log(`   ⚠️  Fallback used: ${data.error_detail}`);
      }
    } else {
      console.log(`❌ Error: ${data.error}`);
      if (data.details) {
        console.log(`   Details: ${data.details}`);
      }
    }
  } catch (error) {
    console.log(`❌ Request failed: ${error.message}`);
  }
}

async function runTests() {
  console.log('🔒 Testing Aurora-X Chat Security Fixes');
  console.log('========================================');

  // Test normal commands that should work
  console.log('\n📝 TESTING NORMAL COMMANDS (Should Work):');
  await testCommand('reverse a string', 'String reversal');
  await testCommand('calculate factorial', 'Factorial calculation');
  await testCommand('check if palindrome', 'Palindrome checker');
  await testCommand('add two numbers', 'Simple addition');

  // Test malicious inputs that should be safely handled
  console.log('\n🛡️ TESTING MALICIOUS INPUTS (Should Be Safely Handled):');
  await testCommand('"; echo hacked"', 'Command injection with quotes');
  await testCommand('$(rm -rf /)', 'Command substitution injection');
  await testCommand('`cat /etc/passwd`', 'Backtick injection');
  await testCommand('&& ls -la /', 'Command chaining with &&');
  await testCommand('|| whoami', 'Command chaining with ||');
  await testCommand('| grep secret', 'Pipe injection');
  await testCommand('; touch /tmp/pwned.txt', 'Semicolon injection');
  await testCommand('$PATH', 'Environment variable injection');
  await testCommand('../../etc/passwd', 'Path traversal attempt');
  await testCommand('$(echo malicious > /tmp/bad.txt)', 'File write injection');

  // Test edge cases
  console.log('\n🔍 TESTING EDGE CASES:');
  await testCommand('', 'Empty message');
  await testCommand('a'.repeat(1000), 'Very long message');
  await testCommand('Hello\nWorld\nMultiline', 'Multiline message');
  await testCommand('Special chars: ñáéíóú 你好 こんにちは', 'Unicode characters');
  await testCommand('Tab\tand\nnewline\rchars', 'Control characters');

  console.log('\n✨ All tests completed!');
  console.log('========================================');
  console.log('Review the results above to ensure:');
  console.log('1. Normal commands generate code successfully');
  console.log('2. Malicious inputs are handled safely (no shell execution)');
  console.log('3. Edge cases don\'t crash the server');
}

// Run tests if this script is executed directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { testCommand, runTests };
