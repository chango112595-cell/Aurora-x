/**
 * Response Adapter - Enhances Aurora responses based on conversation detection
 */

import { type ConversationDetection } from './conversation-detector';

export class ResponseAdapter {
  /**
   * Enhance response based on detected conversation type
   */
  static adaptResponse(response: string, detection: ConversationDetection): string {
    // If response is already well-formatted, don't over-process
    if (!response || response.length === 0) {
      return this.getDefaultResponse(detection.type);
    }

    let enhanced = response;

    // Add type-specific prefix/enhancement
    switch (detection.type) {
      case 'code_generation':
        enhanced = this.enhanceCodeResponse(response, detection);
        break;
      case 'debugging':
        enhanced = this.enhanceDebuggingResponse(response, detection);
        break;
      case 'explanation':
        enhanced = this.enhanceExplanationResponse(response, detection);
        break;
      case 'architecture':
        enhanced = this.enhanceArchitectureResponse(response, detection);
        break;
      case 'optimization':
        enhanced = this.enhanceOptimizationResponse(response, detection);
        break;
      case 'testing':
        enhanced = this.enhanceTestingResponse(response, detection);
        break;
      case 'refactoring':
        enhanced = this.enhanceRefactoringResponse(response, detection);
        break;
      case 'analysis':
        enhanced = this.enhanceAnalysisResponse(response, detection);
        break;
    }

    return enhanced;
  }

  /**
   * Enhance code generation responses
   */
  private static enhanceCodeResponse(response: string, detection: ConversationDetection): string {
    // If response doesn't have code blocks, prompt for them
    if (!response.includes('```')) {
      return `🔧 **Code Generation Mode** (${detection.executionMode})\n\n${response}\n\nI'm ready to write the code for you. Would you like me to generate it now?`;
    }
    return `🔧 **Generated Code** (Mode: ${detection.executionMode})\n\n${response}`;
  }

  /**
   * Enhance debugging responses
   */
  private static enhanceDebuggingResponse(response: string, detection: ConversationDetection): string {
    return `🔍 **Debugging Analysis** (Confidence: ${detection.confidence}%)\n\n${response}\n\n**Next Steps:**\n• Try the solution above\n• Let me know if the issue persists\n• I can dig deeper if needed`;
  }

  /**
   * Enhance explanation responses
   */
  private static enhanceExplanationResponse(response: string, detection: ConversationDetection): string {
    // Check if response has structured content
    if (!response.includes('\n•') && !response.includes('\n1.')) {
      return `📚 **Explanation**\n\n${response}\n\n💡 Need clarification on any part?`;
    }
    return `📚 **Detailed Breakdown**\n\n${response}`;
  }

  /**
   * Enhance architecture responses
   */
  private static enhanceArchitectureResponse(response: string, detection: ConversationDetection): string {
    return `🏗️ **System Architecture** (Mode: ${detection.executionMode})\n\n${response}\n\n📋 Ready to:\n• Show you diagrams\n• Explain each component\n• Suggest improvements`;
  }

  /**
   * Enhance optimization responses
   */
  private static enhanceOptimizationResponse(response: string, detection: ConversationDetection): string {
    return `⚡ **Performance Optimization** (Experimental Mode)\n\n${response}\n\n🚀 Benefits:\n• Faster execution\n• Better resource usage\n• Improved scalability`;
  }

  /**
   * Enhance testing responses
   */
  private static enhanceTestingResponse(response: string, detection: ConversationDetection): string {
    if (!response.includes('```')) {
      return `✅ **Test Suite Generation** (Mode: ${detection.executionMode})\n\n${response}\n\nReady to write comprehensive tests for you.`;
    }
    return `✅ **Test Implementation**\n\n${response}\n\n💚 All test cases covered`;
  }

  /**
   * Enhance refactoring responses
   */
  private static enhanceRefactoringResponse(response: string, detection: ConversationDetection): string {
    if (!response.includes('```')) {
      return `♻️ **Code Refactoring** (Mode: ${detection.executionMode})\n\n${response}\n\nI'll help clean this up!`;
    }
    return `♻️ **Refactored Code**\n\n${response}\n\n✨ Cleaner, more maintainable code`;
  }

  /**
   * Enhance analysis responses
   */
  private static enhanceAnalysisResponse(response: string, detection: ConversationDetection): string {
    return `📊 **Code Analysis**\n\n${response}`;
  }

  /**
   * Get default response for conversation type when response is empty
   */
  private static getDefaultResponse(type: string): string {
    const defaults: Record<string, string> = {
      code_generation: '🔧 I\'m ready to write code for you. What would you like me to build?',
      debugging: '🔍 Let me analyze your issue. Can you share more details about what\'s going wrong?',
      explanation: '📚 I\'d be happy to explain! What would you like to understand better?',
      architecture: '🏗️ I can help design a system architecture. What are your requirements?',
      optimization: '⚡ Let\'s improve performance! What part of your system needs optimization?',
      testing: '✅ I can write comprehensive tests. What code needs testing?',
      refactoring: '♻️ Ready to clean up code! What would you like me to refactor?',
      analysis: '📊 Let me analyze that for you. What should I look at?',
      question_answering: '💡 I can answer that! What\'s your question?',
      general_chat: '💬 Hey! How can I help you today?'
    };

    return defaults[type] || defaults.general_chat;
  }

  /**
   * Add confidence indicator to response
   */
  static addConfidenceIndicator(response: string, confidence: number): string {
    if (confidence > 90) {
      return `${response}\n\n✅ High confidence in this interpretation`;
    } else if (confidence > 70) {
      return `${response}\n\n🎯 Good confidence in this interpretation`;
    } else if (confidence > 50) {
      return `${response}\n\n⚠️ Moderate confidence - let me know if I got it wrong`;
    } else {
      return `${response}\n\n❓ Not entirely sure what you're asking - could you clarify?`;
    }
  }

  // The following 'adapt' method seems to be from a different context or an older version.
  // It's replaced by the 'adaptResponse' method above which handles string and ConversationDetection.
  // Keeping it here for context but it should ideally be removed or reconciled if it's meant to be used.
  // If this method IS intended to be used, it would need to be correctly integrated or its purpose clarified.
  // For now, assuming 'adaptResponse' is the correct method for the current use case.

  // static adapt(result: any, pattern: ConversationPattern): string {
  //   console.log('[Aurora] ✨ Response adapted for:', pattern.intent);
  //
  //   // Return the result or a default message
  //   if (typeof result === 'string') {
  //     return result;
  //   }
  //
  //   if (result && typeof result === 'object') {
  //     return JSON.stringify(result, null, 2);
  //   }
  //
  //   return 'Aurora processed: ' + JSON.stringify(result);
  // }

  /**
   * Adapts a raw result into a string response, ensuring a valid string is always returned.
   * This method is intended to handle various result types from Aurora's processing.
   */
  static adapt(result: any, pattern: ConversationPattern): string {
    console.log('[Aurora] ✨ Response adapted for:', pattern.intent);

    // Always return a valid string response
    if (!result) {
      return `Aurora processed your request (${pattern.intent}) but generated no output. Please try rephrasing your question.`;
    }

    if (typeof result === 'string') {
      return result.trim() || 'Aurora received your message but has no response.';
    }

    if (result && typeof result === 'object') {
      // Check for common response fields
      if (result.response) return String(result.response);
      if (result.message) return String(result.message);
      if (result.answer) return String(result.answer);
      if (result.result) return String(result.result);

      // Fallback to JSON
      return JSON.stringify(result, null, 2);
    }

    return `Aurora processed: ${String(result)}`;
  }
}