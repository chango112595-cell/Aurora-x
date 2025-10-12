# Chango - AI-Powered Autonomous Code Synthesis Platform

## Overview

Chango is a JARVIS-inspired web application that acts as the interface for Aurora-X Ultra, an offline autonomous code synthesis engine. It allows users to request complex code generation through a chat interface, monitor real-time synthesis progress, explore generated code libraries, and analyze corpus learning data. Designed with a cinematic tech aesthetic, Chango aims to provide a professional, developer-first experience for AI-assisted code generation, with ambitions for market potential as a leading autonomous code synthesis platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**December 2024 Updates**:
- Added T13 "Universal Code Synthesis Engine (UCSE)" to Master Task List (5% complete)
- Implemented visual task dependency graph visualization with D3.js at /dashboard/graph endpoint
- Fixed dashboard rendering issue: Updated Task interface to handle numeric percent values from API
- Improved sidebar navigation with proper client-side routing using wouter Link components
- Fixed "View Task Graph" button to correctly navigate to /dashboard/graph (now served by Express backend)
- Added interactive force-directed graph with color-coded task status indicators
- **NEW**: Made graph nodes editable - click any node to update task percentage directly (updates progress.json in real-time)
- **NEW**: Auto-refresh README badges - task updates now automatically update README progress badges (set AURORA_AUTO_GIT=1 to enable auto git commit/push)

## System Architecture

**Frontend Architecture**:
- **Technology Stack**: React 18 with TypeScript, Vite.
- **UI Framework**: Shadcn/ui (Radix UI + Tailwind CSS) with a "New York" style variant.
- **Routing**: Wouter for client-side routing, including Home, Dashboard, Library, Corpus, and Settings pages.
- **State Management**: TanStack Query for server state management.
- **Design System**: Custom HSL-based theme with dark mode, cinematic tech colors (JARVIS-inspired cyan, emerald, amber, purple), Inter font for UI, and JetBrains Mono for code.
- **Component Architecture**: Modular structure separating UI primitives, feature components, and page-level components.
- **Dashboard Features**: Real-time progress tracking with 13 tasks (T01-T13), overall progress at 83.8%, visual task cards with status indicators.

**Backend Architecture**:
- **Framework**: Express.js server with TypeScript, ESM modules.
- **API Design**: RESTful API for corpus management, including endpoints for ingesting, querying, and retrieving similar functions. New endpoints for real-time synthesis progress tracking (`/api/synthesis/progress`, `/api/synthesis/result`, `/api/synthesis/estimate`), domain-specific problem solving (`/api/solve`, `/api/explain`), and unit conversion (`/api/units`).
- **Request Validation**: Zod schemas for runtime type validation.
- **Middleware Stack**: JSON body parsing, custom logging, error handling.
- **Deployment**: Production-grade CI/CD with GitHub Actions for SSH and GHCR deployments, supporting multi-architecture Docker builds, automatic backups, health-gated rollouts, and rollback capabilities.
- **Auto-Updater**: Zero-maintenance update system for Aurora-X, featuring automatic git pull, Docker rebuilds, and health checks via a `/healthz` endpoint.
- **Language Router**: Automatic language selection (Python, Go, Rust, C#) based on prompt keywords, with configurable PORT environment variables for web services and a `/healthz` endpoint for service monitoring.
- **Progress Tracking**: Real-time synthesis progress display with live ETA, percentage, and stage indicators, updated via WebSockets.
- **Domain Router**: Integration of Math & Physics solvers for English prompts, unit conversion, and safe expression evaluation using AST.

**Data Storage Solutions**:
- **Corpus Database**: SQLite (better-sqlite3) with WAL for concurrent reads, tracking function synthesis metadata with advanced querying (filtering, similarity scoring using Jaccard distance, pagination).
- **Schema Design**: `corpus` table with 18 fields, UUID primary keys, ISO 8601 timestamps, JSON-serialized arrays, and computed fields for similarity matching.
- **Indexes**: Optimized for lookups by specification, function name, signature, timestamp, and score.
- **User Storage**: In-memory storage with interface-based design for future migration to persistent storage.
- **Migration Strategy**: Drizzle ORM configured for PostgreSQL migrations.

**Authentication and Authorization**:
- **API Security**: Header-based API key authentication (`x-api-key`) for corpus ingestion.
- **User Authentication**: Schema prepared for username/password authentication with Drizzle ORM.
- **Session Management**: Infrastructure for PostgreSQL-backed sessions (connect-pg-simple).

## External Dependencies

- **Aurora-X Integration**: Aurora-X Ultra (Python-based autonomous code synthesis engine) for code generation.
- **Anthropic AI SDK**: `@anthropic-ai/sdk` for potential LLM features.
- **Database Providers**: Neon Serverless PostgreSQL (`@neondatabase/serverless`) for production, SQLite (`better-sqlite3`) for corpus storage and local development.
- **UI Component Dependencies**: Radix UI primitives for accessible, unstyled components.
- **Build and Development Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS.