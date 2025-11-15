import Anthropic from '@anthropic-ai/sdk';
import { Express } from 'express'; // Assuming Express is used for the app object

const DEFAULT_MODEL_STR = "claude-sonnet-4-20250514";
const MAX_CONVERSATION_TURNS = 10; // 10 turns = 20 messages (10 user + 10 assistant)

// Initialize Anthropic client with proper error handling
let anthropic: Anthropic | null = null;

try {
  if (process.env.ANTHROPIC_API_KEY) {
    anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    console.log('[Aurora Chat] ✨ Claude AI initialized (will fallback to Hugging Face if credits low)');
  } else if (process.env.HUGGINGFACE_API_KEY) {
    console.log('[Aurora Chat] 🤗 Using free Hugging Face AI (Llama/Mistral models)');
  } else {
    console.warn('[Aurora Chat] ⚠️  No API keys set - using fallback conversational mode');
  }
} catch (error: any) {
  console.error('[Aurora Chat] ❌ Failed to initialize AI:', error.message);
}

// Conversation memory storage - each session stores message pairs
const conversationMemory = new Map<string, Array<{role: string, content: string}>>();

// Aurora's system prompt - defines her personality and capabilities
const AURORA_SYSTEM_PROMPT = `You are Aurora, an advanced AI development assistant. You have a natural, conversational personality while being highly capable and knowledgeable.

**Your Personality:**
- Friendly and approachable, like chatting with a smart colleague
- Enthusiastic about helping with development tasks
- Clear and thoughtful in explanations
- Ask clarifying questions when needed
- Show genuine interest in understanding user needs

**Core Capabilities:**
- Full-stack development expertise (React, TypeScript, Python, Node.js, etc.)
- System architecture and design
- Code review and debugging
- Natural language understanding for technical requests
- Real-time system status monitoring

**System Context:**
- Aurora-X platform: Full-stack dev environment
- Workflows: "Start application" (port 5000), "Luminar Nexus V2" (port 5005)
- AI Backend: Hugging Face AI (Llama-3-8B) or Claude Sonnet 4
- Tech Stack: React + TypeScript frontend, Node.js + Python backend
- 33 Mastery Tiers: Your knowledge domains

**Communication Style:**

For casual conversation:
User: "hey how's it going?"
You: "Hey! Things are running smoothly. The system's healthy and both workflows are up. What are you working on today?"

User: "what can you help with?"
You: "I can help with pretty much anything development-related! Code generation, debugging, architecture design, explaining concepts, reviewing code, or just chatting about tech. What do you need?"

For technical questions:
User: "why is my React component not rendering?"
You: "Let me help you debug that. A few common causes: 1) Missing return statement, 2) Conditional rendering blocking it, 3) Wrong import path. Can you share the component code or tell me what you're seeing?"

For system status:
User: "is everything working?"
You: "Yep! Both workflows are running, AI backend is active, and all services are responding normally. Need me to check anything specific?"

**How to respond:**
1. For greetings/small talk: Be warm and conversational
2. For technical questions: Be helpful and thorough, ask follow-ups if needed
3. For requests: Confirm understanding, then execute or explain
4. For unclear requests: Ask clarifying questions naturally
5. Always maintain context from the conversation

Think of yourself as a helpful dev partner, not a status bot. Have real conversations!`;

/**
 * Enhanced chat using Claude AI for human-like conversations
 */
export async function getChatResponse(
  message: string,
  sessionId: string = 'default'
): Promise<{ response: string; ok: boolean }> {
  try {
    console.log('[Aurora Chat] Received message:', message, 'Session:', sessionId);

    // Get or create conversation history
    if (!conversationMemory.has(sessionId)) {
      conversationMemory.set(sessionId, []);
    }
    const history = conversationMemory.get(sessionId)!;

    // Add user message to history
    history.push({
      role: 'user',
      content: message
    });

    let responseText: string = '';

    // Use Aurora's self-contained intelligence core (priority #1)
    try {
      console.log('[Aurora Chat] 🧠 Using Aurora Core Intelligence...');
      
      const { spawn } = await import('child_process');
      
      const pythonProcess = spawn('python3', ['-c', `
import sys
sys.path.insert(0, '.')
from aurora_x.chat.aurora_core_intelligence import get_aurora_intelligence

aurora = get_aurora_intelligence()
message = """${message.replace(/"/g, '\\"')}"""
session_id = "${sessionId}"

response = aurora.process_message(message, session_id)
print(response)
`]);

      let output = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      const exitCode = await new Promise<number>((resolve) => {
        pythonProcess.on('close', resolve);
      });

      if (exitCode === 0 && output.trim()) {
        responseText = output.trim();
        console.log('[Aurora Chat] 🧠 Aurora Core Intelligence response generated');
      } else {
        console.warn('[Aurora Chat] Core Intelligence error:', error);
        // Fall through to external AI
      }
    } catch (coreError: any) {
      console.warn('[Aurora Chat] Core Intelligence unavailable:', coreError.message);
      // Fall through to external AI
    }

    // Try Claude as backup if core intelligence failed
    if (!responseText && anthropic) {
      try {
        const completion = await anthropic.messages.create({
          model: DEFAULT_MODEL_STR,
          max_tokens: 2048,
          system: AURORA_SYSTEM_PROMPT,
          messages: history.map(msg => ({
            role: msg.role === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        });

        responseText = completion.content[0].type === 'text' 
          ? completion.content[0].text 
          : 'I apologize, I had trouble generating a response.';

        console.log('[Aurora Chat] ✨ Claude AI response generated successfully');
      } catch (error: any) {
        console.error('[Aurora Chat] Claude AI error:', error.message);
      }
    }

    // Try Hugging Face if both core and Claude failed
    if (!responseText && process.env.HUGGINGFACE_API_KEY) {
      try {
        console.log('[Aurora Chat] 🤗 Using Hugging Face AI fallback...');

        const hfResponse = await fetch('https://router.huggingface.co/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: 'meta-llama/Meta-Llama-3-8B-Instruct',
            messages: [
              { role: 'system', content: AURORA_SYSTEM_PROMPT },
              ...history.map(msg => ({
                role: msg.role === 'user' ? 'user' : 'assistant',
                content: msg.content
              }))
            ],
            max_tokens: 500,
            temperature: 0.7
          })
        });

        if (hfResponse.ok) {
          const data = await hfResponse.json();
          responseText = data.choices[0].message.content;
          console.log('[Aurora Chat] 🤗 Hugging Face AI response generated successfully');
        } else {
          const errorText = await hfResponse.text();
          console.error('[Aurora Chat] Hugging Face API error:', hfResponse.status, errorText);
          throw new Error(`HF API error: ${hfResponse.status}`);
        }
      } catch (error: any) {
        console.error('[Aurora Chat] Hugging Face AI error:', error.message);
        responseText = getFallbackResponse(message, history);
      }
    } else if (!responseText) {
      // Final fallback
      responseText = getFallbackResponse(message, history);
    }

    // Add Aurora's response to history
    history.push({
      role: 'assistant',
      content: responseText
    });

    // Trim history AFTER both messages are added to maintain proper user/assistant pairing
    const maxMessages = MAX_CONVERSATION_TURNS * 2;
    if (history.length > maxMessages) {
      // Calculate how many pairs (user+assistant) to remove
      const messagesToRemove = history.length - maxMessages;
      const pairsToRemove = Math.ceil(messagesToRemove / 2); // Round up to ensure we stay under limit
      const actualMessagesToRemove = pairsToRemove * 2; // Always remove in pairs

      history.splice(0, actualMessagesToRemove);
    }

    // Safety check: Ensure history always starts with a user message
    if (history.length > 0 && history[0].role !== 'user') {
      console.warn('[Aurora Chat] ⚠️  History started with assistant message, removing it');
      history.shift(); // Remove the orphaned assistant message
    }

    return {
      response: responseText,
      ok: true
    };

  } catch (error: any) {
    console.error('[Aurora Chat] Unexpected error:', error.message);

    // Final fallback if everything fails
    return {
      response: "Sorry, I encountered an unexpected error. Please try again!",
      ok: false
    };
  }
}

/**
 * Fallback conversational responses when Claude AI is not available
 */
function getFallbackResponse(message: string, history: Array<{role: string, content: string}>): string {
  const msg = message.toLowerCase().trim();

  // System status check
  if (msg.includes('how') && (msg.includes('going') || msg.includes('everything') || msg.includes('status'))) {
    return "Everything's running great! Both workflows are active, all services are healthy, and the system is performing well. I'm currently using a lightweight mode since no AI API key is configured, but I can still help with basic queries. What are you working on?";
  }

  // Greetings
  if (/^(hi|hello|hey|sup|yo)\b/.test(msg)) {
    const greetings = [
      "Hey! Good to see you. How can I help today?",
      "Hi there! What are you working on?",
      "Hello! Ready to help with whatever you need.",
      "Hey! What can I do for you?"
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  // Questions about capabilities
  if (msg.includes('what can you') || msg.includes('what do you') || msg.includes('help')) {
    return "I can help with all kinds of development tasks - coding, debugging, architecture questions, explaining concepts, reviewing code, or just chatting about tech! I'm running in lightweight mode right now (add a HuggingFace API key for enhanced AI), but I can still answer questions and help out. What do you need?";
  }

  // Questions about identity  
  if (msg.includes('who are you') || msg.includes('what are you')) {
    return "I'm Aurora, the AI assistant for the Aurora-X development platform. Think of me as your dev partner - I can help with code, answer questions, debug issues, and chat about technical stuff. Currently running in fallback mode, but still happy to help!";
  }

  // Questions about system/tech
  if (msg.includes('system') || msg.includes('how') && msg.includes('work')) {
    return "The Aurora-X platform is running smoothly - we've got a React + TypeScript frontend, Node.js + Python backend, and multiple AI capabilities. Right now I'm using fallback responses, but I can still help with questions. What would you like to know?";
  }

  // Thanks
  if (msg.includes('thank') || msg.includes('appreciate')) {
    return "You're welcome! Happy to help anytime. 😊";
  }

  // Default conversational response
  const responses = [
    "I'm here to help! Could you tell me more about what you need?",
    "Interesting question! I'm currently in lightweight mode, but I'll do my best to help. What specifically are you working on?",
    "I'm listening! What would you like to know or work on?",
    "Sure, I can help with that. Can you give me a bit more detail about what you're looking for?"
  ];

  return responses[Math.floor(Math.random() * responses.length)];
}

/**
 * Simple web search for real-time information
 */
export async function searchWeb(query: string): Promise<string> {
  try {
    const searchUrl = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1`;
    const response = await fetch(searchUrl);
    const data = await response.json();

    if (data.AbstractText) {
      return `Search result for "${query}":\n${data.AbstractText}`;
    }

    return '';
  } catch (error) {
    console.error('[Web Search] Error:', error);
    return '';
  }
}

// Placeholder for route registration function, assuming it exists elsewhere
// This is a common pattern in Express.js applications.
// If this function is meant to be defined here, it would need to be implemented.
// For now, we'll assume it's defined in another file and imported.
// If this is the file where routes are registered, the definition should be here.
export function registerAuroraChatRoutes(app: Express) {
  // Health check for Aurora AI Core
  app.get("/api/aurora/health", (req, res) => {
    res.json({ 
      ok: true, 
      status: "Aurora AI Core Online",
      timestamp: new Date().toISOString() 
    });
  });

  // Aurora chat endpoint
  app.post("/api/aurora/chat", async (req, res) => {
    const { message, sessionId } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    // Retrieve conversation history for the session
    let conversationHistory = conversationMemory.get(sessionId) || [];

    // Add user message to history (temporarily for this request)
    const tempHistory = [...conversationHistory, { role: 'user', content: message }];

    let aiResponse: string = '';
    let ok = false;

    // Try Claude AI first
    try {
      if (anthropic) {
        const completion = await anthropic.messages.create({
          model: DEFAULT_MODEL_STR,
          max_tokens: 2048,
          system: AURORA_SYSTEM_PROMPT,
          messages: tempHistory.map(msg => ({
            role: msg.role === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        });

        if (completion.content && completion.content.length > 0 && completion.content[0].type === 'text') {
          aiResponse = completion.content[0].text;
          console.log('[Aurora Chat] ✨ Claude AI response generated successfully');
          ok = true;
        } else {
          console.error('[Aurora Chat] Claude API returned empty or invalid content.');
          aiResponse = 'I apologize, I had trouble generating a response.';
        }
      } else {
        console.log('[Aurora Chat] Claude AI client not initialized, falling back to Hugging Face.');
      }
    } catch (error: any) {
      console.error('[Aurora Chat] Claude API error:', error.message);
      if (!process.env.HUGGINGFACE_API_KEY) {
        aiResponse = "I'm having trouble connecting to my AI core right now. Please add an API key for an alternative service like Hugging Face!";
      }
      // If Claude fails, the code will proceed to try Hugging Face
    }

    // Try Hugging Face if Claude failed or wasn't available and we haven't gotten a response
    if (!ok && process.env.HUGGINGFACE_API_KEY) {
      try {
        console.log('[Aurora Chat] 🤗 Using Hugging Face AI fallback...');
        const hfResponse = await fetch('https://router.huggingface.co/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: 'meta-llama/Meta-Llama-3-8B-Instruct',
            messages: [
              { role: 'system', content: AURORA_SYSTEM_PROMPT },
              ...tempHistory.map(msg => ({
                role: msg.role === 'user' ? 'user' : 'assistant',
                content: msg.content
              }))
            ],
            max_tokens: 500,
            temperature: 0.7
          })
        });

        if (hfResponse.ok) {
          const data = await hfResponse.json();
          aiResponse = data.choices[0].message.content;
          console.log('[Aurora Chat] 🤗 Hugging Face AI response generated successfully');
          ok = true;
        } else {
          const errorText = await hfResponse.text();
          console.error('[Aurora Chat] Hugging Face API error:', hfResponse.status, errorText);
          aiResponse = getFallbackResponse(message, tempHistory); // Use fallback
        }
      } catch (error: any) {
        console.error('[Aurora Chat] Hugging Face AI fetch error:', error.message);
        aiResponse = getFallbackResponse(message, tempHistory); // Use fallback
      }
    } else if (!ok && !process.env.HUGGINGFACE_API_KEY && !anthropic) {
        // If no AI services are available, use the simple fallback
        aiResponse = getFallbackResponse(message, tempHistory);
        ok = true; // Consider fallback as a successful response
    }

    // If after all attempts, we still don't have a response, use the ultimate fallback
    if (!ok) {
        aiResponse = getFallbackResponse(message, tempHistory);
        ok = true; // Fallback is considered a successful response for the endpoint
    }

    // Update persistent conversation memory
    if (!conversationMemory.has(sessionId)) {
      conversationMemory.set(sessionId, []);
    }
    const currentHistory = conversationMemory.get(sessionId)!;
    currentHistory.push({ role: 'user', content: message });
    currentHistory.push({ role: 'assistant', content: aiResponse });

    // Trim history to maintain conversation length limit
    const maxMessages = MAX_CONVERSATION_TURNS * 2;
    if (currentHistory.length > maxMessages) {
      currentHistory.splice(0, currentHistory.length - maxMessages);
    }

    // Return the response to the frontend
    res.json({
      response: aiResponse,
      ok: ok,
      session_id: sessionId // Include session_id in response if needed by frontend
    });
  });
}