#!/bin/bash
# Daily snapshot cron job for Aurora-X
# Add to crontab: 0 0 * * * /path/to/cron_snapshot.sh

set -e

# Configuration
AURORA_HOME="${AURORA_HOME:-$(pwd)}"
SNAPSHOT_DIR="${AURORA_HOME}/.aurora/snapshots"
RETENTION_DAYS=30

# Create snapshot directory
mkdir -p "${SNAPSHOT_DIR}"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_STR=$(date +%Y-%m-%d)

echo "=================================================="
echo "Aurora-X Daily Snapshot - ${DATE_STR}"
echo "=================================================="

# 1. Backup seeds.json
if [ -f "${AURORA_HOME}/.aurora/seeds.json" ]; then
    cp "${AURORA_HOME}/.aurora/seeds.json" \
       "${SNAPSHOT_DIR}/seeds_${TIMESTAMP}.json"
    echo "✅ Backed up seeds.json"
else
    echo "⚠️  No seeds.json found"
fi

# 2. Backup corpus database
if [ -f "${AURORA_HOME}/.aurora/corpus.db" ]; then
    cp "${AURORA_HOME}/.aurora/corpus.db" \
       "${SNAPSHOT_DIR}/corpus_${TIMESTAMP}.db"
    echo "✅ Backed up corpus.db"
else
    echo "⚠️  No corpus.db found"
fi

# 3. Backup progress.json
if [ -f "${AURORA_HOME}/progress.json" ]; then
    cp "${AURORA_HOME}/progress.json" \
       "${SNAPSHOT_DIR}/progress_${TIMESTAMP}.json"
    echo "✅ Backed up progress.json"
fi

# 4. Generate stats report
python3 - <<EOF
import json
from pathlib import Path
import sys

sys.path.insert(0, "${AURORA_HOME}")

try:
    from aurora_x.learn import get_seed_store
    
    store = get_seed_store()
    summary = store.get_summary()
    
    stats = {
        "timestamp": "${TIMESTAMP}",
        "date": "${DATE_STR}",
        "seed_stats": {
            "total_seeds": summary["total_seeds"],
            "avg_bias": summary.get("avg_bias", 0),
            "max_bias": summary.get("max_bias", 0),
            "min_bias": summary.get("min_bias", 0),
            "total_updates": summary.get("total_updates", 0)
        }
    }
    
    stats_path = Path("${SNAPSHOT_DIR}/stats_${TIMESTAMP}.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✅ Generated stats report: {stats['seed_stats']['total_seeds']} seeds")
except Exception as e:
    print(f"⚠️  Stats generation failed: {e}")
EOF

# 5. Clean old snapshots
echo ""
echo "Cleaning snapshots older than ${RETENTION_DAYS} days..."
find "${SNAPSHOT_DIR}" -type f -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# 6. Count current snapshots
COUNT=$(ls -1 "${SNAPSHOT_DIR}" 2>/dev/null | wc -l)
echo "✅ Total snapshots: ${COUNT}"

echo ""
echo "=================================================="
echo "Snapshot completed: ${SNAPSHOT_DIR}"
echo "=================================================="