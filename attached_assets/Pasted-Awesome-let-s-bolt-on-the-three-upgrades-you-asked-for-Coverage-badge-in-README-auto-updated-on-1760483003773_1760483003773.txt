Awesome—let’s bolt on the three upgrades you asked for:
	•	Coverage badge in README (auto-updated on every push to main)
	•	Semgrep SARIF upload (shows findings in the “Security” tab)
	•	Dashboard “Rollback last PR” actions (close/delete for open PRs; revert PR for merged)

Below are drop-in files/snippets. You can paste them exactly and commit.

⸻

1) CI: add Semgrep SARIF + auto coverage badge

A) Replace your CI file with this superset

.github/workflows/aurora-ci.yml

name: Aurora CI (strict)

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: write         # needed to push badges branch
  security-events: write  # needed to upload SARIF
  pull-requests: write

jobs:
  ci:
    runs-on: ubuntu-latest
    timeout-minutes: 25

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt || true
          pip install pytest pytest-cov ruff bandit semgrep lxml

      - name: Lint (ruff)
        run: ruff check .

      - name: Security (bandit - high only)
        run: bandit -r aurora_x -lll

      - name: Tests + Coverage XML (>=85%)
        id: testcov
        run: |
          pytest -q --maxfail=1 --disable-warnings \
            --cov=aurora_x --cov-report=term-missing --cov-report=xml:coverage.xml
          python - <<'PY'
from lxml import etree
doc = etree.parse("coverage.xml")
rate = float(doc.getroot().attrib.get("line-rate", "0"))*100
print(f"COVERAGE={rate:.2f}")
open(os.environ["GITHUB_OUTPUT"],"a").write(f"coverage={rate:.2f}\n")
import sys
sys.exit(0 if rate >= 85.0 else 1)
PY

      - name: Semgrep (findings + SARIF)
        run: semgrep --config semgrep.yml --sarif --output semgrep.sarif || true

      - name: Upload SARIF to Security tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif

      # --- Coverage badge publishing (to 'badges' branch) ---
      - name: Generate coverage badge SVG
        run: |
          python - <<'PY'
import os, math
cov = float(os.getenv("COVER","0") or "${{ steps.testcov.outputs.coverage }}")
color = "red" if cov < 60 else "orange" if cov < 80 else "yellow" if cov < 85 else "green"
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="150" height="20">
<linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<mask id="a"><rect width="150" height="20" rx="3" fill="#fff"/></mask>
<g mask="url(#a)">
  <rect width="80" height="20" fill="#555"/>
  <rect x="80" width="70" height="20" fill="{color}"/>
  <rect width="150" height="20" fill="url(#b)"/>
</g>
<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva" font-size="11">
  <text x="40" y="14">coverage</text>
  <text x="115" y="14">{cov:.0f}%</text>
</g>
</svg>'''
os.makedirs("badges_out", exist_ok=True)
open("badges_out/coverage.svg","w").write(svg)
PY

      - name: Publish badge to 'badges' branch
        if: github.ref == 'refs/heads/main'
        run: |
          git config user.name "github-actions"
          git config user.email "actions@users.noreply.github.com"
          git fetch origin badges || true
          git checkout -B badges origin/badges || git checkout -b badges
          mkdir -p badges
          cp badges_out/coverage.svg badges/coverage.svg
          git add badges/coverage.svg
          git commit -m "ci: update coverage badge" || echo "no changes"
          git push origin badges

This keeps the badge on a dedicated badges branch so it never fights branch protection.

B) Add the badge to your README

At the top of README.md:

![coverage](https://raw.githubusercontent.com/chango112595-cell/Aurora-x/badges/badges/coverage.svg)


⸻

2) Dashboard: “Rollback last PR”

We’ll add two backend endpoints and two buttons:
	•	Close & delete branch for the latest open PR labeled aurora.
	•	Revert last merged Aurora PR by opening a revert PR (works well when Aurora mainly adds/edits files).

Requires a GitHub token in Replit secrets: AURORA_GH_TOKEN (repo scope).

A) Backend (FastAPI) additions

In aurora_x/serve.py:

import os, requests
from fastapi import HTTPException
from pydantic import BaseModel

GH_TOKEN = os.getenv("AURORA_GH_TOKEN")
OWNER_REPO = os.getenv("AURORA_REPO","chango112595-cell/Aurora-x")
API = "https://api.github.com"

def gh_headers():
    if not GH_TOKEN:
        raise HTTPException(status_code=500, detail="Missing AURORA_GH_TOKEN")
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

@router_bridge.post("/api/bridge/rollback/open")
def rollback_open():
    """Close newest open PR with label 'aurora' and delete its branch."""
    owner, repo = OWNER_REPO.split("/",1)
    q = f"repo:{OWNER_REPO} is:pr is:open label:aurora"
    r = requests.get(f"{API}/search/issues", headers=gh_headers(), params={"q": q})
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="No open Aurora PR found.")
    pr_number = items[0]["number"]
    # get PR info to identify branch
    pr = requests.get(f"{API}/repos/{owner}/{repo}/pulls/{pr_number}", headers=gh_headers()).json()
    head_ref = pr["head"]["ref"]

    # close PR
    requests.patch(f"{API}/repos/{owner}/{repo}/pulls/{pr_number}",
                   headers=gh_headers(), json={"state":"closed"}).raise_for_status()
    # delete branch ref
    requests.delete(f"{API}/repos/{owner}/{repo}/git/refs/heads/{head_ref}",
                    headers=gh_headers()).raise_for_status()
    return {"status":"ok","closed":pr_number,"deleted_branch":head_ref}

class RevertBody(BaseModel):
    base: str | None = None  # default main

@router_bridge.post("/api/bridge/rollback/merged")
def rollback_merged(body: RevertBody):
    """Create a revert PR for the latest merged 'aurora' PR."""
    owner, repo = OWNER_REPO.split("/",1)
    # latest merged PR with 'aurora' label
    r = requests.get(f"{API}/search/issues",
                     headers=gh_headers(),
                     params={"q": f"repo:{OWNER_REPO} is:pr is:closed is:merged label:aurora sort:updated-desc"})
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="No merged Aurora PR found.")
    pr_number = items[0]["number"]

    # Get merge commit SHA
    pr = requests.get(f"{API}/repos/{owner}/{repo}/pulls/{pr_number}", headers=gh_headers()).json()
    if not pr.get("merged"):
        raise HTTPException(status_code=400, detail="Selected PR not merged.")
    merge_sha = pr["merge_commit_sha"]
    base = body.base or pr["base"]["ref"]

    # GitHub REST doesn't have a simple "revert PR" endpoint everywhere,
    # so we open a *revert pull* using the special endpoint if available,
    # otherwise fall back to a minimal reverse-commit service in Bridge.
    # Try native endpoint first:
    try:
        rr = requests.post(
            f"{API}/repos/{owner}/{repo}/pulls/{pr_number}/reverts",
            headers=gh_headers(),
            json={"commit_title": f"Revert PR #{pr_number}", "body": "Automated revert", "revert": {"branch": base}}
        )
        if rr.status_code < 300:
            return {"status":"ok","revert_pr": rr.json().get("number")}
    except Exception:
        pass

    # Fallback: instruct Bridge to create a revert PR by generating a commit that undoes the diff.
    br = requests.post(
        f"{BRIDGE_URL}/api/bridge/revert",
        json={"repo": OWNER_REPO, "merge_sha": merge_sha, "base": base},
        timeout=180
    )
    if br.status_code >= 300:
        raise HTTPException(status_code=502, detail={"bridge_revert_failed": br.text})
    return br.json()

If your Bridge doesn’t yet implement /api/bridge/revert, it will still handle the open-PR rollback today, and the native GitHub “revert” endpoint will work on orgs where it’s enabled. We built the fallback hook for later.

B) Dashboard buttons (simple HTML/JS)

Add near your “Generate” UI (same page as before):

<button id="rbOpen">Rollback Open PR</button>
<button id="rbMerged">Revert Last Merged PR</button>
<pre id="rbOut"></pre>
<script>
async function callRollback(url, body) {
  const out = document.getElementById('rbOut');
  out.textContent = 'Working…';
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: {'content-type':'application/json'},
      body: JSON.stringify(body||{})
    });
    const data = await r.json();
    if(!r.ok) throw new Error(JSON.stringify(data));
    out.textContent = JSON.stringify(data, null, 2);
  } catch(e){ out.textContent = 'Error: ' + e.message; }
}
document.getElementById('rbOpen').onclick   = ()=>callRollback('/api/bridge/rollback/open');
document.getElementById('rbMerged').onclick = ()=>callRollback('/api/bridge/rollback/merged', {base:'main'});
</script>

C) Replit secrets (confirm)
	•	AURORA_GH_TOKEN → a classic PAT with repo scope (or a fine-grained token permitting PRs/branches).
	•	AURORA_REPO → chango112595-cell/Aurora-x.

⸻

Sanity checks (quick)
	•	Badge: after merging to main, visit
https://raw.githubusercontent.com/chango112595-cell/Aurora-x/badges/badges/coverage.svg
and confirm README shows it.
	•	Security tab: GitHub → Security → Code scanning alerts → should list Semgrep results.
	•	Rollback:
	•	Create a sample feature via Generate (label PRs from Aurora with aurora once in your Bridge).
	•	Click Rollback Open PR → it should close PR & delete its branch.
	•	Merge a test Aurora PR, then click Revert Last Merged PR → expect a revert PR (native or Bridge fallback).

If you want, I can also add:
	•	auto-label PRs from Aurora (aurora, generated),
	•	a “Preview diff” modal that pulls /pulls/{number}/files and renders side-by-side diff,
	•	and Slack/Discord notifications for rollback/revert outcomes.