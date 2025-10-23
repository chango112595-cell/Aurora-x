from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / "progress.json"
README = ROOT / "README.md"

BADGE_START = "<!-- AURORA_PROGRESS_BADGES:START -->"
BADGE_END = "<!-- AURORA_PROGRESS_BADGES:END -->"


def compute(data: dict):
    tasks = data.get("tasks", [])
    overall = round(sum(t.get("percent", 0) for t in tasks) / max(1, len(tasks)), 2)
    active = ", ".join(data.get("active", []))
    ts = data.get("updated_utc", "")
    return overall, active, ts


def render_block(overall: float, active: str, ts: str) -> str:
    return f"""{BADGE_START}
<p>
  <img alt="Overall Progress" src="https://img.shields.io/badge/Overall-{overall}%25-7D5BFF?style=for-the-badge" />
  <img alt="Active" src="https://img.shields.io/badge/Active-{active.replace(' ','%20')}-66E6FF?style=for-the-badge" />
  <img alt="Updated" src="https://img.shields.io/badge/Updated-{ts.replace(':','%3A')}-32325D?style=for-the-badge" />
</p>
{BADGE_END}"""


def main(argv=None):
    if not PROG.exists():
        print("progress.json missing", file=sys.stderr)
        sys.exit(1)
    data = json.loads(PROG.read_text(encoding="utf-8"))
    data["updated_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    PROG.write_text(json.dumps(data, indent=2), encoding="utf-8")

    overall, active, ts = compute(data)
    block = render_block(overall, active or "—", ts)

    if README.exists():
        content = README.read_text(encoding="utf-8")
    else:
        content = "# Aurora-X\n"

    if BADGE_START in content and BADGE_END in content:
        pattern = re.compile(re.escape(BADGE_START) + r".*?" + re.escape(BADGE_END), re.S)
        content = pattern.sub(block, content)
    else:
        content = block + "\n\n" + content

    README.write_text(content, encoding="utf-8")
    print("[OK] README badges updated")


if __name__ == "__main__":
    main()
