from __future__ import annotations

import json
from pathlib import Path

from fastapi import Response
from fastapi.responses import JSONResponse

PROGRESS_PATH = Path("progress.json")

DASH_HTML = r"""<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aurora-X · Progress</title>
<style>
:root{--bg:#070b14;--panel:#0d1324;--fg:#e6f0ff;--ok:#32d296;--ip:#ffd166;--hold:#ff6b6b;}
html,body{height:100%;margin:0;background:radial-gradient(1200px 540px at 12% 8%,rgba(125,91,255,.18),transparent),
radial-gradient(980px 500px at 88% 92%,rgba(102,230,255,.14),transparent),linear-gradient(180deg,#0a0f1f,#050812);color:var(--fg);
font:15px/1.5 system-ui,Segoe UI,Inter,Roboto}
.wrap{max-width:1100px;margin:28px auto;padding:0 18px}
h1{margin:0 0 6px} .sub{opacity:.85;margin:0 0 18px}
.card{background:var(--panel);border:1px solid rgba(126,127,255,.18);border-radius:14px;padding:16px;margin-bottom:14px}
.row{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.bar{height:8px;background:#1b2445;border-radius:999px;overflow:hidden;margin-top:8px}
.fill{height:100%;background:linear-gradient(90deg,#66e6ff,#7d5bff)}
.status{font-size:12px;opacity:.9}
.s-ok{color:var(--ok)} .s-ip{color:var(--ip)} .s-hold{color:var(--hold)}
small{opacity:.8}
.btn{padding:8px 10px;border:0;border-radius:12px;background:linear-gradient(90deg,#66e6ff,#7d5bff);color:#041019;font-weight:700;cursor:pointer}
.actions{display:flex;gap:10px;align-items:center;margin:10px 0}
pre{background:#0b1226;border:1px solid rgba(126,127,255,.18);border-radius:12px;padding:10px;overflow:auto}
</style></head><body>
<div class="wrap">
  <h1>📊 Aurora-X · Progress</h1>
  <p class="sub">Live view powered by <code>progress.json</code>. Auto-refreshes every 5s.</p>

  <div class="card">
    <div class="row">
      <div><span id="overall" class="badge">Overall: --%</span>
           <span id="active" class="badge">Active: --</span>
           <span id="updated" class="badge">Updated: --</span></div>
      <div class="actions"><button class="btn" id="refresh">↻ Refresh</button>
           <a class="btn" href="/api/progress" target="_blank" rel="noopener">Raw JSON</a></div>
    </div>
    <div class="row" style="margin-top:10px">
      <div class="small">Thresholds:
        <label>OK ≥ <input id="thOk" type="number" min="0" max="100" value="90" style="width:64px"></label>
        <label>Warn ≥ <input id="thWarn" type="number" min="0" max="100" value="60" style="width:64px"></label>
      </div>
      <button class="btn" id="saveTh">Save</button>
    </div>
  </div>

  <div id="grid" class="grid"></div>

  <div class="card">
    <h3>Export</h3>
    <pre>make update-progress   # regenerate markdown + CSV
make export-progress   # export CSV only
make progress-view     # preview markdown in terminal</pre>
  </div>
</div>
<script>
const $ = s => document.querySelector(s);
function statusClass(s){ if(s==='complete')return 's-ok'; if(s.startsWith('in'))return 's-ip'; if(s.includes('hold'))return 's-hold'; return '';}
function render(data){
  const tasks = (data.tasks||[]);
  const avg = Math.round(tasks.reduce((a,t)=>a+(t.percent||0),0)/Math.max(1,tasks.length));
  $('#overall').textContent = `Overall: ${avg}%`;
  $('#active').textContent = `Active: ${(data.active||[]).join(', ')||'—'}`;
  $('#updated').textContent = `Updated: ${data.updated_utc||'—'}`;
  const grid = $('#grid'); grid.innerHTML='';
  tasks.forEach(t=>{
    const div = document.createElement('div'); div.className='card';
    div.innerHTML = `<div class="row"><div><strong>${t.id}</strong> — ${t.name}</div>
                     <div class="status ${statusClass(t.status||'')}">${t.status||''}</div></div>
                     <div class="bar"><div class="fill" style="width:${t.percent||0}%"></div></div>
                     <small>${(t.notes||[]).slice(0,2).join(' • ')}</small>`;
    grid.appendChild(div);
  });
}
async function load(){
  try{
    const r=await fetch('/api/progress'); const j=await r.json(); render(j);
    const th = j.ui_thresholds || {ok:90, warn:60};
    document.getElementById('thOk').value = th.ok;
    document.getElementById('thWarn').value = th.warn;
  }catch(e){ console.error(e); }
}
document.getElementById('saveTh').onclick = async ()=>{
  const ok = parseInt(document.getElementById('thOk').value,10);
  const warn = parseInt(document.getElementById('thWarn').value,10);
  const res = await fetch('/api/progress/ui_thresholds', {
    method:'POST', headers:{'content-type':'application/json'},
    body: JSON.stringify({ ui_thresholds: { ok, warn } })
  });
  const j = await res.json();
  if(j.ok){ await load(); alert('Thresholds saved'); } else { alert(j.err||'Failed'); }
};
$('#refresh').onclick = load; load(); setInterval(load, 5000);
</script>
</body></html>"""


def attach_progress(app):
    @app.get("/api/progress")
    def api_progress():
        if not PROGRESS_PATH.exists():
            return JSONResponse({"ok": False, "err": "progress.json not found"}, status_code=404)
        try:
            data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            return JSONResponse(
                {"ok": False, "err": f"invalid progress.json: {e}"}, status_code=422
            )
        tasks = data.get("tasks", [])
        # Parse percent values properly (handle string percentages)
        total = 0
        for t in tasks:
            percent = t.get("percent", 0)
            if isinstance(percent, str):
                percent = float(percent.replace("%", ""))
            total += percent
        overall = round(total / max(1, len(tasks)), 2)
        data["overall_percent"] = overall
        # Add thresholds with defaults if missing
        th = data.get("ui_thresholds") or {}
        data["ui_thresholds"] = {"ok": int(th.get("ok", 90)), "warn": int(th.get("warn", 60))}
        data["ok"] = True
        return JSONResponse(data)

    @app.post("/api/progress/ui_thresholds")
    def api_progress_update_thresholds():
        from flask import request

        try:
            data = (
                json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
                if PROGRESS_PATH.exists()
                else {}
            )
        except Exception as e:
            return JSONResponse(
                {"ok": False, "err": f"invalid progress.json: {e}"}, status_code=422
            )

        body = request.get_json(silent=True) or {}
        th = body.get("ui_thresholds") or {}
        try:
            ok = int(th.get("ok", 90))
            warn = int(th.get("warn", 60))
            if not (0 <= warn <= ok <= 100):
                return JSONResponse(
                    {"ok": False, "err": "require 0 ≤ warn ≤ ok ≤ 100"}, status_code=400
                )
        except Exception:
            return JSONResponse({"ok": False, "err": "ok/warn must be integers"}, status_code=400)

        data["ui_thresholds"] = {"ok": ok, "warn": warn}
        PROGRESS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return JSONResponse({"ok": True, "ui_thresholds": data["ui_thresholds"]})

    @app.get("/dashboard/progress")
    def dashboard_progress():
        return Response(DASH_HTML, media_type="text/html")
