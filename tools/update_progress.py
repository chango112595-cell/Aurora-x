import json, sys, csv
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / "progress.json"
MD = ROOT / "MASTER_TASK_LIST.md"
CSV = ROOT / "progress_export.csv"

def render_md(data: dict) -> str:
    lines = []
    lines.append("# AURORA-X ULTRA — MASTER TASK LIST\n")
    lines.append(f"_Last update (UTC): {data.get('updated_utc','')}_" + "\n")
    lines.append("| Phase | Task | Status | % | Notes |")
    lines.append("|------:|------|--------|---:|-------|")
    for t in data["tasks"]:
        notes = " • ".join((t.get("notes") or [])[:2])
        lines.append(f"| **{t['id']}** | {t['name']} | {t['status']} | {t['percent']} | {notes} |")
    lines.append("\n## Active Now\n")
    lines.append("- " + ", ".join(data.get("active", [])))
    lines.append("\n## Rules\n")
    for r in data.get("rules", []):
        lines.append(f"- {r}")
    return "\n".join(lines)

def export_csv(data: dict):
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","name","percent","status","category"])
        for t in data["tasks"]:
            w.writerow([t["id"], t["name"], t["percent"], t["status"], t.get("category","")])

def main(argv=None):
    data = json.loads(PROG.read_text(encoding="utf-8"))
    data["updated_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    PROG.write_text(json.dumps(data, indent=2), encoding="utf-8")
    MD.write_text(render_md(data), encoding="utf-8")
    export_csv(data)
    print("[OK] Updated MASTER_TASK_LIST.md and progress_export.csv")

if __name__ == "__main__":
    main()