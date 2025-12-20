/**
 * External AI Guard - Controls access to external AI services (Anthropic/Claude, OpenAI, etc.)
 * 
 * This module ensures the system can work fully offline without any external AI calls.
 * When ENABLE_EXTERNAL_AI is not "true" or API keys are missing, the system gracefully
 * falls back to local-only mode with no errors.
 */

export interface ExternalAIConfig {
  enabled: boolean;
  anthropicAvailable: boolean;
  openaiAvailable: boolean;
  mode: 'external' | 'local-only' | 'hybrid';
  fallbackReason?: string;
}

export interface AIResponse {
  success: boolean;
  response: string;
  source: 'anthropic' | 'openai' | 'local' | 'fallback';
  error?: string;
}

const isExternalAIEnabled = (): boolean => {
  return process.env.ENABLE_EXTERNAL_AI === 'true';
};

const hasAnthropicKey = (): boolean => {
  return !!process.env.ANTHROPIC_API_KEY && process.env.ANTHROPIC_API_KEY.trim() !== '';
};

const hasOpenAIKey = (): boolean => {
  return !!process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY.trim() !== '';
};

export function getExternalAIConfig(): ExternalAIConfig {
  const enabled = isExternalAIEnabled();
  const anthropicAvailable = enabled && hasAnthropicKey();
  const openaiAvailable = enabled && hasOpenAIKey();
  
  let mode: 'external' | 'local-only' | 'hybrid';
  let fallbackReason: string | undefined;

  if (!enabled) {
    mode = 'local-only';
    fallbackReason = 'ENABLE_EXTERNAL_AI is not set to "true"';
  } else if (!anthropicAvailable && !openaiAvailable) {
    mode = 'local-only';
    fallbackReason = 'No external AI API keys configured';
  } else if (anthropicAvailable || openaiAvailable) {
    mode = anthropicAvailable && openaiAvailable ? 'hybrid' : 'external';
  } else {
    mode = 'local-only';
  }

  return {
    enabled,
    anthropicAvailable,
    openaiAvailable,
    mode,
    fallbackReason
  };
}

export function isAnthropicAvailable(): boolean {
  return isExternalAIEnabled() && hasAnthropicKey();
}

export function isOpenAIAvailable(): boolean {
  return isExternalAIEnabled() && hasOpenAIKey();
}

export function isAnyExternalAIAvailable(): boolean {
  return isAnthropicAvailable() || isOpenAIAvailable();
}

export function getLocalFallbackResponse(query: string): AIResponse {
  const config = getExternalAIConfig();
  
  const queryLower = query.toLowerCase();
  
  let response: string;
  
  if (queryLower.includes('hello') || queryLower.includes('hi')) {
    response = "Hello! I'm Aurora operating in local-only mode. I can help with code analysis, system queries, and development tasks using my built-in capabilities.";
  } else if (queryLower.includes('status') || queryLower.includes('health')) {
    response = `Aurora Status: Running in ${config.mode} mode. ${config.fallbackReason ? `Reason: ${config.fallbackReason}` : 'All systems operational.'}`;
  } else if (queryLower.includes('help')) {
    response = "Aurora Help (Local Mode): I can assist with code reviews, debugging, architecture analysis, and development guidance. External AI features require enabling ENABLE_EXTERNAL_AI=true and configuring API keys.";
  } else if (queryLower.includes('analyze') || queryLower.includes('review')) {
    response = "Local analysis mode active. I can perform static code analysis and pattern detection. For advanced AI-powered analysis, please configure external AI services.";
  } else {
    response = `Received: "${query.substring(0, 100)}${query.length > 100 ? '...' : ''}"\n\nAurora is running in local-only mode. To enable AI-powered responses, set ENABLE_EXTERNAL_AI=true and configure your API keys (ANTHROPIC_API_KEY or OPENAI_API_KEY).`;
  }

  return {
    success: true,
    response,
    source: 'fallback'
  };
}

export async function executeWithAIGuard(
  externalAIFunction: () => Promise<string>,
  fallbackQuery: string
): Promise<AIResponse> {
  if (!isAnyExternalAIAvailable()) {
    console.log('[External AI Guard] External AI not available, using local fallback');
    return getLocalFallbackResponse(fallbackQuery);
  }

  try {
    const response = await externalAIFunction();
    return {
      success: true,
      response,
      source: isAnthropicAvailable() ? 'anthropic' : 'openai'
    };
  } catch (error: any) {
    console.error('[External AI Guard] External AI call failed:', error.message);
    return {
      success: false,
      response: getLocalFallbackResponse(fallbackQuery).response,
      source: 'fallback',
      error: error.message
    };
  }
}

export function logAIGuardStatus(): void {
  const config = getExternalAIConfig();
  console.log('[External AI Guard] Status:', {
    mode: config.mode,
    anthropicAvailable: config.anthropicAvailable,
    openaiAvailable: config.openaiAvailable,
    fallbackReason: config.fallbackReason || 'N/A'
  });
}
