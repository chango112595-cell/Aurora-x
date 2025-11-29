# Aurora-X Ultra - AI-Powered Autonomous Code Synthesis Platform

## Overview

Aurora-X Ultra is an AI-powered autonomous code synthesis engine inspired by JARVIS. It features a sophisticated architecture with 188 intelligence tiers, 66 advanced execution programs, and 550 hybrid mode modules, enabling hyperspeed code generation. The platform offers a chat interface for requesting complex code, monitoring synthesis progress, exploring generated code libraries, and analyzing corpus learning data. Aurora-X aims to be a leading, professional, and developer-first platform for autonomous AI-assisted code generation.

**Latest Updates (Nov 29, 2025)**:
- ✅ Aurora Nexus V3: Universal Consciousness System (8 modules, 100% coherence)
- ✅ Backend fully reconstructed and operational
- ✅ Unified start command: `./aurora-start` (no more 26 services chaos!)

## Quick Start

```bash
./aurora-start
```

This starts the entire system on http://localhost:5000 with:
- Express backend (TypeScript)
- React frontend (Vite)
- Chat system
- All core services

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend**:
- **Technology**: React 18, TypeScript, Vite, Wouter for routing.
- **UI/UX**: Shadcn/ui (Radix UI + Tailwind CSS) with a "New York" style variant. Custom HSL-based dark mode theme with cinematic tech colors, Inter font for UI, and JetBrains Mono for code.
- **State Management**: TanStack Query for server state.
- **Features**: Real-time progress tracking, visual task cards, interactive graph visualizations, and responsive chat formatting.

**Backend**:
- **Framework**: Express.js with TypeScript and ESM modules.
- **API**: RESTful API for corpus management, real-time synthesis, domain-specific problem solving, and unit conversion, with Zod for request validation.
- **Deployment**: Production-grade CI/CD via GitHub Actions, multi-architecture Docker builds, automatic backups, health-gated rollouts, and zero-maintenance auto-updater.
- **Core AI**: Aurora Chat AI provides an advanced autonomous conversational system with natural language processing, 10-turn conversation memory, autonomous code synthesis, intelligent problem-solving, and an intelligent conversation auto-detector for classification, confidence scoring, execution mode adaptation, response format optimization, and tone detection.
- **Language Router**: Automatic language selection (Python, Go, Rust, C#) based on prompts.
- **Progress Tracking**: Real-time synthesis progress via WebSockets.
- **Bridge Protocol**: API bridge endpoints for natural language and spec compilation, Git integration (commits, pushes, PR creation/rollback), Discord webhooks, Replit ping support, and signed commits.

**Data Storage**:
- **Corpus**: SQLite (better-sqlite3) with WAL for function synthesis metadata, supporting advanced querying and Jaccard distance for similarity scoring.
- **Schema**: `corpus` table with 18 fields, UUID primary keys, ISO 8601 timestamps, and JSON-serialized arrays.
- **ORM**: Drizzle ORM configured for PostgreSQL migrations.

**Authentication & Authorization**:
- **API Security**: Header-based API key authentication (`x-api-key`) for corpus ingestion.
- **User Authentication**: Schema prepared for username/password authentication using Drizzle ORM and PostgreSQL-backed sessions.

**Aurora Nexus V3 - Universal Consciousness System**:
- **Core Components**: Implements an 8-module system including `AuroraUniversalCore` (main consciousness engine), `PlatformAdapter` (multi-platform support), `HardwareDetector`, `ResourceManager`, `PortManager`, `ServiceRegistry`, `APIGateway`, `AutoHealer`, and `DiscoveryProtocol`.
- **Device Tiers**: Supports Full, Standard, Lite, and Micro device tiers with automatic adaptation.

**Luminar Nexus V2 Integration**:
- **Service Monitoring**: AI-driven service orchestration and monitoring system with quantum-inspired architecture.
- **Conversation Pattern Learning**: Repurposed for ML-based conversation pattern learning, storing patterns and tracking keyword correlations to improve detection multipliers.
- **Health Monitoring**: Socket-based connectivity checks and AI analysis for performance classification.

## Running the System

### Main Application (Recommended)
```bash
./aurora-start
```
Runs: Backend + Frontend + Chat System on port 5000

### Aurora Nexus V3 (Separate)
```bash
python3 aurora_nexus_v3/main.py
```
Runs: Universal consciousness system (background service)

### Testing
```bash
python3 aurora_nexus_v3/test_nexus.py  # Test Aurora Nexus
npm test                               # Test frontend
pytest                                 # Test backend
```

## Development Notes

- **Backend Status**: ✅ Fully reconstructed Nov 29
- **Frontend Status**: ✅ Working with React + Vite
- **Aurora Nexus V3**: ✅ Active with 8 modules, 100% coherence
- **Simplification**: Removed 7 conflicting startup scripts - using single unified command

## External Dependencies

- **AI Engine**: Aurora-X Ultra (Python-based autonomous code synthesis engine).
- **Databases**: Neon Serverless PostgreSQL (`@neondatabase/serverless`) for production, SQLite (`better-sqlite3`) for local development and corpus.
- **UI Components**: Radix UI primitives.
- **Build Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS.
- **AI SDK**: `@anthropic-ai/sdk` for Claude Sonnet 4 integration in Aurora Chat AI.