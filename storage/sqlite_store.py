import json
import sqlite3
from pathlib import Path


class SqliteStore:
    def __init__(self, path="data/aurora_proto.db"):
        self.path = Path(path)
        self.conn = None

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, ts REAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY, name TEXT, payload TEXT, ts REAL)"
        )
        self.conn.commit()

    def put_event(self, kind, payload):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO events (kind, payload, ts) VALUES (?,?,?)",
            (kind, json.dumps(payload), payload.get("ts", 0)),
        )
        self.conn.commit()

    def put_metric(self, name, payload):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO metrics (name, payload, ts) VALUES (?,?,?)",
            (name, json.dumps(payload), payload.get("ts", 0)),
        )
        self.conn.commit()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
