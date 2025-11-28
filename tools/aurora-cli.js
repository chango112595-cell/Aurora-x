#!/usr/bin/env node

const message = process.argv.slice(2).join(' ');

if (!message) {
  console.error('Usage: node tools/aurora-cli.js "your message here"');
  console.error('Example: node tools/aurora-cli.js "write a sorting algorithm"');
  process.exit(1);
}

fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message })
})
  .then(res => res.json())
  .then(data => {
    console.log('\n📊 Detection:', data.type || 'unknown', 
      `(${data.confidence || 0}% confidence)`);
    console.log('\n💬 Aurora:\n');
    console.log(data.response || data.message || 'No response');
    console.log('\n');
  })
  .catch(err => console.error('Error:', err.message));
