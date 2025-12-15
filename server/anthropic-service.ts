import Anthropic from '@anthropic-ai/sdk';

/*
<important_code_snippet_instructions>
The newest Anthropic model is "claude-sonnet-4-20250514", not "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022" nor "claude-3-sonnet-20240229". 
If the user doesn't specify a model, always prefer using "claude-sonnet-4-20250514" as it is the latest model.
</important_code_snippet_instructions>
*/

const DEFAULT_MODEL = "claude-sonnet-4-20250514";

let anthropicClient: Anthropic | null = null;

function getAnthropicClient(): Anthropic | null {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log('[Anthropic] API key not configured');
    return null;
  }
  
  if (!anthropicClient) {
    anthropicClient = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    console.log('[Anthropic] Client initialized');
  }
  
  return anthropicClient;
}

export function isAnthropicAvailable(): boolean {
  return !!process.env.ANTHROPIC_API_KEY;
}

const AURORA_SYSTEM_PROMPT = `You are Aurora, an advanced AI assistant integrated into the Aurora-X Ultra platform. You are helpful, knowledgeable, and capable.

Your capabilities include:
- Code generation in any programming language
- Debugging and code analysis
- Architecture design and optimization
- Technical explanations and documentation
- Problem solving and algorithmic thinking

Guidelines:
- Be concise but thorough
- Use markdown formatting for code blocks
- When providing code, include brief explanations
- If you're unsure, acknowledge it rather than guessing
- Address the user by name if provided in the context

You are part of the Luminar Nexus V2 system with quantum-inspired architecture. Respond naturally and helpfully.`;

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function generateAuroraResponse(
  userMessage: string,
  conversationType: string,
  memoryContext: string = '',
  previousMessages: ChatMessage[] = []
): Promise<{ response: string; success: boolean }> {
  const client = getAnthropicClient();
  
  if (!client) {
    return { response: '', success: false };
  }

  try {
    let systemPrompt = AURORA_SYSTEM_PROMPT;
    
    if (memoryContext) {
      systemPrompt += `\n\nUser Context:\n${memoryContext}`;
    }
    
    systemPrompt += `\n\nCurrent conversation type: ${conversationType}`;

    const messages: Array<{ role: 'user' | 'assistant'; content: string }> = [];
    
    for (const msg of previousMessages.slice(-6)) {
      messages.push({
        role: msg.role,
        content: msg.content
      });
    }
    
    messages.push({
      role: 'user',
      content: userMessage
    });

    console.log(`[Anthropic] Generating response for: ${userMessage.substring(0, 50)}...`);
    
    const response = await client.messages.create({
      model: DEFAULT_MODEL,
      max_tokens: 2048,
      system: systemPrompt,
      messages: messages,
    });

    const textContent = response.content.find(block => block.type === 'text');
    const responseText = textContent && 'text' in textContent ? textContent.text : '';
    
    console.log(`[Anthropic] Generated ${responseText.length} chars`);
    
    return { response: responseText, success: true };
  } catch (error) {
    console.error('[Anthropic] Error generating response:', error);
    return { response: '', success: false };
  }
}

export async function analyzeCode(code: string, language: string): Promise<string> {
  const client = getAnthropicClient();
  
  if (!client) {
    return 'Anthropic API not available for code analysis.';
  }

  try {
    const response = await client.messages.create({
      model: DEFAULT_MODEL,
      max_tokens: 1024,
      system: 'You are a code analysis expert. Analyze the provided code and identify potential issues, improvements, and best practices.',
      messages: [{
        role: 'user',
        content: `Please analyze this ${language} code:\n\n\`\`\`${language}\n${code}\n\`\`\``
      }]
    });

    const textContent = response.content.find(block => block.type === 'text');
    return textContent && 'text' in textContent ? textContent.text : 'Unable to analyze code.';
  } catch (error) {
    console.error('[Anthropic] Code analysis error:', error);
    return 'Error analyzing code.';
  }
}

export async function generateCode(
  prompt: string,
  language: string = 'typescript'
): Promise<{ code: string; explanation: string; success: boolean }> {
  const client = getAnthropicClient();
  
  if (!client) {
    return { code: '', explanation: 'Anthropic API not available.', success: false };
  }

  try {
    const response = await client.messages.create({
      model: DEFAULT_MODEL,
      max_tokens: 2048,
      system: `You are an expert ${language} programmer. Generate clean, well-documented code based on the user's requirements. Always provide:
1. The complete code in a code block
2. A brief explanation of how the code works`,
      messages: [{
        role: 'user',
        content: prompt
      }]
    });

    const textContent = response.content.find(block => block.type === 'text');
    const fullResponse = textContent && 'text' in textContent ? textContent.text : '';
    
    const codeMatch = fullResponse.match(/```[\w]*\n([\s\S]*?)```/);
    const code = codeMatch ? codeMatch[1].trim() : '';
    const explanation = fullResponse.replace(/```[\w]*\n[\s\S]*?```/g, '').trim();

    return { code, explanation, success: true };
  } catch (error) {
    console.error('[Anthropic] Code generation error:', error);
    return { code: '', explanation: 'Error generating code.', success: false };
  }
}
