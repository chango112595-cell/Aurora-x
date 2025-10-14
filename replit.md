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

**Data Storage Solutions**:
- **Corpus Database**: SQLite (better-sqlite3) with WAL for function synthesis metadata, including advanced querying and similarity scoring (Jaccard distance).
- **Schema Design**: `corpus` table with 18 fields, UUID primary keys, ISO 8601 timestamps, and JSON-serialized arrays.
- **Migration Strategy**: Drizzle ORM configured for PostgreSQL migrations.

**Authentication and Authorization**:
- **API Security**: Header-based API key authentication (`x-api-key`) for corpus ingestion.
- **User Authentication**: Schema prepared for username/password authentication with Drizzle ORM and PostgreSQL-backed sessions.

## Recent Updates

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