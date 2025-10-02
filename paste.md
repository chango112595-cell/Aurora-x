# Aurora Run Metadata Telemetry System

## Overview
Implemented a complete telemetry tracking system for Aurora-X synthesis runs in the Chango platform. This system captures and displays seeding configurations and tracks which corpus entries were used as seeds during synthesis.

## Implementation Details

### 1. Database Schema
Added two new SQLite tables to track run metadata and seed usage:

**run_meta table:**
- `run_id` (TEXT PRIMARY KEY) - Unique identifier for each synthesis run
- `timestamp` (TEXT) - ISO 8601 timestamp of the run
- `seed_bias` (REAL) - Bias value for seeding (0.0 to 0.5)
- `seeding_enabled` (INTEGER) - Boolean flag for seeding status
- `max_iters` (INTEGER) - Maximum iterations for synthesis
- `beam` (INTEGER, optional) - Beam search width
- `notes` (TEXT, optional) - Additional run notes

**used_seeds table:**
- `id` (TEXT PRIMARY KEY) - Auto-generated UUID
- `run_id` (TEXT) - Reference to the parent run
- `function` (TEXT) - Name of the synthesized function
- `source_id` (TEXT, optional) - ID of the corpus entry used as seed
- `reason_json` (TEXT, optional) - JSON-encoded reasoning for seed selection
- `score` (REAL, optional) - Seed quality score
- `passed` (INTEGER, optional) - Number of passing tests
- `total` (INTEGER, optional) - Total number of tests
- `snippet` (TEXT, optional) - The actual seed code snippet
- `timestamp` (TEXT) - When the seed was used

### 2. API Endpoints

**POST /api/run-meta**
- Protected by x-api-key header authentication
- Accepts RunMeta schema with synthesis configuration
- Stores run metadata when Aurora starts a synthesis session

**GET /api/run-meta/latest**
- Returns the most recent synthesis run metadata
- Used by UI to display current run configuration

**POST /api/used-seeds**
- Protected by x-api-key header authentication
- Records when Aurora selects a corpus entry as a seed
- Includes reasoning, similarity scores, and code snippets

**GET /api/used-seeds**
- Query parameters: `run_id` (optional), `limit` (default: 200)
- Returns list of seeds used in synthesis runs
- Automatically parses JSON reason field

### 3. React UI Component

**RunStatus Component:**
- Displays latest run configuration (seed bias, max iterations, beam width)
- Shows all seeds used in the current run with:
  - Function name and timestamp
  - Source corpus entry ID
  - Similarity score and test results
  - Selection reasoning (why Aurora chose this seed)
  - Code snippet with copy-to-clipboard functionality
- Handles loading and empty states gracefully
- Integrated into the Corpus Explorer page

### 4. Type Safety
- Added Zod schemas for RunMeta and UsedSeed types
- Full TypeScript types throughout backend and frontend
- Proper validation on all API endpoints

## Testing
Successfully tested all endpoints with curl:
```bash
# Create run metadata
curl -X POST http://localhost:5000/api/run-meta \
  -H "x-api-key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"run_id": "test-run-001", "timestamp": "2025-10-02T09:20:00.000Z", 
       "seed_bias": 0.25, "seeding_enabled": true, "max_iters": 100, "beam": 5}'

# Record used seed
curl -X POST http://localhost:5000/api/used-seeds \
  -H "x-api-key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"run_id": "test-run-001", "function": "quick_sort", 
       "reason": {"similarity": 0.92, "method": "jaccard"}, 
       "score": 0.88, "snippet": "def quick_sort(arr):..."}'

# Retrieve latest run info
curl http://localhost:5000/api/run-meta/latest

# Get seeds for a specific run
curl http://localhost:5000/api/used-seeds?run_id=test-run-001
```

## Integration with Aurora-X
Aurora-X can now POST telemetry data to these endpoints when:
1. A synthesis run begins (POST to /api/run-meta)
2. A seed is selected from the corpus (POST to /api/used-seeds)

Required environment variables on Aurora-X side:
- `AURORA_EXPORT_ENABLED=true`
- `AURORA_POST_URL=http://chango-url/api`
- `AURORA_API_KEY=<secure-key>`

## Files Modified
- `shared/schema.ts` - Added RunMeta and UsedSeed schemas
- `server/corpus-storage.ts` - Added database tables and storage methods
- `server/routes.ts` - Added four new API endpoints
- `client/src/components/run-status.tsx` - New component for displaying run status
- `client/src/pages/corpus.tsx` - Integrated RunStatus component

## Security
- API endpoints protected with same x-api-key authentication as existing corpus endpoints
- Environment variable `AURORA_API_KEY` controls access (defaults to dev key)
- No sensitive data exposed in GET endpoints

## Next Steps for Aurora-X Integration
Aurora-X Python code should:
1. Track run configuration when synthesis starts
2. POST to `/api/run-meta` with run parameters
3. When selecting seeds from corpus, POST to `/api/used-seeds` with:
   - The function being synthesized
   - Source corpus entry ID
   - Similarity/selection metrics
   - The actual code snippet used
4. Include reasoning data to help understand Aurora's learning patterns