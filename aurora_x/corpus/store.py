from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]+")
TYPE_CANON = {"int":"I","float":"F","number":"N","str":"S","string":"S","bool":"B","list":"L","list[int]":"L[I]","list[float]":"L[F]","Any":"A"}

def now_iso() -> str: return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
def short_id(s: str) -> str: return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]
def spec_digest(text: str) -> dict[str, str]:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {"spec_hash": h, "spec_id": h[:12]}

def normalize_signature(sig: str) -> str:
    try:
        name, rest = sig.split("(", 1)
        args_s, ret_s = rest.split(")->")
        args_s = args_s.rstrip(")")
        def canon(t: str) -> str: return TYPE_CANON.get(t.strip(), t.strip())
        arg_types: list[str] = []
        if args_s.strip():
            for a in args_s.split(","):
                if ":" in a: _, t = a.split(":"); arg_types.append(canon(t.strip()))
                else: arg_types.append("A")
        ret = canon(ret_s.strip())
        return f"{name.strip()}({','.join(arg_types)})->{ret}"
    except Exception: return sig

def tokenize_post(post_list: list[str]) -> list[str]:
    toks: list[str] = []
    for p in (post_list or []):
        for w in WORD.findall(p.lower()):
            if len(w) >= 2: toks.append(w)
    return toks

@dataclass
class CorpusPaths:
    root: Path
    jsonl: Path
    sqlite: Path

def paths(run_root: Path) -> CorpusPaths:
    r = Path(run_root); r.mkdir(parents=True, exist_ok=True)
    return CorpusPaths(root=r, jsonl=r/"corpus.jsonl", sqlite=r/"corpus.db")

def _open_sqlite(dbp: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(dbp)); conn.row_factory = sqlite3.Row
    conn.executescript("""
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS corpus (
      id TEXT PRIMARY KEY, timestamp TEXT,
      spec_id TEXT, spec_hash TEXT,
      func_name TEXT, func_signature TEXT, sig_key TEXT,
      passed INTEGER, total INTEGER, score REAL,
      failing_tests TEXT, snippet TEXT, complexity INTEGER,
      iteration INTEGER, calls_functions TEXT, post_bow TEXT
    );
    """)
    return conn

def record(run_root: Path, entry: dict[str, Any]) -> None:
    p = paths(run_root)
    try:
        rec = {**entry}
        rec.setdefault("id", str(uuid.uuid4()))
        rec.setdefault("timestamp", now_iso())
        if "sig_key" not in rec and "func_signature" in rec:
            rec["sig_key"] = normalize_signature(rec["func_signature"])
        if "post_bow" not in rec and isinstance(rec.get("post_conditions"), list):
            rec["post_bow"] = tokenize_post(rec["post_conditions"])
        with p.jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        conn = _open_sqlite(p.sqlite)
        with conn:
            conn.execute("""INSERT OR REPLACE INTO corpus
                (id,timestamp,spec_id,spec_hash,func_name,func_signature,sig_key,passed,total,score,failing_tests,snippet,complexity,iteration,calls_functions,post_bow)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rec.get("id"), rec.get("timestamp"), rec.get("spec_id"), rec.get("spec_hash"),
                 rec.get("func_name"), rec.get("func_signature"), rec.get("sig_key"),
                 int(rec.get("passed",0)), int(rec.get("total",0)), float(rec.get("score",0.0)),
                 json.dumps(rec.get("failing_tests")), rec.get("snippet"), rec.get("complexity"),
                 rec.get("iteration"), json.dumps(rec.get("calls_functions")), json.dumps(rec.get("post_bow"))))
    except Exception: return

def retrieve(run_root: Path, signature: str, k: int = 10) -> list[dict[str, Any]]:
    """Retrieve corpus entries matching signature, ordered by score."""
    p = paths(run_root)
    if not p.sqlite.exists():
        return []

    sig_key = normalize_signature(signature)
    conn = _open_sqlite(p.sqlite)

    try:
        # Query by signature key
        rows = conn.execute("""
            SELECT * FROM corpus
            WHERE sig_key = ?
            ORDER BY score DESC, passed DESC
            LIMIT ?
        """, (sig_key, k)).fetchall()

        results = []
        for row in rows:
            d = dict(row)
            # Parse JSON fields
            if d.get("failing_tests"):
                try: d["failing_tests"] = json.loads(d["failing_tests"])
                except (json.JSONDecodeError, TypeError): pass
            if d.get("calls_functions"):
                try: d["calls_functions"] = json.loads(d["calls_functions"])
                except (json.JSONDecodeError, TypeError): pass
            if d.get("post_bow"):
                try: d["post_bow"] = json.loads(d["post_bow"])
                except (json.JSONDecodeError, TypeError): pass
            results.append(d)

        return results
    finally:
        conn.close()
