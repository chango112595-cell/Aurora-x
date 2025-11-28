# Chango - Luminar Nexus V2 Integration Game Plan
**Created**: November 28, 2025  
**Objective**: Re-enable V2 orchestrator and repurpose ML engine for conversation learning

---

## Executive Summary

**The Opportunity**: V3 has self-healing (100 workers) but it's optimized for SERVICE resilience. V2 has an AI ML engine (`AIServiceOrchestrator`) that's **wasted on just ops** — we can repurpose it for **conversation pattern learning** to improve our auto-detector from 7/8 to 10/10 type detection.

**The Approach**: 
- Enable V2 on port 5005 as a background service
- Convert V2's `AIServiceOrchestrator` into a **Conversation Pattern Learner**
- Pipe detected conversations to V2 for ML analysis
- Use learned patterns to improve future detection

**Timeline**: 3-4 turns (Phase 1: Fix detection, Phase 2: Enable V2, Phase 3: Integration)

---

## Current State

### What's Working
- ✅ V3 on port 5000 (main service, 188 power units)
- ✅ 7/8 conversation types detected correctly
- ✅ Response adaptation with type-specific prefixes
- ✅ 100-worker autofixer pool (for service resilience)
- ✅ Aurora Chat with NLP classification

### What's Missing
- ❌ `code_generation` detection (only 1 of remaining type)
  - Current multiplier: 1.8x (vs debugging 2.5x)
  - Missing keywords for modern code requests
- ❌ V2 disabled/not running (port 5005 empty)
- ❌ ML learning from conversation patterns
- ❌ Cross-service communication (V3 ↔ V2)

### The V3 100-Worker Pool Issue
- Currently active but **optimized for service repair only**
- Can't be repurposed for NLP without major V3 rewrite
- V2's `AIServiceOrchestrator` is actually **perfect for ML pattern learning**

---

## The Problem We're Solving

**Why 7/8 isn't good enough:**
```
User: "write a function to calculate fibonacci"
Expected: code_generation ✅
Actual: general_chat ❌

Why it fails:
- "write" keyword hits code_generation score (1.8x multiplier)
- "?" at end boosts question_answering (automatic +15)
- Result: question_answering wins!
```

**Why V2 matters:**
- V2 has `learn_service_patterns()` — we can adapt to `learn_conversation_patterns()`
- V2 has `detect_service_patterns()` — we can use for `detect_conversation_patterns()`
- V2 has `_analyze_metric_correlations()` — we can use for `analyze_keyword_correlations()`
- **Already has ML, just need to redirect it**

---

## Proposed Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER SENDS MESSAGE                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  ConversationDetector  │ (TypeScript)
         │  (Current: 1.8x mult) │
         └──────────┬────────────┘
                    │
      ┌─────────────┴──────────────┐
      │ (Detected Type + Keywords) │
      └─────────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────────┐
         │  V3: Response Adapter       │
         │  (Return to user)           │
         └─────────────┬───────────────┘
                       │
                       ▼
              ┌──────────────────────────┐
              │ PIPE TO V2 (Async)       │
              │ (Port 5005)              │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────────────────┐
              │  V2: ConversationPatternLearner     │
              │  ├─ learn_conversation_patterns()   │
              │  ├─ analyze_keyword_correlations()  │
              │  ├─ predict_type_confidence()       │
              │  └─ return_improved_confidence()    │
              └──────────┬───────────────────────────┘
                         │
              Store patterns (keep last 1000)
              │
              ▼
        ┌──────────────────────┐
        │ Future Requests Get  │
        │ Better Detection Via │
        │ ML Learned Patterns  │
        └──────────────────────┘
```

---

## Phase-by-Phase Implementation Roadmap

### Phase 1: Quick Detection Fix (1-2 hours)
**Goal**: Get from 7/8 to 8/8 types working

**File**: `server/conversation-detector.ts`

**Changes**:
1. Boost `code_generation` multiplier from 1.8x → 2.3x (line 68)
2. Add missing keywords to `codeGenKeywords` array (line 43):
   - Add: `'function', 'class', 'method', 'api', 'component', 'function', 'algorithm'`
3. Add pattern detection for code requests (after line 85):
   ```typescript
   // Code request patterns
   if (messageUpper.includes('FUNCTION') || messageUpper.includes('CLASS')) {
     scores.code_generation += 25;
   }
   if (messageUpper.includes('ALGORITHM')) {
     scores.code_generation += 20;
   }
   ```
4. Reduce `question_answering` boost when code keywords present:
   ```typescript
   // De-prioritize question_answering when code context is strong
   if (scores.code_generation > 15) {
     scores.question_answering = Math.max(0, scores.question_answering - 10);
   }
   ```

**Success Criteria**: 
- Test messages like "write a fibonacci function" → code_generation detected
- Test messages like "build me an API" → code_generation detected
- All 10 types now detected correctly

---

### Phase 2: Enable V2 on Port 5005 (30 minutes)
**Goal**: Start V2 as background service

**Actions**:
1. Create workflow config for V2:
   ```bash
   python3 tools/luminar_nexus_v2.py --port 5005
   ```
2. Verify V2 startup:
   ```bash
   curl http://localhost:5005/api/nexus/status
   ```
3. Update `server/index.ts`:
   - Uncomment V2 route registration (currently commented out)
   - Change comment from "V2 removed" → "V2 enabled for ML learning"

**Success Criteria**:
- V2 service running on port 5005
- Health check returns 200
- V3 can reach V2 via proxy

---

### Phase 3: Integrate V2 ML for Conversation Learning (2-3 hours)
**Goal**: V2 learns conversation patterns, feeds back to detector

**New File**: `server/conversation-pattern-adapter.ts`
```typescript
interface ConversationPattern {
  type: ConversationType;
  keywords: string[];
  confidence: number;
  timestamp: number;
  context: string;
}

export class ConversationPatternAdapter {
  async sendPatternToV2(pattern: ConversationPattern): Promise<void>
  async getLearnedPatterns(type: ConversationType): Promise<any>
  async adjustDetectionBased(type: ConversationType): Promise<void>
}
```

**Changes to `server/routes.ts`**:
1. After successful chat detection, pipe pattern to V2:
   ```typescript
   POST /api/chat → detect type → send to V2 async
   ```

2. Add endpoint to retrieve learned confidence scores:
   ```typescript
   GET /api/conversation/learned-patterns/:type → V2 response
   ```

**Changes to V2** (`tools/luminar_nexus_v2.py`):
1. Adapt `AIServiceOrchestrator` class:
   ```python
   def learn_conversation_patterns(self, conv_type: str, keywords: list, confidence: float)
   def analyze_keyword_correlations(self, type_a: str, type_b: str) -> dict
   def get_improved_confidence(self, type: str) -> float
   ```

2. Add POST endpoint:
   ```python
   POST /api/nexus/learn-conversation
   {
     "type": "code_generation",
     "keywords": ["function", "write"],
     "confidence": 85
   }
   ```

**Success Criteria**:
- V2 receives conversation patterns
- V2 stores last 1000 patterns per type
- Confidence scores improve with more data
- V3 can query improved scores

---

### Phase 4: Real-World Validation (1-2 hours)
**Goal**: Verify end-to-end system

**Test Cases**:
1. 10 code generation requests → All detected as `code_generation`
2. 5 debugging requests → All detected as `debugging`
3. Check V2 has learned patterns:
   ```bash
   curl http://localhost:5005/api/nexus/learned-conversation-patterns/code_generation
   ```
4. Monitor system resilience:
   - Restart V2 → V3 gracefully handles unavailable
   - Check logs for cross-service communication

**Success Criteria**:
- 100% detection accuracy on test set
- V2 ML engine active and learning
- System handles V2 outages gracefully

---

## Implementation Details by File

| File | Change | Impact | Risk |
|------|--------|--------|------|
| `server/conversation-detector.ts` | Line 68: multiplier boost | 7/8→8/8 types | Low - keyword tuning only |
| `server/index.ts` | Enable V2 routes | V2 becomes accessible | Low - routes already defined |
| `tools/luminar_nexus_v2.py` | Add conversation methods | ML for patterns | Medium - new functionality |
| `server/routes.ts` | Add pattern piping | V3→V2 communication | Medium - async pipe |
| NEW: `server/conversation-pattern-adapter.ts` | Create adapter layer | Clean separation | Low - isolated logic |

---

## Risk Assessment & Mitigation

### Risk 1: V2 Crashes, Breaks Chat
**Impact**: Medium (chat still works, just no ML)  
**Mitigation**: Wrap all V2 calls in try-catch, graceful degradation

### Risk 2: Cross-Service Communication Fails
**Impact**: Low (V3 works without V2)  
**Mitigation**: V2→V3 pipes are async, not blocking

### Risk 3: Memory Leak from Pattern Storage
**Impact**: Low (capped at 1000 per type)  
**Mitigation**: Already implemented in V2 code

### Risk 4: Network Latency Between Services
**Impact**: Low (V2 calls are fire-and-forget)  
**Mitigation**: Pipe patterns asynchronously

---

## Success Metrics

### Short-term (Phase 1-2)
- ✅ 8/8 conversation types detected
- ✅ V2 running and healthy
- ✅ V3 can proxy requests to V2

### Medium-term (Phase 3)
- ✅ V2 receiving conversation patterns
- ✅ Learned patterns stored (1000+ per type)
- ✅ Confidence scores improve 5-10% after 100 conversations

### Long-term (Phase 4+)
- ✅ Aurora reaches 95%+ detection accuracy
- ✅ V2 ML engine self-optimizes
- ✅ System scales to multiple conversation types

---

## Timeline & Effort

| Phase | Task | Effort | Timeline |
|-------|------|--------|----------|
| 1 | Fix detection multipliers | 30 min | Turn 1 |
| 2 | Enable V2 service | 30 min | Turn 1-2 |
| 3 | V2 ML integration | 2 hours | Turn 2-3 |
| 4 | Testing & validation | 1-2 hours | Turn 3-4 |
| **Total** | **Full Integration** | **4-5 hours** | **3-4 Turns** |

---

## What We're Leveraging

**From V2** (Don't reinvent, reuse):
- ✅ `AIServiceOrchestrator.learn_service_patterns()` → `learn_conversation_patterns()`
- ✅ `_calculate_performance_score()` → `_calculate_confidence_score()`
- ✅ `_analyze_metric_correlations()` → `analyze_keyword_correlations()`
- ✅ `predict_service_issues()` → `predict_type_confusion()`
- ✅ Pattern history (last 1000) — efficient and proven

**From V3**:
- ✅ ConversationDetector (foundation)
- ✅ ResponseAdapter (format optimization)
- ✅ Aurora Chat (user interface)
- ✅ 188 Power Units (already operational)

---

## Decision Points

### Should We Use V2 or Build New ML Module?
**Answer**: V2 has proven ML code, already handles history/patterns, less risk.

### Should ML Learning Be Synchronous or Async?
**Answer**: Async (V2 pipes don't block chat response to user).

### Should We Auto-Update Detection Based on V2 Feedback?
**Answer**: Phase 1: No (manual tuning). Phase 3: Yes (async improvement).

### What If V2 Goes Down?
**Answer**: V3 continues normally. Chat works. Just no new ML data collected.

---

## Next Steps

### To Start:
1. **Turn 1**: Apply Phase 1 changes to `conversation-detector.ts`
2. **Turn 1**: Verify 8/8 types working
3. **Turn 2**: Enable V2, verify connectivity
4. **Turn 3**: Implement adapter layer, test E2E
5. **Turn 4**: Validate, monitor, celebrate

### Decision Required:
Do you want to proceed with this plan? 
- **"Yes"** → Start Phase 1 immediately
- **"Yes, but focus on Phase 1-2 only"** → Get detection + V2 running
- **"Modify the plan"** → Tell me what to change

---

## Appendix: Key Code Locations

```
Core Detection:
  server/conversation-detector.ts (line 68 - multiplier tuning)
  server/conversation-detector.ts (line 43 - keyword arrays)
  
V2 Integration:
  tools/luminar_nexus_v2.py (AIServiceOrchestrator class)
  server/luminar-routes.ts (V2 route definitions)
  server/index.ts (V2 registration comment)
  
Response Adaptation:
  server/response-adapter.ts (type-based formatting)
  server/aurora-chat.ts (chat endpoints)
```

---

**Status**: Ready for approval  
**Owner**: Chango Aurora System  
**Last Updated**: November 28, 2025
