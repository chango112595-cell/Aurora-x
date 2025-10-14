# Chango - AI-Powered Autonomous Code Synthesis Platform

## Overview

Chango is a JARVIS-inspired web application that acts as the interface for Aurora-X Ultra, an offline autonomous code synthesis engine. It allows users to request complex code generation through a chat interface, monitor real-time synthesis progress, explore generated code libraries, and analyze corpus learning data. Designed with a cinematic tech aesthetic, Chango aims to provide a professional, developer-first experience for AI-assisted code generation, with ambitions for market potential as a leading autonomous code synthesis platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**January 2025 Updates**:
- **Enhanced CI/CD Pipeline**: 
  - Upgraded GitHub Actions workflow with SARIF output for GitHub Security tab integration
  - Coverage badge generation as SVG with color coding (red <60%, orange <80%, yellow <85%, green ≥85%)
  - Auto-publishing of coverage badge to separate 'badges' branch
  - Coverage calculation using lxml for accurate XML parsing
  - Added permissions for contents:write and security-events:write
- **PR Rollback Controls**: 
  - Added rollback endpoints to manage Aurora-generated pull requests
  - Dashboard UI integration with "Rollback Open PR" and "Revert Last Merged PR" buttons
  - Requires AURORA_GH_TOKEN environment variable with repo permissions
- **Coverage Badge**: Added coverage badge to README.md for real-time coverage visibility

**October 14, 2024 Updates**:
- **CI/CD Pipeline**: Added strict GitHub Actions workflow with 85% coverage requirement, Ruff linting, Bandit/Semgrep security gates
- **Dashboard Generate Button**: Integrated Generate button that creates PRs via Aurora Bridge with natural language prompts
- **GPG Signing Fixed**: Generated new GPG key for verified commits, properly configured with AURORA_GPG_PRIVATE secret
- **Aurora Chat Fixed**: Resolved natural language processing issues - Aurora now correctly handles English commands
- **PR Mode Integration**: Dashboard can create pull requests instead of direct pushes when AURORA_PR=1 is set
- **Security Configuration**: Added pytest.ini, ruff.toml, semgrep.yml for comprehensive code quality checks

**December 2024 Updates**:
- **COMPLETED T13**: Universal Code Synthesis Engine (UCSE) now at 100% completion
  - 1855-line synthesis engine with Multi-Intent Parser, Blueprint Engine, Dynamic Synthesizer, Safety Gate, and Persistence Layer
  - Supports 8 project types: UI/Frontend, API/Backend, AI/ML, Database, Fullstack, Library, CLI, Microservice
  - Generates complete projects with 10-12 files from natural language prompts
  - Creates downloadable ZIP archives for easy distribution
  - Fixed dashboard apiRequest bug for correct POST method invocation
  - End-to-end testing verified successful project generation and download
  - All quality gates passing (configuration, determinism, drift detection, seed validation)
- **COMPLETED T08**: Universal Code Intelligence now at 100% completion
  - Math & Physics Solver integrated into Aurora-X dashboard
  - Supports arithmetic evaluation, polynomial differentiation, and orbital period calculations
  - Secure AST-based expression parser (replaced eval() for security)
  - Accessible error handling with ARIA attributes for screen readers
  - API endpoints: /api/solve and /api/solve/pretty
  - All 7 unit tests passing
- **COMPLETED T10**: Cross-Platform Runtime (OS Matrix) now at 100% completion
  - Progressive Web App (PWA) support with offline caching capabilities
  - Service worker for caching key routes (/, /dashboard, /dashboard/progress)
  - PWA manifest with Aurora-X branding and standalone display mode
  - Multi-architecture Docker support (ARM64/AMD64) configured
  - Docker Compose deployment ready with health monitoring
  - Express endpoints: /manifest.webmanifest and /service-worker.js
- **COMPLETED T12**: Aurora Factory Protocol (Bridge) now at 100% completion
  - API bridge endpoints for natural language and spec compilation
  - Git integration with automatic commits and pushes
  - Discord webhook notifications for build status
  - Deploy functionality with Replit ping support
  - FastAPI endpoints: /api/bridge/nl, /api/bridge/spec, /api/bridge/deploy
  - Bridge test suite passing
  - Overall Aurora-X progress: 100% 🎉
- Implemented visual task dependency graph visualization with D3.js at /dashboard/graph endpoint
- Fixed dashboard rendering issue: Updated Task interface to handle numeric percent values from API
- Improved sidebar navigation with proper client-side routing using wouter Link components
- Made graph nodes editable - click any node to update task percentage directly
- Auto-refresh README badges - task updates automatically update progress badges
- Added /api/progress/recompute endpoint to regenerate MASTER_TASK_LIST.md, CSV, and badges
- Added `make progress-recompute` command for CLI access to recompute endpoint

## Bridge Protocol Enhancements

**Signed Commits Support (GPG Optional)**:
- **Environment Variables for Signing**:
  - `AURORA_SIGN=1` - Enable commit signing
  - `AURORA_GIT_EMAIL` - Git commit email (default: aurora@local)
  - `AURORA_GIT_NAME` - Git commit name (default: Aurora Bridge)
  - `GPG_KEY_ID` - GPG key ID for signing (optional)
  - `GPG_PRIVATE_ASC` - Armored ASCII GPG private key (optional)
- **Auto-Detection**: Signing is automatically enabled when environment variables are set
- **Verification**: Commits appear as "Verified" on GitHub when signed

**Preview & Diff Endpoints**:
- **GET /bridge/preview** - Preview files in generated ZIP without applying changes
- **GET /bridge/diff** - Get git diff statistics summary
- **GET /bridge/diff/full** - Get complete git diff
- **Purpose**: Review changes before creating PR to avoid surprises

**Makefile Helpers**:
- `make diff-full` - Show full git diff
- `make preview` - Preview latest generated project ZIP
- `make sign-on` - Enable commit signing
- `make sign-off` - Disable commit signing

**Natural Language Project Synthesis**:
- **New Endpoint**: `/api/bridge/nl/project` - Generate complete projects from natural language prompts
  - **Parameters**:
    - `prompt` (string): Natural language description of the desired project
    - `repo` (string): Target repository name for generated code
    - `stack` (string): Technology stack to use (e.g., "react", "vue", "python", "golang")
    - `mode` (string): Generation mode ("create" for new projects, "enhance" for existing)
  - **Example**: POST request with `{"prompt": "Build a todo app", "repo": "todo-app", "stack": "react", "mode": "create"}`

**GitHub Pull Request Integration**:
- **Automatic PR Creation**: Bridge now supports creating pull requests with generated code
- **GitHub Integration Features**:
  - Automatic branch creation for new features
  - Commit messages generated from synthesis context
  - PR descriptions with implementation details
  - Direct push to configured repositories
- **Required Environment Variables**:
  - `GITHUB_TOKEN`: Personal access token for GitHub API authentication
  - `AURORA_GIT_URL`: Target repository URL (e.g., `https://github.com/username/repo.git`)
  - `AURORA_GIT_BRANCH`: Default branch for pushes (e.g., `main` or `develop`)

**PR Rollback Controls** (Added January 2025):
- **New Rollback Endpoints**:
  - `/api/bridge/rollback/open`: Closes the latest open PR with 'aurora' label and deletes its branch
  - `/api/bridge/rollback/merged`: Creates a revert PR for the latest merged PR with 'aurora' label
- **Dashboard UI Integration**:
  - New "PR Rollback Controls" section added to dashboard
  - "Rollback Open PR" button to close and delete branch
  - "Revert Last Merged PR" button to create revert PR
- **Required Environment Variables**:
  - `AURORA_GH_TOKEN`: GitHub Personal Access Token with repo permissions (for rollback operations)
  - `AURORA_REPO`: Repository identifier (e.g., `chango112595-cell/Aurora-x`)
  - `AURORA_BRIDGE_URL`: Bridge service URL (defaults to `http://localhost:5001`)

**Quality Gates and CI/CD**:
- **Makefile Quality Targets**:
  - `make lint`: Run code linting and static analysis
  - `make sec`: Execute security vulnerability scanning
  - `make cov`: Generate code coverage reports
  - `make gates`: Run all quality gates in sequence
- **GitHub Actions Workflow**:
  - Automatic CI pipeline on push and pull requests
  - Runs all quality gates before allowing merge
  - Multi-architecture Docker builds (ARM64/AMD64)
  - Health checks and rollback on deployment failures
  - Test results published as GitHub annotations

**Usage Guide**:
- **Using the nl-pr Target**: 
  ```bash
  # Generate code and create a pull request from natural language
  make nl-pr PROMPT="Create a REST API for user management" REPO="user-api" STACK="python"
  
  # This command will:
  # 1. Call the /api/bridge/nl/project endpoint
  # 2. Generate the complete project structure
  # 3. Run quality gates (lint, security, coverage)
  # 4. Create a new branch
  # 5. Commit the generated code
  # 6. Push to GitHub
  # 7. Create a pull request with description
  ```

- **Environment Setup**:
  ```bash
  # Set required environment variables
  export GITHUB_TOKEN="ghp_your_token_here"
  export AURORA_GIT_URL="https://github.com/yourusername/yourrepo.git"
  export AURORA_GIT_BRANCH="main"
  
  # Verify configuration
  make bridge-config
  ```

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