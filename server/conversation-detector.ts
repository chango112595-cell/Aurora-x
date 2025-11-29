/**
 * Aurora Conversation Auto-Detector
 * Intelligently classifies conversations and adapts execution strategy
 */

export type ConversationType = 
  | 'code_generation'
  | 'debugging'
  | 'explanation'
  | 'architecture'
  | 'optimization'
  | 'testing'
  | 'general_chat'
  | 'question_answering'
  | 'analysis'
  | 'refactoring';

export interface ConversationDetection {
  type: ConversationType;
  confidence: number;
  keywords: string[];
  executionMode: 'fast' | 'detailed' | 'experimental' | 'standard';
  suggestedFormat: 'code' | 'explanation' | 'bullet_points' | 'step_by_step' | 'mixed';
  shouldExecute: boolean;
  tone: 'technical' | 'casual' | 'formal' | 'debugging';
  generateContextPrefix?: () => string;
  generateFormatInstructions?: () => string;
}

export class ConversationDetector {
  private readonly conversationHistory: string[] = [];
  private contextWindow: number = 5;

  /**
   * Analyze user message and detect conversation type
   */
  detect(userMessage: string, previousMessages: string[] = []): ConversationDetection {
    const allMessages = [...previousMessages, userMessage];
    const context = allMessages.slice(-this.contextWindow).join(' ');
    const messageUpper = userMessage.toUpperCase();

    // Keyword sets for classification - prioritize specific keywords
    const codeGenKeywords = ['write', 'create', 'generate', 'build', 'implement', 'code', 'app', 'script', 'module', 'library', 'method', 'routine', 'function', 'class', 'algorithm', 'api', 'component', 'program', 'service', 'endpoint', 'handler'];
    const debugKeywords = ['bug', 'error', 'fix', 'crash', 'problem', 'issue', 'fail', 'broken', 'exception', 'null pointer', 'undefined', 'doesn\'t work', 'can\'t', 'throw', 'debug', 'debugging', 'troubleshoot'];
    const explainKeywords = ['explain', 'how does', 'what is', 'describe', 'tell me', 'teach', 'understand', 'learning', 'learn', 'works', 'tutorial', 'how it', 'what does'];
    const archKeywords = ['architecture', 'design', 'structure', 'pattern', 'system', 'schema', 'layer', 'component', 'diagram', 'database schema'];
    const optimizeKeywords = ['optimize', 'faster', 'performance', 'improve', 'speed', 'efficient', 'scale', 'reduce', 'accelerate'];
    const testKeywords = ['test', 'unit test', 'integration', 'jest', 'mocha', 'coverage', 'validate', 'verify', 'assert'];
    const refactorKeywords = ['refactor', 'clean up', 'reorganize', 'simplify', 'rewrite', 'cleanup'];
    const analysisKeywords = ['analyze', 'review', 'examine', 'compare', 'evaluate', 'assess', 'audit', 'inspection', 'analyze', 'diagnose', 'diagnostic', 'self diagnose', 'self-diagnose', 'check', 'scan', 'health check'];

    let detectedType: ConversationType = 'general_chat';
    let maxScore = 0;
    const scores: Record<ConversationType, number> = {
      code_generation: 0,
      debugging: 0,
      explanation: 0,
      architecture: 0,
      optimization: 0,
      testing: 0,
      refactoring: 0,
      analysis: 0,
      question_answering: 0,
      general_chat: 1
    };

    // Calculate keyword match scores with boost multipliers
    scores.code_generation = this.calculateKeywordScore(messageUpper, codeGenKeywords) * 2.3;
    scores.debugging = this.calculateKeywordScore(messageUpper, debugKeywords) * 2.5; // Boost debugging
    scores.explanation = this.calculateKeywordScore(messageUpper, explainKeywords) * 2.0; // Boost explanation
    scores.architecture = this.calculateKeywordScore(messageUpper, archKeywords) * 2.0; // Boost architecture
    scores.optimization = this.calculateKeywordScore(messageUpper, optimizeKeywords) * 2.0; // Boost optimization
    scores.testing = this.calculateKeywordScore(messageUpper, testKeywords) * 2.2; // Boost testing
    scores.refactoring = this.calculateKeywordScore(messageUpper, refactorKeywords) * 2.0; // Boost refactoring
    scores.analysis = this.calculateKeywordScore(messageUpper, analysisKeywords) * 2.0; // Boost analysis

    // Question detection
    if (messageUpper.includes('?')) {
      scores.question_answering += 15;
    }

    // Code block patterns
    if (userMessage.includes('```')) {
      scores.code_generation += 15;
    }

    // Strong code generation patterns - boost significantly
    if (messageUpper.includes('FUNCTION') || messageUpper.includes('CLASS')) {
      scores.code_generation += 25;
    }
    if (messageUpper.includes('ALGORITHM')) {
      scores.code_generation += 20;
    }
    if (messageUpper.includes('API') || messageUpper.includes('ENDPOINT')) {
      scores.code_generation += 20;
    }
    if (messageUpper.includes('COMPONENT') || messageUpper.includes('MODULE')) {
      scores.code_generation += 15;
    }

    // De-prioritize question_answering when code context is strong
    if (scores.code_generation > 15) {
      scores.question_answering = Math.max(0, scores.question_answering - 10);
    }

    // Error stack traces detection - strong debugging signal
    if (userMessage.includes('Error') || userMessage.includes('Exception') || userMessage.includes('Traceback') || messageUpper.includes('THROW')) {
      scores.debugging += 30;
    }

    // Testing patterns
    if (messageUpper.includes('TEST') && messageUpper.includes('WRITE')) {
      scores.testing += 20;
    }

    // Refactoring patterns
    if (messageUpper.includes('CLEAN') || messageUpper.includes('SIMPLIF')) {
      scores.refactoring += 20;
    }

    // Optimization patterns
    if (messageUpper.includes('FAST') || messageUpper.includes('SLOW')) {
      scores.optimization += 15;
    }

    // Explanation patterns
    if (messageUpper.includes('HOW') || messageUpper.includes('WHAT')) {
      scores.explanation += 10;
    }

    // Architecture patterns
    if (messageUpper.includes('SCHEMA') || messageUpper.includes('STRUCTURE')) {
      scores.architecture += 20;
    }

    // Analysis patterns
    if (messageUpper.includes('ANALYZE') || messageUpper.includes('REVIEW')) {
      scores.analysis += 25;
    }

    // Context-based adjustment
    if (previousMessages.length > 0) {
      const recentContext = allMessages.slice(-2).join(' ').toUpperCase();
      if (recentContext.includes('ERROR') || recentContext.includes('ISSUE')) {
        scores.debugging += 10;
      }
    }

    // Find highest scoring type
    let keywords: string[] = [];
    for (const [type, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        detectedType = type as ConversationType;
      }
    }

    // Extract relevant keywords for this type
    switch (detectedType) {
      case 'code_generation':
        keywords = this.extractKeywords(messageUpper, codeGenKeywords);
        break;
      case 'debugging':
        keywords = this.extractKeywords(messageUpper, debugKeywords);
        break;
      case 'explanation':
        keywords = this.extractKeywords(messageUpper, explainKeywords);
        break;
      case 'architecture':
        keywords = this.extractKeywords(messageUpper, archKeywords);
        break;
      case 'optimization':
        keywords = this.extractKeywords(messageUpper, optimizeKeywords);
        break;
      case 'testing':
        keywords = this.extractKeywords(messageUpper, testKeywords);
        break;
      case 'refactoring':
        keywords = this.extractKeywords(messageUpper, refactorKeywords);
        break;
      case 'analysis':
        keywords = this.extractKeywords(messageUpper, analysisKeywords);
        break;
      default:
        keywords = [];
    }

    // Determine execution strategy
    const executionMode = this.determineExecutionMode(detectedType, userMessage);
    const suggestedFormat = this.determineSuggestedFormat(detectedType);
    const shouldExecute = this.shouldExecuteCode(detectedType, userMessage);
    const tone = this.detectTone(messageUpper);

    // Calculate confidence (0-100)
    const confidence = Math.min(100, maxScore * 20);

    return {
      type: detectedType,
      confidence,
      keywords,
      executionMode,
      suggestedFormat,
      shouldExecute,
      tone
    };
  }

  /**
   * Calculate keyword match score
   */
  private calculateKeywordScore(message: string, keywords: string[]): number {
    let score = 0;
    keywords.forEach(keyword => {
      if (message.includes(keyword)) {
        score += 5;
      }
    });
    return score;
  }

  /**
   * Extract relevant keywords from message
   */
  private extractKeywords(message: string, possibleKeywords: string[]): string[] {
    return possibleKeywords.filter(keyword => message.includes(keyword));
  }

  /**
   * Determine execution mode based on conversation type
   */
  private determineExecutionMode(type: ConversationType, message: string): 'fast' | 'detailed' | 'experimental' | 'standard' {
    switch (type) {
      case 'debugging':
        return 'detailed'; // Thorough debugging
      case 'optimization':
        return 'experimental'; // Try different approaches
      case 'code_generation':
        return 'fast'; // Quick generation
      case 'explanation':
        return 'standard';
      case 'architecture':
        return 'detailed';
      default:
        return 'standard';
    }
  }

  /**
   * Determine suggested response format
   */
  private determineSuggestedFormat(type: ConversationType): 'code' | 'explanation' | 'bullet_points' | 'step_by_step' | 'mixed' {
    switch (type) {
      case 'code_generation':
        return 'code';
      case 'debugging':
        return 'step_by_step';
      case 'explanation':
        return 'mixed';
      case 'architecture':
        return 'step_by_step';
      case 'optimization':
        return 'mixed';
      case 'testing':
        return 'code';
      case 'refactoring':
        return 'code';
      case 'analysis':
        return 'bullet_points';
      default:
        return 'mixed';
    }
  }

  /**
   * Determine if code should be executed
   */
  private shouldExecuteCode(type: ConversationType, message: string): boolean {
    const hasCodeBlock = message.includes('```');
    const executeTypes = ['code_generation', 'testing', 'debugging'];
    return executeTypes.includes(type) || hasCodeBlock;
  }

  /**
   * Detect tone of conversation
   */
  private detectTone(message: string): 'technical' | 'casual' | 'formal' | 'debugging' {
    if (message.includes('ERROR') || message.includes('BUG') || message.includes('FIX')) {
      return 'debugging';
    }
    if (message.includes('FORMAL') || message.includes('PLEASE') || message.includes('KINDLY')) {
      return 'formal';
    }
    if (message.includes('???') || message.includes('LOL') || message.includes('COOL')) {
      return 'casual';
    }
    return 'technical';
  }

  /**
   * Add message to history for context
   */
  addMessageToHistory(message: string): void {
    this.conversationHistory.push(message);
    if (this.conversationHistory.length > this.contextWindow) {
      this.conversationHistory.shift();
    }
  }

  /**
   * Get conversation history
   */
  getHistory(): string[] {
    return this.conversationHistory;
  }

  /**
   * Generate context-aware response prefix based on detection
   */
  generateContextPrefix(detection: ConversationDetection): string {
    const mode = detection.executionMode;
    const tone = detection.tone;

    const prefixes: Record<ConversationType, string> = {
      code_generation: '🔧 Let me write this code for you:\n\n',
      debugging: '🔍 I found the issue. Here\'s what\'s happening:\n\n',
      explanation: '📚 Let me break this down for you:\n\n',
      architecture: '🏗️ Here\'s the system design:\n\n',
      optimization: '⚡ Here\'s how to improve performance:\n\n',
      testing: '✅ Here\'s a complete test suite:\n\n',
      refactoring: '♻️ Here\'s the refactored code:\n\n',
      analysis: '📊 Analysis results:\n\n',
      question_answering: '💡 Answer:\n\n',
      general_chat: '💬 '
    };

    return prefixes[detection.type] || prefixes.general_chat;
  }

  /**
   * Generate response format instructions for Aurora's backend
   */
  generateFormatInstructions(detection: ConversationDetection): string {
    const instructions: Record<'code' | 'explanation' | 'bullet_points' | 'step_by_step' | 'mixed', string> = {
      code: 'Respond with code blocks. Format: ```language\ncode here\n```',
      explanation: 'Explain clearly and concisely.',
      bullet_points: 'Use bullet points for clarity. Start with • or -',
      step_by_step: 'Break down into numbered steps. Format: 1. Step\n2. Step',
      mixed: 'Use a combination of explanation and code examples.'
    };

    return instructions[detection.suggestedFormat];
  }
}

// Export singleton instance
export const conversationDetector = new ConversationDetector();
