// Progress tracking store for synthesis operations
export type SynthesisStage = 
  | "QUEUED" 
  | "ANALYZING" 
  | "GENERATING" 
  | "TESTING" 
  | "COMPLETE" 
  | "ERROR";

export interface ProgressEntry {
  id: string;
  stage: SynthesisStage;
  percentage: number;
  message: string;
  estimatedTimeRemaining: number; // seconds
  startedAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  error?: string;
  complexity?: "simple" | "medium" | "complex";
  actualDuration?: number; // seconds
}

class ProgressStore {
  private progressMap: Map<string, ProgressEntry> = new Map();
  private estimationHistory: Array<{
    complexity: string;
    actualTime: number;
    messageLength: number;
  }> = [];

  // Generate unique synthesis ID
  generateId(): string {
    return `synth-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Create new progress entry
  createProgress(id: string, complexity: "simple" | "medium" | "complex"): ProgressEntry {
    const entry: ProgressEntry = {
      id,
      stage: "QUEUED",
      percentage: 0,
      message: "Request queued for processing",
      estimatedTimeRemaining: this.getInitialEstimate(complexity),
      startedAt: new Date(),
      updatedAt: new Date(),
      complexity
    };
    this.progressMap.set(id, entry);
    return entry;
  }

  // Get initial time estimate based on complexity
  private getInitialEstimate(complexity: "simple" | "medium" | "complex"): number {
    // Check historical data for better estimates
    const relevantHistory = this.estimationHistory.filter(h => h.complexity === complexity);
    
    if (relevantHistory.length > 3) {
      const avgTime = relevantHistory.slice(-5).reduce((sum, h) => sum + h.actualTime, 0) / Math.min(relevantHistory.length, 5);
      return Math.round(avgTime);
    }

    // Default estimates
    switch (complexity) {
      case "simple": return 7; // 5-10 seconds
      case "medium": return 20; // 15-30 seconds
      case "complex": return 45; // 30-60 seconds
      default: return 15;
    }
  }

  // Update progress
  updateProgress(
    id: string, 
    stage: SynthesisStage, 
    percentage: number, 
    message: string
  ): ProgressEntry | undefined {
    const entry = this.progressMap.get(id);
    if (!entry) return undefined;

    entry.stage = stage;
    entry.percentage = percentage;
    entry.message = message;
    entry.updatedAt = new Date();

    // Calculate estimated time remaining based on progress
    const elapsedSeconds = (entry.updatedAt.getTime() - entry.startedAt.getTime()) / 1000;
    
    if (stage === "COMPLETE") {
      entry.completedAt = new Date();
      entry.estimatedTimeRemaining = 0;
      entry.actualDuration = elapsedSeconds;
      
      // Store in history for better future estimates
      if (entry.complexity) {
        this.estimationHistory.push({
          complexity: entry.complexity,
          actualTime: elapsedSeconds,
          messageLength: 0 // Could be extended to track message length
        });
        // Keep only last 100 entries
        if (this.estimationHistory.length > 100) {
          this.estimationHistory = this.estimationHistory.slice(-100);
        }
      }
    } else if (percentage > 0) {
      const estimatedTotal = elapsedSeconds / (percentage / 100);
      entry.estimatedTimeRemaining = Math.max(0, Math.round(estimatedTotal - elapsedSeconds));
    }

    return entry;
  }

  // Get progress by ID
  getProgress(id: string): ProgressEntry | undefined {
    return this.progressMap.get(id);
  }

  // Estimate complexity based on message
  estimateComplexity(message: string): "simple" | "medium" | "complex" {
    const length = message.length;
    const hasLoops = /\b(loop|iterate|for|while|repeat)\b/i.test(message);
    const hasRecursion = /\b(recursive|recursion)\b/i.test(message);
    const hasTests = /\b(test|testing|unit test|pytest)\b/i.test(message);
    const hasAdvanced = /\b(optimize|parallel|concurrent|async|database|api)\b/i.test(message);

    let complexityScore = 0;
    
    // Message length scoring
    if (length < 50) complexityScore += 0;
    else if (length < 150) complexityScore += 1;
    else complexityScore += 2;

    // Feature scoring
    if (hasLoops) complexityScore += 1;
    if (hasRecursion) complexityScore += 2;
    if (hasTests) complexityScore += 2;
    if (hasAdvanced) complexityScore += 2;

    // Determine complexity
    if (complexityScore <= 1) return "simple";
    if (complexityScore <= 4) return "medium";
    return "complex";
  }

  // Clean up old entries (older than 1 hour)
  cleanup(): void {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    const idsToDelete: string[] = [];
    
    this.progressMap.forEach((entry, id) => {
      if (entry.updatedAt < oneHourAgo && entry.stage === "COMPLETE") {
        idsToDelete.push(id);
      }
    });

    idsToDelete.forEach(id => this.progressMap.delete(id));
  }

  // Get estimation statistics
  getEstimationStats(): any {
    const stats: any = {
      simple: { count: 0, avgTime: 0 },
      medium: { count: 0, avgTime: 0 },
      complex: { count: 0, avgTime: 0 }
    };

    this.estimationHistory.forEach(h => {
      if (stats[h.complexity]) {
        stats[h.complexity].count++;
        stats[h.complexity].avgTime += h.actualTime;
      }
    });

    Object.keys(stats).forEach(key => {
      if (stats[key].count > 0) {
        stats[key].avgTime = Math.round(stats[key].avgTime / stats[key].count);
      }
    });

    return stats;
  }
}

// Export singleton instance
export const progressStore = new ProgressStore();