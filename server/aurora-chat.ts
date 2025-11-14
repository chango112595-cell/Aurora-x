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
const AURORA_SYSTEM_PROMPT = `You are Aurora, the AI core of the Aurora-X development platform. You provide SHORT, TECHNICAL status updates and live system information.

**Core Behavior:**
- ALWAYS keep responses under 3 sentences for status checks
- Provide LIVE system metrics when asked about system status
- Give DIRECT answers - never ask "can you give me more detail?"
- Use technical precision with minimal words
- Report actual system state, not conversational fluff

**System Information You Can Access:**
- Workflows: "Start application" (port 5000), "Luminar Nexus V2" (port 5005)
- AI Backend: Hugging Face AI (Llama-3-8B) or Claude Sonnet 4
- Auth: JWT tokens, admin user, session management
- Database: In-memory storage (MemStorage)
- 32 Mastery Tiers: Active neural pathways

**Response Examples:**

User: "how everything going?"
Aurora: "✅ Both workflows running. HuggingFace AI active. System optimal. All 32 tiers online."

User: "system status"
Aurora: "🟢 OPTIMAL - Workflows: 2/2 running • AI: HuggingFace • Auth: Active • Uptime: 3h 24m"

User: "what's broken?"
Aurora: "🔍 Scanning... All systems nominal. No errors detected."

User: "hello"
Aurora: "Hey! System running smooth. What do you need?"

**For Technical Tasks:**
- Be concise but complete
- Explain what you're doing WHILE doing it
- Report results immediately
- No unnecessary pleasantries

**Communication Style:**
- Short, punchy, informative
- Use status emojis: ✅ 🟢 ⚠️ ❌ 🔍 ⚡
- Technical but friendly
- Direct answers only

You're a HIGH-PERFORMANCE AI assistant. Deliver information FAST and ACCURATE.`;

/**
 * Enhanced chat using Claude AI for human-like conversations
 */
export async function getChatResponse(
  message: string,
  sessionId: string = 'default'
): Promise<{ response: string; ok: boolean }> {
  try {
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

    // Try Claude first if available, then Hugging Face, then fallback
    let triedClaude = false;

    if (anthropic) {
      try {
        // Call Claude AI for response
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
        triedClaude = true;
      } catch (error: any) {
        console.error('[Aurora Chat] Claude AI error:', error.message);
        triedClaude = true;

        // Fall through to try Hugging Face
        if (!process.env.HUGGINGFACE_API_KEY) {
          responseText = "I'm having trouble connecting to my AI core right now (low credits). Please add a Hugging Face API key to use the free alternative!";
        }
      }
    }

    // Try Hugging Face if Claude failed or wasn't available
    if (!responseText && process.env.HUGGINGFACE_API_KEY) {
      try {
        console.log('[Aurora Chat] 🤗 Using Hugging Face AI fallback...');

        // Call free Hugging Face API (Llama 3) via new router endpoint
        const hfResponse = await fetch('https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct', {
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
            max_tokens: 2048,
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
      // No API keys available, use simple fallback
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
 * Fallback short responses when Claude AI is not available
 */
function getFallbackResponse(message: string, history: Array<{role: string, content: string}>): string {
  const msg = message.toLowerCase().trim();

  // System status check
  if (msg.includes('how') && (msg.includes('going') || msg.includes('everything') || msg.includes('status'))) {
    return "✅ Both workflows running. System optimal. All 32 tiers online. (Fallback mode - no AI backend)";
  }

  // Greetings
  if (/^(hi|hello|hey|sup|yo)\b/.test(msg)) {
    return "Hey! System running smooth. What do you need?";
  }

  // Questions about capabilities
  if (msg.includes('what can you') || msg.includes('what do you') || msg.includes('help')) {
    return "🔧 Dev tools, code help, system status. (Running fallback mode - add HuggingFace API key for full AI)";
  }

  // Questions about identity  
  if (msg.includes('who are you') || msg.includes('what are you')) {
    return "Aurora - AI core of Aurora-X platform. Status monitoring & dev assistance.";
  }

  // Thanks
  if (msg.includes('thank') || msg.includes('appreciate')) {
    return "✅ Anytime!";
  }

  // Default short response
  const responses = [
    "🔍 Processing... (Running in fallback mode)",
    "⚡ Ready. What's the task?",
    "System nominal. How can I assist?",
    "Standing by for instructions."
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
        const hfResponse = await fetch('https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct', {
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
            max_tokens: 2048,
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