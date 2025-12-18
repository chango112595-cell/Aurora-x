# Aurora-X Ultra - AI-Powered Autonomous Code Synthesis Platform

## Overview
Aurora-X Ultra is an AI-powered autonomous code synthesis engine inspired by JARVIS. It features a sophisticated architecture with 188 intelligence tiers, 66 advanced execution methods, and 550 hybrid mode modules, enabling hyperspeed code generation. The platform offers a chat interface for requesting complex code, monitoring synthesis progress, exploring generated code libraries, and analyzing corpus learning data. The system operates with an "Always-On Nexus," automatically activating an embedded mode if external services are unavailable, ensuring continuous operation.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The frontend uses React 18 with Vite, TypeScript, and Wouter for routing. The UI/UX is built with Shadcn/ui (Radix UI + Tailwind CSS) using a "New York" style variant. TanStack Query is used for server state management.

### Technical Implementations
- **Core AI**: Aurora Chat AI with 10-turn conversation memory and autonomous code synthesis capabilities.
- **Backend**: Express.js with TypeScript and ESM modules, providing a RESTful API for corpus management, real-time synthesis, and domain-specific problem solving.
- **Data Storage**: SQLite (better-sqlite3) with WAL for function synthesis metadata for local development, and Drizzle ORM configured for PostgreSQL migrations for production.
- **Autonomous Core**: Aurora Nexus V3, referred to as the "Universal Consciousness System," orchestrates 300 autonomous workers and integrates 188 tiers, 66 Advanced Execution Methods, and 550 Cross-Temporal Modules. It includes self-healing capabilities, issue detection, and task dispatching.
- **Security**: ASE-∞ Vault provides multi-layer secret encryption (22-layer default) using multiple algorithms (AES-GCM, ChaCha20-Poly1305, NaCl SecretBox, Chaotic XOR), Argon2id key stretching, and machine fingerprinting.
- **Edge Runtimes**: Aurora EdgeOS Runtimes (PACK 3B-3J) support various domains (Automotive, Aviation, IoT, etc.) with both offline and cloud-assisted modes, utilizing a companion-computer pattern with human-signed approval for critical operations.
- **Production Pipeline**: Phase-1 Production Bundle includes a complete autonomy system for module generation, inspection, testing, and promotion, supporting universal cross-platform deployment and GPU acceleration.

### Feature Specifications
- **Grandmaster Tiers (188)**: Foundational and Grandmaster Skills categories.
- **Advanced Execution Methods (66)**: Including Sequential, Parallel, Speculative, Adversarial, Self-Reflective, and Hybrid.
- **Cross-Temporal Modules (550)**: Ranging from "Ancient" to "Futuristic" tools, some with GPU support.
- **Hyperspeed Mode**: Capable of processing 1,000+ code units in under 0.001 seconds.
- **Hybrid Parallel Execution**: Combines Task, Data, Pipeline, and Agent parallelism.
- **Autonomous Workers (300)**: Non-conscious task executors for fixing, coding, and analysis.

### System Design Choices
The architecture emphasizes modularity, autonomy, and resilience. The "Always-On Nexus" design ensures continuous operation even when external dependencies are temporarily unavailable. The system integrates various "PACK Systems" and controllers for comprehensive functionality and self-management.

## External Dependencies
- **AI Engine**: Aurora-X Ultra (Python-based autonomous code synthesis engine)
- **Databases**: Neon Serverless PostgreSQL, SQLite (better-sqlite3)
- **UI Components**: Radix UI
- **Build Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS
