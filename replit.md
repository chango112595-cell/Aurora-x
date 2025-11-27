# Chango - AI-Powered Autonomous Code Synthesis Platform

## Overview

Chango is a JARVIS-inspired web application that serves as the interface for Aurora-X Ultra, an offline autonomous code synthesis engine. It provides a chat interface for requesting complex code generation, monitoring real-time synthesis progress, exploring generated code libraries, and analyzing corpus learning data. Chango aims to deliver a professional, developer-first experience for AI-assisted code generation, with significant market potential as a leading autonomous code synthesis platform.

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
- **Port Configuration**: Luminar Nexus V2 API runs on port 5005, backend/frontend on port 5000. Frontend is served via Vite middleware through the backend.
- **Service Registry**: Monitors backend:5000 (fullstack service) only, avoiding monitoring of non-existent or middleware services.
- **Health Monitoring**: Socket-based connectivity checks with AI analysis for performance classification. "Down" services skip AI analysis.
- **Quantum Coherence**: System health metric based on `healthy_services / total_services` ratio.

## External Dependencies

- **Aurora-X Integration**: Aurora-X Ultra (Python-based autonomous code synthesis engine).
- **Database Providers**: Neon Serverless PostgreSQL (`@neondatabase/serverless`) for production, SQLite (`better-sqlite3`) for local development and corpus storage.
- **UI Component Dependencies**: Radix UI primitives.
- **Build and Development Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS.
- **AI SDK**: `@anthropic-ai/sdk` (for Claude Sonnet 4 integration in Aurora Chat AI).