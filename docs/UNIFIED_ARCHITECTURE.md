# Aurora-X Ultra - Unified Architecture

## Overview

Aurora-X Ultra is a self-contained, AI-powered autonomous code synthesis platform. All intelligence systems run internally with no external API dependencies.

## Cognitive Event Loop

Aurora continuously cycles through six phases:

```
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE EVENT LOOP                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [User Input] ──► [Perception] ──► [Context Retrieval]         │
│       ▲                                    │                    │
│       │                                    ▼                    │
│  [Learning] ◄── [Reflection] ◄── [Reasoning]                   │
│       │                                    │                    │
│       │                                    ▼                    │
│       └────────────────────────── [Action Execution]            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Details

| Phase | Component | Purpose |
|-------|-----------|---------|
| **Perception** | Aurora AI Engine | Process incoming user input |
| **Context Retrieval** | Memory Fabric V2 | Gather relevant memories and facts |
| **Reasoning** | Luminar Nexus V2 | Language understanding and intent analysis |
| **Consciousness Alignment** | Aurora Nexus V3 | Coordinate awareness and worker state |
| **Action Execution** | Aurora-X Core | Generate response or synthesize code |
| **Reflection** | Memory Fabric V2 | Store outcomes and update context |
| **Learning** | Adaptive Bias Scheduler | Adjust behavior based on feedback |

## System Integration Blueprint

```
┌──────────────────────────────────────────────────────────────────────┐
│                        AURORA-X ULTRA SYSTEM                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              FRONTEND (React + TypeScript)                   │    │
│  │                                                              │    │
│  │  [Aurora Chat] [Corpus Browser] [Evolution] [Dashboard]     │    │
│  └──────────────────────────┬───────────────────────────────────┘    │
│                             │ WebSocket + REST                       │
│  ┌──────────────────────────▼───────────────────────────────────┐    │
│  │           BACKEND (Express + TypeScript) Port 5000           │    │
│  │                                                              │    │
│  │  [API Gateway] ──► [Aurora AI Engine] ──► [Cognitive Loop]  │    │
│  │        │                   │                    │            │    │
│  └────────┼───────────────────┼────────────────────┼────────────┘    │
│           │                   │                    │                 │
│  ┌────────▼───────────────────▼────────────────────▼────────────┐    │
│  │              PYTHON COGNITIVE SYSTEMS                         │    │
│  │                                                              │    │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │    │
│  │  │ Aurora Nexus V3  │  │ Luminar Nexus V2 │                 │    │
│  │  │ Port 5002        │  │ Port 8000        │                 │    │
│  │  │                  │  │                  │                 │    │
│  │  │ - Consciousness  │  │ - Language       │                 │    │
│  │  │ - 300 Workers    │  │ - Reasoning      │                 │    │
│  │  │ - Orchestration  │  │ - Pattern Learn  │                 │    │
│  │  └────────┬─────────┘  └────────┬─────────┘                 │    │
│  │           │                     │                            │    │
│  │  ┌────────▼─────────────────────▼───────────────────────┐   │    │
│  │  │              Memory Fabric V2 - Port 5004             │   │    │
│  │  │                                                       │   │    │
│  │  │  [Short-Term] ──► [Mid-Term] ──► [Long-Term]         │   │    │
│  │  │       │               │               │               │   │    │
│  │  │       └───────────────┴───────────────┘               │   │    │
│  │  │                       │                               │   │    │
│  │  │              [Semantic Memory Layer]                  │   │    │
│  │  └───────────────────────────────────────────────────────┘   │    │
│  │                                                              │    │
│  │  ┌───────────────────────────────────────────────────────┐   │    │
│  │  │                 Aurora-X Core                          │   │    │
│  │  │                                                       │   │    │
│  │  │  [Synthesis Engine] ◄──► [Adaptive Bias Scheduler]    │   │    │
│  │  │         │                          │                  │   │    │
│  │  │         └──────────────────────────┘                  │   │    │
│  │  │                Self-Learning Loop                     │   │    │
│  │  └───────────────────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Memory Evolution Model

Memory flows through three tiers with automatic consolidation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY EVOLUTION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Input/Event] ──► [SHORT-TERM MEMORY]                         │
│                          │                                      │
│                          │ Threshold: 10 messages               │
│                          ▼                                      │
│                    [Context Embedding]                          │
│                    [Similarity Mapping]                         │
│                          │                                      │
│                          ▼                                      │
│                    [MID-TERM MEMORY]                            │
│                          │                                      │
│                          │ Threshold: 10 summaries              │
│                          ▼                                      │
│                    [Pattern Consolidation]                      │
│                    [Fact Extraction]                            │
│                          │                                      │
│                          ▼                                      │
│                    [LONG-TERM MEMORY]                           │
│                          │                                      │
│                          ▼                                      │
│                    [Knowledge Graph]                            │
│                          │                                      │
│                          ▼                                      │
│                    [SEMANTIC RECALL] ◄──────────────────────┐  │
│                          │                                   │  │
│                          └───────────────────────────────────┘  │
│                                  Contextual Recall              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Tiers

| Tier | Purpose | Capacity | Lifespan |
|------|---------|----------|----------|
| **Short-Term** | Transient conversation buffer | 10 messages | Session |
| **Mid-Term** | Semantic meaning + emotional tone | 10 summaries | Days |
| **Long-Term** | Consolidated facts and relationships | 100 entries | Permanent |
| **Semantic** | Vector-indexed knowledge | 500 entries | Permanent |

## Core Components

### 1. Aurora Nexus V3 (Consciousness Layer)

- **Port**: 5002
- **Purpose**: Universal consciousness system
- **Features**:
  - 188 Grandmaster Tiers
  - 66 Advanced Execution Methods
  - 550 Cross-Temporal Modules
  - 300 Autonomous Workers

### 2. Luminar Nexus V2 (Language Layer)

- **Port**: 8000
- **Purpose**: Language understanding and reasoning
- **Features**:
  - Pattern recognition
  - Intent classification
  - Conversation flow management
  - ML-based response generation

### 3. Memory Fabric V2 (Memory Layer)

- **Port**: 5004
- **Purpose**: Semantic memory storage and retrieval
- **Features**:
  - Three-tier memory model
  - Automatic consolidation
  - Vector similarity search
  - Fact and event storage

### 4. Aurora-X Core (Synthesis Layer)

- **Purpose**: Code synthesis and learning
- **Features**:
  - Adaptive Bias Scheduler
  - Self-learning daemon
  - Epsilon-greedy exploration
  - Continuous improvement

## Data Flow

1. **User Input** → Express Backend (port 5000)
2. **Context Retrieval** → Memory Fabric V2 (port 5004)
3. **Consciousness Query** → Aurora Nexus V3 (port 5002)
4. **Language Processing** → Luminar Nexus V2 (port 8000)
5. **Response Generation** → Aurora AI Engine
6. **Memory Update** → Memory Fabric V2
7. **Learning Feedback** → Adaptive Bias Scheduler
8. **Response** → User

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Express.js, TypeScript, WebSocket |
| AI Core | Python, Flask, NumPy |
| Storage | SQLite, JSON (in-memory) |
| Communication | HTTP REST, WebSocket |

## Self-Contained Design

Aurora-X Ultra operates 100% internally:

- No external AI APIs (Anthropic, OpenAI, etc.)
- No external vector databases (Pinecone, etc.)
- No Docker or containers required
- All services run natively on the host

## Running the System

```bash
# Start all services
./aurora-start

# Individual services
python3 aurora_nexus_v3/main.py    # Consciousness (port 5002)
python3 tools/luminar_nexus_v2.py serve  # Language (port 8000)
npm run dev                         # Frontend + Backend (port 5000)
```

## Architecture Principles

1. **Self-Contained**: All intelligence runs internally
2. **Typed**: TypeScript orchestration ensures type safety
3. **Modular**: Each component has a single responsibility
4. **Adaptive**: Continuous learning from interactions
5. **Resilient**: Fallback mechanisms at every layer
6. **Observable**: Full cognitive event logging
