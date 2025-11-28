# Aurora-X Ultra - AI-Powered Autonomous Code Synthesis Platform

## Overview

Aurora is a JARVIS-inspired autonomous code synthesis engine featuring 188 intelligence tiers, 66 advanced execution programs, and 200+ hybrid mode modules with hyperspeed capabilities. It provides a chat interface for requesting complex code generation, monitoring real-time synthesis progress, exploring generated code libraries, and analyzing corpus learning data. Aurora aims to deliver a professional, developer-first experience for AI-assisted code generation with significant market potential as a leading autonomous code synthesis platform.

**Aurora Specifications**:
- **188 Intelligence Tiers**: Full hierarchical knowledge structure for context-aware synthesis
- **66 Advanced Execution Programs**: Specialized execution engines for optimization, parallelization, and domain-specific synthesis
- **200+ Hybrid Mode Modules**: Extensible modules supporting multi-language compilation, framework integration, and cross-platform deployment
- **Hyperspeed Mode**: Accelerated synthesis with intelligent caching and pattern recognition

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**:
- **Technology Stack**: React 18 with TypeScript, Vite, Wouter for routing.
- **UI Framework**: Shadcn/ui (Radix UI + Tailwind CSS) with a "New York" style variant.
- **Design System**: Custom HSL-based dark mode theme with cinematic tech colors, Inter font for UI, and JetBrains Mono for code.
- **State Management**: TanStack Query for server state management.
- **Dashboard Features**: Real-time progress tracking, visual task cards, and interactive graph visualizations.

**Backend Architecture**:
- **Framework**: Express.js server with TypeScript, ESM modules.
- **API Design**: RESTful API for corpus management, real-time synthesis progress, domain-specific problem solving, and unit conversion.
- **Request Validation**: Zod schemas.
- **Deployment**: Production-grade CI/CD with GitHub Actions, multi-architecture Docker builds, automatic backups, health-gated rollouts, and rollback capabilities. Features a zero-maintenance auto-updater.
- **Language Router**: Automatic language selection (Python, Go, Rust, C#) based on prompts.
- **Progress Tracking**: Real-time synthesis progress via WebSockets.
- **Bridge Protocol**: API bridge endpoints for natural language and spec compilation, Git integration with automatic commits/pushes, Discord webhooks, Replit ping support, signed commits, preview/diff endpoints, and automatic GitHub Pull Request creation and rollback controls.
- **Aurora Chat AI**: Advanced autonomous conversational system with natural language processing, conversation memory management (10-turn history), autonomous code synthesis, intelligent problem-solving, and an intelligent conversation auto-detector for classification, confidence scoring, execution mode adaptation, response format optimization, and tone detection.

**Data Storage Solutions**:
- **Corpus Database**: SQLite (better-sqlite3) with WAL for function synthesis metadata, including advanced querying and similarity scoring (Jaccard distance).
- **Schema Design**: `corpus` table with 18 fields, UUID primary keys, ISO 8601 timestamps, and JSON-serialized arrays.
- **Migration Strategy**: Drizzle ORM configured for PostgreSQL migrations.

**Authentication and Authorization**:
- **API Security**: Header-based API key authentication (`x-api-key`) for corpus ingestion.
- **User Authentication**: Schema prepared for username/password authentication with Drizzle ORM and PostgreSQL-backed sessions.

**Luminar Nexus V2 Integration**:
- **Service Monitoring**: AI-driven service orchestration and monitoring system with quantum-inspired architecture.
- **Port Configuration**: Luminar Nexus V2 API runs on port 8000, backend/frontend on port 5000. Frontend is served via Vite middleware through the backend.
- **Service Registry**: Monitors backend:5000 (fullstack service) only, avoiding monitoring of non-existent or middleware services.
- **Health Monitoring**: Socket-based connectivity checks with AI analysis for performance classification. "Down" services skip AI analysis.
- **Quantum Coherence**: System health metric based on `healthy_services / total_services` ratio.
- **Conversation Pattern Learning**: V2 now includes ML-based conversation pattern learning via `AIServiceOrchestrator`:
  - POST `/api/nexus/learn-conversation` - Learn from detected conversation patterns
  - GET `/api/nexus/learned-conversation-patterns` - Get all learned patterns
  - GET `/api/nexus/learned-conversation-patterns/:type` - Get patterns for specific type
  - GET `/api/nexus/keyword-correlations/:typeA/:typeB` - Analyze keyword correlations

## Recent Updates

**November 28, 2025 (Luminar Nexus V2 Integration & Conversation Learning - COMPLETE)**:
- **V2 Re-enabled**: Luminar Nexus V2 now runs on port 8000 as a background ML service
- **Conversation Pattern Learning**: V2's AIServiceOrchestrator repurposed for ML-based conversation pattern learning
  - Stores last 1000 patterns per conversation type
  - Tracks keyword correlations for improved detection
  - Calculates improved multipliers based on learned patterns
- **Detection Improvements**: Boosted code_generation detection from 1.8x to 2.3x multiplier
  - Added keywords: function, class, algorithm, api, component, program, service, endpoint, handler
  - Added pattern detection for FUNCTION, CLASS, ALGORITHM, API, ENDPOINT patterns (+20-25 boost)
  - De-prioritized question_answering when code context is strong
- **Robust Pattern Adapter**: 
  - `server/conversation-pattern-adapter.ts` - Bridges V3 detection with V2 ML learning
  - Queues patterns during V2 unavailability (max 50 pending patterns)
  - Flushes pending patterns on every successful health check
  - Handles cold starts and transient V2 outages gracefully
- **Updated Routes**:
  - `server/luminar-routes.ts` with conversation learning proxy endpoints
  - `tools/luminar_nexus_v2.py` with conversation learning methods and endpoints
- **V3-V2 Communication**: V3 proxies conversation patterns to V2 asynchronously for learning
- **Verified Working**: 5+ patterns learned, 97% avg confidence, common keywords detected

**November 27, 2025 (Aurora Auto-Detector System - LIVE & WORKING)**:
- **Intelligent Conversation Classification**: Aurora now automatically detects and adapts to 10 conversation types
  - Types: code_generation, debugging, explanation, architecture, optimization, testing, refactoring, analysis, question_answering, general_chat
  - Confidence scoring (0-100%) with keyword analysis and error detection
  - Auto-detected response prefixes with emojis (🔧 code, 🔍 debugging, 📚 explanation, etc.)
- **Core Implementation Files**:
  - `server/conversation-detector.ts` (310 lines): Intelligent keyword analysis, tone detection, confidence scoring
  - `server/response-adapter.ts` (260 lines): NEW - Enhances responses based on conversation type
  - `server/aurora-chat.ts`: Enhanced with detection metadata passing to Python
  - `server/routes.ts`: Integrated response adaptation pipeline
- **Execution Mode Adaptation**: fast, detailed, experimental, standard - automatically selected per conversation type
- **Response Format Optimization**: Selects best format (code, bullet_points, step_by_step, mixed) for conversation type
- **Status**: Tested and verified working - responses now adapt in real-time based on detected conversation classification
- **API Response Enhancement**: Returns detection metadata (`{"type": "...", "confidence": ...}`) for frontend awareness

**November 27, 2025 (Chat Improvements - Enhanced Formatting & Context)**:
- Improved welcome message with 5 key capabilities listed with bullet points
- Enhanced message formatting: code blocks with language detection, bold text, numbered lists, links
- Context-aware responses sending last 4 messages for better conversation understanding
- Better error messages that acknowledge user requests and offer alternatives
- Responsive code block styling for mobile and desktop

**November 27, 2025 (Routing & Chat Fix)**:
- **Routing System Fixed**: Implemented complete routing fix per ROUTING_FIX_GUIDE.md
  - Moved routing from `main.tsx` to `App.tsx` using wouter's `Switch` and `Route` components
  - Added 18 routes matching sidebar navigation paths
  - Sidebar navigation now properly changes page content (not just URL)
- **Aurora Chat Fixed**: Changed hardcoded `http://localhost:5000/api/chat` to relative `/api/chat`
  - Enables hosted environment compatibility (Replit, cloud deployments)
  - Allows browser to automatically use correct domain
- **Restored AuroraFuturisticChat**: Reverted to original chat component on home page
- **System Verification**: 188 power units operational, 100-worker autofixer pool active, WebSocket ready

## External Dependencies

- **Aurora-X Integration**: Aurora-X Ultra (Python-based autonomous code synthesis engine).
- **Database Providers**: Neon Serverless PostgreSQL (`@neondatabase/serverless`) for production, SQLite (`better-sqlite3`) for local development and corpus storage.
- **UI Component Dependencies**: Radix UI primitives.
- **Build and Development Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS.
- **AI SDK**: `@anthropic-ai/sdk` (for Claude Sonnet 4 integration in Aurora Chat AI).

## Key Files & Structures

**Conversation Detection System**:
- `server/conversation-detector.ts` - Analyzes messages, detects type, calculates confidence
- `server/response-adapter.ts` - Adapts responses with type-specific formatting and prefixes
- `server/aurora-chat.ts` - WebSocket + HTTP chat endpoints with detection integration
- `client/src/components/AuroraFuturisticChat.tsx` - Frontend chat UI with message formatting

**Routing**:
- `client/src/App.tsx` - Main router with 18 pages (Switch/Route from wouter)
- `client/src/pages/` - Page components for each sidebar item

**Authentication & Users**:
- `server/auth.ts` - JWT and session authentication
- `server/auth-routes.ts` - Login/register/logout endpoints
- `server/users.ts` - User store and management
