
from flask import request, jsonify
from pathlib import Path
from aurora_x.router.intent_router import classify
from aurora_x.templates.web_app_flask import render_app

def attach_router(app):
    @app.post('/chat')
    def chat():
        data = request.get_json(silent=True) or {}
        prompt = (data.get('prompt') or '').strip()
        if not prompt:
            return jsonify({"ok": False, "err": "missing prompt"}), 400
        intent = classify(prompt)
        if intent.kind == "web_app":
            title = "Futuristic UI Timer" if intent.fields.get("feature")=="timer" else intent.name.replace('_',' ').title()
            code = render_app(title=title, subtitle=intent.brief)
            Path("app.py").write_text(code, encoding="utf-8")
            return jsonify({"ok": True, "kind": "web_app", "file": "app.py", "hint": "Run: python app.py"})
        # Future: cli_tool, lib_func
        return jsonify({"ok": True, "kind": intent.kind, "name": intent.name, "note": "Template not implemented yet"})
