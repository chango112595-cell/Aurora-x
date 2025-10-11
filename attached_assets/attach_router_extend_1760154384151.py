
from flask import request, jsonify
from pathlib import Path
from aurora_x.router.intent_router import classify
from aurora_x.templates.web_app_flask import render_app
from aurora_x.templates.cli_tool import render_cli
from aurora_x.templates.lib_function import render_function

def attach_router(app):
    @app.post('/chat')
    def chat():
        data = request.get_json(silent=True) or {}
        prompt = (data.get('prompt') or '').strip()
        if not prompt:
            return jsonify({"ok": False, "err": "missing prompt"}), 400
        intent = classify(prompt)

        if intent.kind == "web_app":
            title = "Futuristic UI" if "timer" not in intent.fields else "Futuristic UI Timer"
            code = render_app(title=title, subtitle=intent.brief)
            Path("app.py").write_text(code, encoding="utf-8")
            return jsonify({"ok": True, "kind": "web_app", "file": "app.py", "hint": "Run: python app.py"})

        if intent.kind == "cli_tool":
            code = render_cli(intent.name, intent.brief)
            fname = f"{intent.name}.py"
            Path(fname).write_text(code, encoding="utf-8")
            return jsonify({"ok": True, "kind": "cli_tool", "file": fname, "hint": f"Run: python {fname} --help"})

        # lib function
        code, tests = render_function(intent.name, intent.brief)
        fname = f"{intent.name}.py"
        Path(fname).write_text(code, encoding="utf-8")
        tf = f"tests/test_{intent.name}.py"
        Path("tests").mkdir(exist_ok=True, parents=True)
        Path(tf).write_text(tests, encoding="utf-8")
        return jsonify({"ok": True, "kind": "lib_func", "file": fname, "tests": tf, "hint": "Run: pytest -q"})
