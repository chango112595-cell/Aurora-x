# Chango - Aurora-X Web Interface Project

## Project Overview
Chango is a TypeScript/React web application serving as the telemetry and monitoring interface for Aurora-X Ultra, an offline autonomous code synthesis engine. Features a JARVIS-inspired cinematic tech aesthetic with real-time synthesis monitoring, corpus exploration, and learning data analysis.

## Tech Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Shadcn/ui, Wouter
- **Backend**: Express.js, TypeScript, SQLite (better-sqlite3)
- **Data**: TanStack Query, Drizzle ORM (prepared), Zod validation
- **UI**: Radix UI primitives, Lucide icons, Framer Motion

## Project Structure
```
.
├── client/
│   └── src/
│       ├── components/
│       │   ├── ui/           # Shadcn UI components
│       │   ├── aurora-status.tsx
│       │   ├── synthesis-progress.tsx
│       │   ├── code-preview.tsx
│       │   ├── run-status.tsx
│       │   └── sidebar.tsx
│       ├── pages/
│       │   ├── home.tsx     # Chat interface
│       │   ├── dashboard.tsx # Aurora monitoring
│       │   ├── corpus.tsx   # Corpus explorer
│       │   ├── library.tsx  # Function library
│       │   └── settings.tsx # Configuration
│       ├── lib/
│       │   └── queryClient.ts
│       ├── App.tsx
│       └── main.tsx
├── server/
│   ├── index.ts             # Express server
│   ├── routes.ts            # API endpoints
│   ├── corpus-storage.ts    # SQLite corpus manager
│   └── storage.ts           # User storage interface
├── shared/
│   └── schema.ts            # Type definitions
├── data/
│   └── corpus.db            # SQLite database
└── attached_assets/         # Documentation & images

## Key Configuration Files
├── package.json             # Dependencies
├── vite.config.ts          # Vite bundler config
├── tailwind.config.ts      # Tailwind CSS config
├── tsconfig.json           # TypeScript config
├── drizzle.config.ts       # Database migrations
└── replit.md               # Project documentation
```

## Database Schema

### corpus table
```sql
CREATE TABLE corpus(
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  spec_id TEXT NOT NULL,
  spec_hash TEXT NOT NULL,
  func_name TEXT NOT NULL,
  func_signature TEXT NOT NULL,
  passed INTEGER NOT NULL,
  total INTEGER NOT NULL,
  score REAL NOT NULL,
  failing_tests TEXT NOT NULL,
  snippet TEXT NOT NULL,
  complexity INTEGER,
  iteration INTEGER,
  calls_functions TEXT,
  sig_key TEXT,
  post_bow TEXT,
  duration_ms INTEGER,
  synthesis_method TEXT
);
```

### run_meta table
```sql
CREATE TABLE run_meta(
  run_id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  seed_bias REAL NOT NULL,
  seeding_enabled INTEGER NOT NULL,
  max_iters INTEGER NOT NULL,
  beam INTEGER,
  notes TEXT
);
```

### used_seeds table
```sql
CREATE TABLE used_seeds(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  function TEXT NOT NULL,
  source_id TEXT,
  reason_json TEXT,
  score REAL,
  passed INTEGER,
  total INTEGER,
  snippet TEXT,
  timestamp TEXT NOT NULL
);
```

## API Endpoints

### Corpus Management
- `GET /api/corpus` - Query entries with filters
  - Query params: func, limit, offset, perfectOnly, minScore, maxScore, startDate, endDate
- `GET /api/corpus/top` - Get top functions by name
- `GET /api/corpus/recent` - Get recent entries
- `POST /api/corpus/similar` - Find similar functions

### Telemetry (Currently Disabled)
- `POST /api/corpus` - Ingest new corpus entry (disabled)
- `POST /api/run-meta` - Record run metadata (disabled)
- `GET /api/run-meta/latest` - Get latest run (disabled)
- `POST /api/used-seeds` - Record seed usage (disabled)
- `GET /api/used-seeds` - Get seeds by run_id (disabled)

## Core Implementation Files

### server/corpus-storage.ts
- CorpusStorage class managing SQLite database
- Methods: insertEntry, getEntries, getTopByFunc, getRecent, getSimilar
- Similarity scoring: Jaccard distance on signatures and post-conditions
- Weighted scoring: 0.6 signature + 0.4 Jaccard + 0.1 perfect bonus

### server/routes.ts
- Express route definitions
- API key authentication (x-api-key header)
- Zod schema validation
- Error handling middleware

### client/src/pages/corpus.tsx
- Main corpus exploration interface
- Advanced filtering: function name, score range, date range, perfect runs
- Offset-based pagination (25/50/100/200 per page)
- Similarity analysis panel
- Statistics display (total records, perfect runs, average score)
- Copy-to-clipboard for code snippets

### client/src/components/run-status.tsx
- Displays latest synthesis run configuration
- Shows seed usage and selection reasons
- Real-time telemetry visualization

## Environment Variables
```bash
AURORA_API_KEY=dev-key-change-in-production  # API key for Aurora-X authentication
DATABASE_URL=<postgresql_url>                # PostgreSQL for production (optional)
```

## How to Run
```bash
npm install          # Install dependencies
npm run dev          # Start development server (port 5000)
```

## Aurora-X Integration

### From Aurora-X Side (Python)
1. Set environment variables:
   ```bash
   AURORA_EXPORT_ENABLED=1
   AURORA_POST_URL=http://localhost:5000
   AURORA_API_KEY=dev-key-change-in-production
   ```

2. Aurora-X POSTs to Chango endpoints:
   - Corpus entries → `/api/corpus`
   - Run metadata → `/api/run-meta`
   - Seed usage → `/api/used-seeds`

### From Chango Side (TypeScript)
1. Receives telemetry data via API endpoints
2. Stores in SQLite database
3. Displays in UI components
4. Provides querying and analysis tools

## Design System

### Color Scheme (Dark Mode Primary)
- Primary: JARVIS cyan (195 85% 55%) - AI activity
- Success: Emerald - successful operations
- Warning: Amber - alerts
- Destructive: Red - errors
- Purple: Advanced features
- Background: Dark with elevated surfaces

### Typography
- UI: Inter font family
- Code: JetBrains Mono

### Components
- Shadcn/ui New York style variant
- Radix UI primitives for accessibility
- Custom hover/active elevations
- Cinematic tech aesthetic throughout

## Current Status
- ✅ Corpus database and querying complete
- ✅ Telemetry endpoints implemented
- ✅ UI components for corpus exploration
- ✅ Similarity analysis working
- ⚠️ Telemetry disabled (commented out in routes.ts)
- 🔜 Ready for Aurora-X integration when re-enabled

## To Re-enable Telemetry
1. Uncomment telemetry endpoints in `server/routes.ts`
2. Restart the server
3. Configure Aurora-X with correct environment variables
4. Aurora-X will start posting data to Chango

## Notes
- Chango is the TypeScript/React web interface
- Aurora-X is a separate Python synthesis engine project
- Communication happens via HTTP POST with API key auth
- All data stored locally in SQLite database
- No external dependencies or API calls required