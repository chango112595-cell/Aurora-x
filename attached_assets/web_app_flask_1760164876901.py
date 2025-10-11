
from flask import Flask, Response
import os

HTML = """<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
  :root{--bg1:#0a0f1f;--bg2:#030611;--neon1:#66e6ff;--neon2:#7d5bff;--text:#e6f0ff}
  html,body{height:100%;margin:0}body{font-family:system-ui,Segoe UI,Inter,Roboto;
  color:var(--text);background:radial-gradient(1100px 520px at 18% 12%,rgba(125,91,255,.25),transparent),
  radial-gradient(920px 480px at 82% 88%,rgba(102,230,255,.20),transparent),
  linear-gradient(180deg,var(--bg1),var(--bg2));display:flex;align-items:center;justify-content:center}
  .card{width:min(760px,92vw);padding:28px;border-radius:18px;background:rgba(255,255,255,.03);
  backdrop-filter:blur(8px);border:1px solid rgba(126,127,255,.18);box-shadow:0 0 24px rgba(102,230,255,.18),inset 0 0 24px rgba(125,91,255,.10)}
  h1{margin:0 0 10px;font-size:28px}p{margin:0 0 16px;opacity:.86}
</style></head><body>
<div class="card"><h1>{title}</h1><p>{subtitle}</p></div>
</body></html>"""

def render_app(title: str, subtitle: str) -> str:
    return f"""from flask import Flask, Response
import os
TITLE={title!r}; SUBTITLE={subtitle!r}
HTML=r{HTML!r}
def create_app()->Flask:
    app=Flask(__name__)
    @app.get('/')
    def index()->Response:
        return Response(HTML.format(title=TITLE, subtitle=SUBTITLE), mimetype='text/html')
    return app
if __name__=='__main__':
    app=create_app()
    port=int(os.getenv('PORT','8000'))
    app.run(host='0.0.0.0', port=port, debug=True)
"""
