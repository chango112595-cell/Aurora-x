
#!/usr/bin/env python3
"""Check Aurora-X database health."""
import sqlite3
from pathlib import Path

def check_corpus_db():
    """Check corpus database health."""
    db_path = Path("data/corpus.db")
    
    if not db_path.exists():
        print("⚠️  corpus.db does not exist")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='corpus'")
        if not cursor.fetchone():
            print("❌ corpus table missing")
            return False
        
        # Count entries
        cursor.execute("SELECT COUNT(*) FROM corpus")
        count = cursor.fetchone()[0]
        print(f"✅ corpus.db healthy with {count} entries")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_corpus_db()
