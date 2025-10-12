# Chango - AI-Powered Autonomous Code Synthesis Platform

## Overview

Chango is a futuristic, JARVIS-inspired web application that serves as the interface for Aurora-X Ultra, an offline autonomous code synthesis engine. The platform enables users to request complex code generation through a chat interface while monitoring real-time synthesis progress, exploring generated code libraries, and analyzing corpus learning data. Built with a cinematic tech aesthetic drawing inspiration from Linear's precision and Vercel's developer focus, Chango provides a professional developer-first experience for AI-assisted code generation.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (October 2025)

### T10 Progress Tracking System Complete ✅
- **Real-time Synthesis Progress**: Users now see exactly how long Aurora will take to complete code generation
  - Live progress bar with percentage and stage indicators (ANALYZING → GENERATING → TESTING → COMPLETE)
  - Time estimates: Simple (10s), Medium (20s), Complex (45s) based on request analysis
  - WebSocket real-time updates with automatic polling fallback every 2 seconds
  - Multiple concurrent syntheses tracked independently
- **Progress API Endpoints**: Complete progress lifecycle management
  - POST /api/chat returns synthesis_id immediately, processes asynchronously
  - GET /api/synthesis/progress/:id for current status checking
  - GET /api/synthesis/result/:id retrieves completed code with metadata
  - POST /api/synthesis/estimate predicts duration before synthesis
- **Frontend Integration**: SynthesisProgress component in chat interface
  - Animated progress bar with stage-specific colors (cyan for active, emerald for complete)
  - Human-readable time remaining (e.g., "About 15 seconds remaining")
  - Smooth transitions between stages with live ETA updates
  - Replaces with code block on completion
- **Production-Ready**: E2E tested with multiple synthesis scenarios, architect-approved

### T09 Domain Router Complete ✅
- **Math & Physics Solvers**: Aurora now solves mathematical and physics problems from English prompts
  - Math: Expression evaluation ("2+3*4" → 14.0), polynomial differentiation ("differentiate 3x^2" → "6x")
  - Physics: Orbital period calculations using Kepler's third law, EM field superposition
  - Domain classification automatically routes prompts to appropriate solver
- **API Endpoints**: Added /api/solve and /api/explain for direct problem solving
  - POST /api/solve with {"problem": "differentiate 3x^2+2x+5"} returns derivative
  - POST /api/explain provides both solution and explanation
- **Unit Conversion System**: Automatic normalization to SI units
  - /api/units endpoint converts any value with units (e.g., "7000 km" → 7,000,000 m)
  - Physics solver auto-detects units ("orbital period a=1 AU M=2e30 kg" works correctly)
  - Supports distance (km, miles, AU), mass (tons, pounds), time (hours, days, years)
- **Safe Evaluation**: AST-based expression parser prevents code injection
- **Comprehensive Testing**: 21 tests covering all math/physics operations

### T08 Language Router Complete ✅
- **Language Auto-Select**: Aurora now automatically selects Python/Go/Rust/C# based on prompt keywords
  - Go: Fast microservices, high-performance APIs (PORT env, default 8080)
  - Rust: Memory-safe CLI tools, system utilities (non-web service)
  - C#: Enterprise web APIs with Swagger/OpenAPI (PORT env, default 5080)
  - Python: Default for everything else (Flask apps, PORT env, default 8000)
- **Port Configuration**: All web services now use PORT environment variable for cloud deployment
  - Flask apps: `PORT=8000` (default)
  - Go services: `PORT=8080` (default)
  - C# WebAPIs: `PORT=5080` (default)
  - Fully compatible with Replit, Heroku, and other cloud platforms
- **Health Check Endpoint**: `/healthz` endpoint for service monitoring
  - Returns service status, version, and component health
  - Enables automatic restarts and uptime monitoring
  - Compatible with Cloudflare, Replit, and CI/CD pipelines
- **Offline Template Validation**: Test suite confirms all templates generate valid, runnable code
- **FastAPI Integration**: Language router fully integrated with `/api/chat` endpoint

### Aurora-X Ultra Implementation Complete
- **Baseline Comparisons**: Added --baseline CLI flag to compare against any previous run
- **Visual Regression Badges**: Red "REGRESSIONS ⚠ X" or green "No regressions ✓" badges in HTML reports
- **Makefile Targets**: compare-latest and compare-baseline for on-demand run comparisons
- **Graph Diff**: Automatic generation of graph_diff.json/html showing added/removed edges
- **Scores Diff**: Function-level regression tracking with scores_diff.json/html
- **Timestamp Tracking**: Full run_meta.json with start_ts, end_ts, duration_seconds

## System Architecture

### Frontend Architecture

**Technology Stack**: React 18 with TypeScript, leveraging Vite as the build tool for optimal development experience and production builds.

**UI Framework**: Shadcn/ui component library built on Radix UI primitives, providing accessible, unstyled components that are styled with Tailwind CSS. The design system follows a "New York" style variant with custom spacing, border radius, and color tokens.

**Routing**: Wouter for lightweight client-side routing with the following main pages:
- Home (`/`) - Chat interface for code generation requests
- Dashboard (`/dashboard`) - Real-time Aurora synthesis monitoring
- Library (`/library`) - Browse synthesized function library
- Corpus (`/corpus`) - Explore corpus learning data with advanced features:
  - Multi-criteria filtering (function name, perfect runs, score range, date range)
  - Offset-based pagination (25/50/100/200 records per page)
  - Similarity analysis showing why Aurora chose specific seed snippets
  - Real-time statistics (total records, perfect runs, average score)
  - Copy-to-clipboard for code snippets
- Settings (`/settings`) - Configure Aurora synthesis parameters

**State Management**: TanStack Query (React Query) for server state management with infinite stale time and disabled auto-refetch, optimized for a development environment where data changes are explicit.

**Design System**: Custom theme built on HSL color space with comprehensive dark mode support (primary theme). Features cinematic tech colors including JARVIS-inspired cyan (195 85% 55%) for AI activity, emerald for success states, amber for warnings, and purple for advanced features. Typography uses Inter for UI and JetBrains Mono for code snippets.

**Component Architecture**: Modular component structure with separation between UI primitives (`/components/ui`), feature components (`/components`), and page-level components (`/pages`). Each major feature has accompanying example components for documentation.

### Backend Architecture

**Framework**: Express.js server with TypeScript, using ESM modules throughout the codebase.

**API Design**: RESTful API with the following corpus-focused endpoints:
- `POST /api/corpus` - Accept new corpus entries from Aurora-X (API key protected)
- `GET /api/corpus` - Query corpus entries with advanced filtering:
  - Function name matching
  - Perfect runs only (passed == total)
  - Score range (min/max)
  - Date range (ISO 8601 timestamps)
  - Offset-based pagination with hasMore flag
- `GET /api/corpus/top` - Retrieve top-performing functions by name
- `GET /api/corpus/recent` - Fetch recent corpus entries
- `POST /api/corpus/similar` - Find similar functions using Jaccard similarity:
  - Signature matching (return type + arguments)
  - Bag-of-words Jaccard distance on post-conditions
  - Weighted scoring: 0.6 signature + 0.4 Jaccard + 0.1 perfect bonus

**Request Validation**: Zod schemas for runtime type validation on all API endpoints, ensuring data integrity between Aurora-X Python engine and TypeScript backend.

**Middleware Stack**:
- JSON body parsing for API requests
- Custom request/response logging with duration tracking
- Error handling middleware with consistent JSON error responses
- Vite development middleware (dev only) for HMR and asset serving

**Development Features**: 
- Replit-specific plugins for error overlays, cartographer integration, and dev banners (development environment only)
- Source maps enabled for debugging
- Hot Module Replacement through Vite middleware

### Data Storage Solutions

**Corpus Database**: SQLite (via better-sqlite3) with Write-Ahead Logging (WAL) enabled for concurrent read performance. The corpus storage layer tracks learning data from Aurora-X synthesis runs with advanced querying capabilities including multi-parameter filtering, similarity scoring (Jaccard distance on signatures and post-conditions), and offset-based pagination.

**Schema Design**: 
- Primary table: `corpus` with 18 fields tracking function synthesis metadata
- UUID primary keys for idempotent ingestion
- ISO 8601 timestamps for temporal queries
- JSON-serialized arrays for failing tests, function calls, and BOW tokens
- Computed fields: func_signature, complexity, sig_key for similarity matching

**Indexes**:
- `(spec_id, func_name)` - Fast lookups by specification and function
- `(sig_key)` - Enable signature-based similarity retrieval
- `(timestamp DESC)` - Temporal ordering for recent queries
- `(func_name, score, passed, total)` - Optimize best function queries

**User Storage**: In-memory storage implementation (MemStorage class) for user data during development. Prepared for database migration with interface-based design (IStorage).

**Migration Strategy**: Drizzle ORM configured for PostgreSQL migrations with schema defined in `shared/schema.ts`. Database credentials expected via `DATABASE_URL` environment variable.

### Authentication and Authorization

**API Security**: Header-based API key authentication for corpus ingestion endpoint (`x-api-key` header). Key stored in `AURORA_API_KEY` environment variable with fallback to development key.

**User Authentication**: Schema prepared for username/password authentication with Drizzle ORM user table including:
- UUID primary keys
- Unique username constraint
- Password field for hashed credentials

**Session Management**: Infrastructure in place for connect-pg-simple session store (referenced in dependencies), prepared for PostgreSQL-backed sessions.

### External Dependencies

**Aurora-X Integration**: The platform serves as the web interface for Aurora-X Ultra, a Python-based offline autonomous code synthesis engine. Aurora-X operates independently and posts synthesis results to Chango's corpus API when export is enabled via environment variables (`AURORA_EXPORT_ENABLED`, `AURORA_POST_URL`, `AURORA_API_KEY`).

**Anthropic AI SDK**: Integrated via `@anthropic-ai/sdk` package, likely for future LLM-powered features in the chat interface or code explanation capabilities.

**Database Providers**:
- Neon Serverless PostgreSQL driver (`@neondatabase/serverless`) for production database
- SQLite (`better-sqlite3`) for corpus storage and local development

**UI Component Dependencies**: Extensive Radix UI primitive collection for accessible, unstyled components including accordions, dialogs, dropdown menus, popovers, tooltips, and form controls.

**Build and Development Tools**:
- Vite for frontend bundling and development server
- esbuild for backend bundling in production builds
- tsx for TypeScript execution in development
- Tailwind CSS with PostCSS for styling

**Asset Management**: Custom alias (`@assets`) for attached assets directory, currently containing Aurora-X documentation and generated background images for the cinematic UI.