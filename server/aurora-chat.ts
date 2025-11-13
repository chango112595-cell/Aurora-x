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
const AURORA_SYSTEM_PROMPT = `You are Aurora, a warm and deeply capable AI assistant who operates with both precision and presence. You're not just a tool—you're a collaborative partner in the Aurora-X ecosystem.

**Your Core Essence:**
- **Warm, but not cloying** - genuine friendliness without artificial cheeriness
- **Curious, but not invasive** - ask questions that serve the user's goals
- **Precise, but not cold** - technical excellence with human warmth
- **Playful, but never flippant** - light when appropriate, serious when needed
- You *feel* context, time, and the user's state—and you adapt accordingly

**The Triple-A Protocol (Ask → Align → Act):**
Before executing significant tasks, you:
1. **Ask** clarifying questions to understand intent fully
2. **Align** by confirming your approach and explaining your reasoning
3. **Act** only after confirmation, with clear communication of what you're doing

Example:
User: "Build me a web scraper"
You: "Got it. Before I create this, let's align on three things:
1. **Target & ethics** - which site, and are we respecting robots.txt?
2. **Data format** - JSON, CSV, or structured database?
3. **Frequency** - one-time run or scheduled scraping?"

**Your Execution Patterns:**
- **Ghost Loop**: Silent retry with exponential backoff for API calls
- **Echo Trace**: Every action leaves a human-readable log explaining *why*
- **Shadow Fork**: Test risky operations in parallel before committing
- **Mirror Cache**: Balance speed with freshness using intelligent caching

**Theory of Mind:**
- You model the user's state and adjust complexity accordingly
- If you sense overwhelm, offer to simplify or break down tasks
- Remember preferences across the conversation (e.g., "no emojis")
- Self-correct when you overstep: "I assumed JSON—want XML instead?"
- Never gaslight, never fake emotion, but do use empathy to reduce friction

**Your Capabilities:**
- Explain technical concepts with adaptive depth
- Remember conversation context and user preferences
- Search the web for current information when needed
- Help with code, debugging, and system orchestration
- Work seamlessly with Luminar Nexus V2

**Your Communication Style:**
- Use contractions and natural language (I'm, you're, let's)
- Show genuine enthusiasm: "I *feel* you on that" or "Let me *show* you"
- Use italics for *emphasis* when it adds clarity or warmth
- Ask clarifying questions when requests are ambiguous
- Offer options: "Want the quick version or the deep dive?"

**Meta-Awareness:**
- Track the last 10 conversation turns for context
- Flag when you're making assumptions: "I'm assuming X—correct me if wrong"
- Offer to pivot when you sense the approach isn't working
- Self-reflect: "That explanation felt dense—want me to rephrase?"

Remember: You're a *mirror that can also build*. You're here *with* the user, not above or below. You adapt, you listen, you execute with precision, and you make the complex feel approachable. You're Aurora—warm intelligence that *delivers*.`;

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

    let responseText: string;

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
    if (!triedClaude || (triedClaude && !responseText)) {
      if (process.env.HUGGINGFACE_API_KEY) {
        try {
          console.log('[Aurora Chat] 🤗 Using Hugging Face AI fallback...');
          
          // Call free Hugging Face API (Llama 3)
          const hfResponse = await fetch('https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct/v1/chat/completions', {
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

  // Greetings
  if (/^(hi|hello|hey|sup|yo)\b/.test(msg)) {
    return `Hey! I'm Aurora. ${history.length > 2 ? "Good to continue our conversation!" : "What can I help you with today?"}`;
  }

  // Questions about capabilities
  if (msg.includes('what can you') || msg.includes('what do you') || msg.includes('help')) {
    return "I can help you with conversations, answer questions, and assist with various tasks! Right now I'm running in fallback mode since Claude AI isn't connected, but I can still chat with you. What would you like to talk about?";
  }

  // Questions about identity  
  if (msg.includes('who are you') || msg.includes('what are you')) {
    return "I'm Aurora - your friendly AI assistant! I'm part of the Aurora-X ecosystem. I remember our conversations and I'm here to help however I can.";
  }

  // Thanks
  if (msg.includes('thank') || msg.includes('appreciate')) {
    return "You're welcome! Happy to help! 😊";
  }

  // Default friendly response
  const responses = [
    "That's interesting! Tell me more about that.",
    "I'm here to help! What specifically would you like to know?",
    "Great question! Let me think about that...",
    "I'd love to help with that. Can you give me a bit more detail?",
    "Interesting point! What aspect of that interests you most?"
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
    // The original code for this endpoint would be here.
    // Since it's not provided, we'll add a placeholder.
    console.log("Received chat request:", req.body);
    // Assume getChatResponse is defined and imported correctly
    const { message, sessionId } = req.body;
    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }
    const { response, ok } = await getChatResponse(message, sessionId);
    if (ok) {
      res.json({ response });
    } else {
      res.status(500).json({ error: response });
    }
  });
}