# Chango - AI-Powered Autonomous Code Synthesis Platform

## Overview

Chango is a JARVIS-inspired web application serving as the interface for Aurora-X Ultra, an offline autonomous code synthesis engine. It enables users to request complex code generation via a chat interface, monitor real-time synthesis progress, explore generated code libraries, and analyze corpus learning data. Chango aims to deliver a professional, developer-first experience for AI-assisted code generation, with significant market potential as a leading autonomous code synthesis platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**:
- **Technology Stack**: React 18 with TypeScript, Vite, Wouter for routing.
- **UI Framework**: Shadcn/ui (Radix UI + Tailwind CSS) with a "New York" style variant.
- **Design System**: Custom HSL-based dark mode theme with cinematic tech colors (cyan, emerald, amber, purple), Inter font for UI, and JetBrains Mono for code.
- **State Management**: TanStack Query for server state management.
- **Dashboard Features**: Real-time progress tracking with 13 tasks, visual task cards, and interactive graph visualizations.

**Backend Architecture**:
- **Framework**: Express.js server with TypeScript, ESM modules.
- **API Design**: RESTful API for corpus management, real-time synthesis progress (`/api/synthesis/*`), domain-specific problem solving (`/api/solve`, `/api/explain`), and unit conversion (`/api/units`).
- **Request Validation**: Zod schemas.
- **Deployment**: Production-grade CI/CD with GitHub Actions, multi-architecture Docker builds, automatic backups, health-gated rollouts, and rollback capabilities.
- **Auto-Updater**: Zero-maintenance update system with automatic git pull, Docker rebuilds, and health checks.
- **Language Router**: Automatic language selection (Python, Go, Rust, C#) based on prompts.
- **Progress Tracking**: Real-time synthesis progress via WebSockets.
- **Bridge Protocol**: API bridge endpoints (`/api/bridge/nl`, `/api/bridge/spec`, `/api/bridge/deploy`, `/api/bridge/nl/project`) for natural language and spec compilation, Git integration with automatic commits/pushes, Discord webhooks, and Replit ping support. Includes features for signed commits, preview/diff endpoints, and automatic GitHub Pull Request creation and rollback controls.
- **Aurora Chat AI**: Anthropic Claude-powered conversational AI with natural language processing, conversation memory management (10 turn history with pair-wise trimming), web search capabilities via DuckDuckGo API, and graceful fallback mode when Claude is unavailable. Located in `server/aurora-chat.ts`.

**Data Storage Solutions**:
- **Corpus Database**: SQLite (better-sqlite3) with WAL for function synthesis metadata, including advanced querying and similarity scoring (Jaccard distance).
- **Schema Design**: `corpus` table with 18 fields, UUID primary keys, ISO 8601 timestamps, and JSON-serialized arrays.
- **Migration Strategy**: Drizzle ORM configured for PostgreSQL migrations.

**Authentication and Authorization**:
- **API Security**: Header-based API key authentication (`x-api-key`) for corpus ingestion.
- **User Authentication**: Schema prepared for username/password authentication with Drizzle ORM and PostgreSQL-backed sessions.

**Luminar Nexus V2 Integration**:
- **Service Monitoring**: AI-driven service orchestration and monitoring system with quantum-inspired architecture.
- **Port Configuration**: Luminar Nexus V2 API runs on port 5005, backend/frontend on port 5000.
- **Architecture Note**: Frontend is served via Vite middleware through backend on port 5000 (not separate port 5173). Only backend:5000 requires monitoring as it serves both API and frontend.
- **Service Registry**: Monitors backend:5000 (fullstack service) only. Services that don't exist (bridge, chat, self-learn) or run as middleware (Vite) are not monitored to prevent false healing triggers.
- **Health Monitoring**: Socket-based connectivity checks with AI analysis for performance classification. "Down" services skip AI analysis to prevent healing loops.
- **Quantum Coherence**: System health metric based on healthy_services / total_services ratio (100% = all services healthy).

## Recent Updates

**November 27, 2025 (Final Debug)**:
- **Critical Bug Fixed**: Rate limiter was blocking `/api/health` endpoint
  - Problem: Health checks called every 5 seconds hit 100 request/15 minute limit, returning 429 errors
  - Solution: Moved health endpoint BEFORE rate limiter middleware to exempt it from limiting
  - Removed duplicate health endpoint at line 1552
  - Result: Health checks now return 200 OK consistently
- **System Status**: All systems operational
  - Aurora: 188 power units operational (100-worker autofixer pool)
  - LSP: Clean (no diagnostics)
  - Nexus V3: Active (tools/luminar_nexus.py loaded)
  - WebSocket: Ready on /ws/synthesis and /aurora/chat

**November 27, 2025 (Aurora 35-Files Completion)**:
- **Aurora 35-File Game Plan COMPLETE**: Executed the complete game plan for Universal IDE & Deployment Integration:
  - **Phase 1 (Core Integration - 4 files)**: All core files verified and operational
    - `aurora_x/self_learn_diagnostics.py` (249 lines)
    - `tools/aurora_autonomous_fixer.py` (1024 lines)
    - `tools/aurora_terminal_chat.py` (162 lines)
    - `tools/aurora_emergency_recovery.py` (229 lines)
  - **Phase 2 (IDE Support - 9 files)**: All IDE reference files in place
    - VS Code performance patterns, Python language support, terminal client reference
    - Chat creation patterns, enhancement techniques, feature documentation
    - Auto-fix algorithms, workflow automation, power user commands
  - **Phase 3 (Universal Deployment - 22+ files)**: Complete deployment infrastructure
    - Linux: install-linux.sh, INSTALL_LINUX.md, README_LINUX.md, LINUX_QUICKSTART.txt
    - Docker: docker-compose.yml, multiple Dockerfiles
    - Testing: test_aurora_comprehensive.py, test_aurora_fix.py, verify_tiers.py
    - Requirements: requirements-dev.txt, requirements-test.txt, requirements-ubuntu.txt
    - Documentation: AURORA_SMART_INTERFACE_DRAFT.md, LUMINAR_NEXUS_STATUS.md
  - **Frontend Fix**: Replaced Next.js imports with wouter for Vite compatibility
  - **Total**: 5,663+ lines of production-ready code across 35 files

- **Aurora 4-File Experimental Integration**: Completed integration of 4 experimental Aurora modules following the AURORA_INTEGRATION_DETAILED_FIX_GUIDE.md:
  - **Self-Learning Diagnostics** (`aurora_x/self_learn_diagnostics.py`): 
    - Honest 0-100 quality scoring with true zero on failures
    - Persistent state tracking via `.aurora_diagnostics.json`
    - Failure pattern analysis and learning progress metrics
    - Integrated with `aurora_x/self_learn.py` for quality tracking
  - **Autonomous Healing** (`tools/aurora_autonomous_fixer.py`):
    - AutonomousHealer class with 6 health check systems
    - Checks: self_learn, chat_server, corpus_db, frontend, diagnostics, state_files
    - Before/after health comparison during healing
    - API endpoint: `POST /api/heal` for triggering autonomous healing
  - **Emergency Recovery** (`tools/aurora_recovery_system.py`):
    - Backup/restore with integrity verification
    - Health report with critical file and state file checks
    - Preview restore functionality before actual restore
  - **Terminal Chat Client** (`tools/aurora_terminal_client.py`):
    - Interactive terminal interface for Aurora chat
    - Dependency checking with clear install instructions
    - Enhanced error handling for various HTTP status codes
    - Usage: `python3 tools/aurora_terminal_client.py`

**November 15, 2025**:
- **System-Wide Debugging and Optimization**: Comprehensive system health check and fixes
  - Fixed Luminar Nexus V2 Aurora Bridge warning being printed unconditionally
  - Fixed CREATE_NEW_PROCESS_GROUP cross-platform compatibility issue in luminar_nexus_v2.py (Windows/Linux)
  - Fixed quantum coherence initialization showing 0.0 at startup - now maintains 1.0 until first health check completes
  - Updated @replit/vite-plugin-cartographer from 0.3.2 to 0.4.3
  - All LSP errors resolved - codebase is clean
- **Security Configuration Notes**:
  - `ANTHROPIC_API_KEY`: Required for Aurora Chat AI with Claude Sonnet 4. System falls back to conversational mode when unavailable
  - `JWT_SECRET`: Currently using default development secret. Set custom value in production for enhanced security
  - `ADMIN_PASSWORD`: Set via environment variable. Default development password is in use
- **Corpus Database Git Issue**: 
  - File `data/corpus.db` is properly listed in `.gitignore`
  - If still appearing in git status, it was likely committed before being ignored
  - **To remove from git tracking** (user action required):
    ```bash
    git rm --cached data/corpus.db
    git rm --cached data/corpus.db-shm
    git rm --cached data/corpus.db-wal
    git commit -m "Remove corpus database from git tracking"
    ```
  - This removes files from git index while preserving them on disk

**November 13, 2025**:
- **Aurora Chat AI Enhanced**: Integrated Anthropic Claude Sonnet 4 for natural, human-like conversations
  - Conversation memory management with proper user/assistant pairing (10 turn history, 20 messages total)
  - Pair-wise trimming logic ensures conversation structure is always maintained
  - Safety guards prevent orphaned assistant messages
  - Web search capability via DuckDuckGo API for real-time information access
  - Graceful fallback mode with friendly responses when Claude API is unavailable
  - Robust error handling with multiple fallback layers
- **Fixed Luminar Nexus V2 Routing**: Updated sidebar URL from `/luminar` to `/luminar-nexus` to match route definition
- **Fixed HTTP Server Creation**: Added proper `createServer` initialization and corrected import paths
- **Fixed Luminar Nexus V2 Healing Loops**: Reduced service registry from 5 phantom services to 1 actual service (backend:5000), eliminating false healing triggers
- **Quantum Coherence Restored**: Improved from 20% to 100% by monitoring only actually running services
- **Health Check Logic**: Fixed to properly handle "down" services without triggering autonomous healing loops. Down services now skip AI analysis
- **LSP Errors Fixed**: Resolved serviceName scope issue in server/routes.ts error handling

**October 14, 2024**:
- **Enhanced CI/CD Pipeline**: 
  - Upgraded GitHub Actions workflow with SARIF output for GitHub Security tab integration
  - Coverage badge generation as SVG with color coding (red <60%, orange <80%, yellow <85%, green ≥85%)
  - Auto-publishing of coverage badge to separate 'badges' branch
  - Coverage calculation using lxml for accurate XML parsing
- **PR Rollback Controls**: 
  - Added rollback endpoints to manage Aurora-generated pull requests
  - Dashboard UI integration with "Rollback Open PR" and "Revert Last Merged PR" buttons
  - Requires AURORA_GH_TOKEN environment variable with repo permissions
- **Coverage Badge**: Added coverage badge to README.md for real-time coverage visibility
- **GPG Signing**: Generated new GPG key for verified commits
- **Aurora Chat Fixed**: Natural language processing now handles English commands correctly
- **Dashboard Generate Button**: Integrated for PR creation via Aurora Bridge

## External Dependencies

- **Aurora-X Integration**: Aurora-X Ultra (Python-based autonomous code synthesis engine).
- **Database Providers**: Neon Serverless PostgreSQL (`@neondatabase/serverless`) for production, SQLite (`better-sqlite3`) for local development and corpus storage.
- **UI Component Dependencies**: Radix UI primitives.
- **Build and Development Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS.
- **AI SDK**: `@anthropic-ai/sdk` (for potential LLM features).