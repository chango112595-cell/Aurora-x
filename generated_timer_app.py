from flask import Flask, Response

TITLE = 'Timer UI'
SUBTITLE = 'Futuristic timer application'

HTML = r'<!doctype html><html><head>\n<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>\n<title>{title}</title>\n<style>\n  :root{--bg1:#0a0f1f;--bg2:#030611;--neon1:#66e6ff;--neon2:#7d5bff;--text:#e6f0ff}\n  html,body{height:100%;margin:0}body{font-family:system-ui,Segoe UI,Inter,Roboto;\n  color:var(--text);background:radial-gradient(1100px 520px at 18% 12%,rgba(125,91,255,.25),transparent),\n  radial-gradient(920px 480px at 82% 88%,rgba(102,230,255,.20),transparent),\n  linear-gradient(180deg,var(--bg1),var(--bg2));display:flex;align-items:center;justify-content:center}\n  .card{width:min(760px,92vw);padding:28px;border-radius:18px;background:rgba(255,255,255,.03);\n  backdrop-filter:blur(8px);border:1px solid rgba(126,127,255,.18);box-shadow:0 0 24px rgba(102,230,255,.18),inset 0 0 24px rgba(125,91,255,.10)}\n  h1{margin:0 0 10px;font-size:28px}p{margin:0 0 16px;opacity:.86}\n  .timer{font-variant-numeric:tabular-nums;letter-spacing:.5px;font-size:56px;margin:12px 0;text-shadow:0 0 18px rgba(102,230,255,.55),0 0 28px rgba(125,91,255,.3)}\n  .row{display:flex;gap:10px;margin:12px 0}\n  input,button{font:inherit;padding:12px 14px;border-radius:12px;border:1px solid transparent;background:#0f1428;color:var(--text)}\n  input{flex:1;outline:none}input:focus{border-color:var(--neon1);box-shadow:0 0 0 2px rgba(102,230,255,.3)}\n  button{cursor:pointer;background:linear-gradient(90deg,var(--neon1),var(--neon2));color:#041019;font-weight:600}\n  button.ghost{background:transparent;color:var(--text);border:1px solid rgba(126,127,255,.28)}\n</style></head><body>\n<div class="card">\n  <h1>{title}</h1><p>{subtitle}</p>\n  <div id="timer" class="timer">00:00</div>\n  <div class="row">\n    <input id="seconds" type="number" min="0" placeholder="Enter seconds e.g. 90"/>\n    <button id="start">Start</button>\n    <button id="pause" class="ghost">Pause</button>\n    <button id="reset" class="ghost">Reset</button>\n  </div>\n</div>\n<script>\nfunction fmt(ms){ms=Math.max(0,Math.floor(ms));const t=Math.floor(ms/1000);const m=(\'\'+Math.floor(t/60)).padStart(2,\'0\');const s=(\'\'+(t%60)).padStart(2,\'0\');return m+\':\'+s;}\nlet dur=0,t0=0,left=0,raf=null,run=false;const view=document.getElementById(\'timer\');\nfunction tick(ts){if(!run)return;if(!t0)t0=ts;const el=ts-t0;left=Math.max(0,dur-el);view.textContent=fmt(left);if(left<=0){run=false;cancelAnimationFrame(raf);}else{raf=requestAnimationFrame(tick);}}\ndocument.getElementById(\'start\').onclick=()=>{const secs=Math.max(0,Number(document.getElementById(\'seconds\').value||0));if(!run){if(left<=0)dur=secs*1000;t0=0;run=true;raf=requestAnimationFrame(tick);}};\ndocument.getElementById(\'pause\').onclick=()=>{run=false;};document.getElementById(\'reset\').onclick=()=>{run=false;t0=0;left=0;view.textContent=\'00:00\';};\n</script></body></html>'

def create_app() -> Flask:
    app = Flask(__name__)
    @app.get('/')
    def index() -> Response:
        return Response(HTML.format(title=TITLE, subtitle=SUBTITLE), mimetype='text/html')
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.getenv('PORT', '8000'))
    print(f'🚀 Starting Flask app on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=True)
