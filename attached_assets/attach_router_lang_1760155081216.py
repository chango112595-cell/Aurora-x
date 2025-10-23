from pathlib import Path

from aurora_x.templates.lib_function import render_function
from flask import jsonify, request

from aurora_x.router.intent_router import classify
from aurora_x.router.lang_select import pick_language
from aurora_x.templates.cli_tool import render_cli
from aurora_x.templates.csharp_webapi import render_csharp_webapi
from aurora_x.templates.go_service import render_go_service
from aurora_x.templates.rust_cli import render_rust_cli
from aurora_x.templates.web_app_flask import render_app


def attach_router(app):
    @app.post("/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify({"ok": False, "err": "missing prompt"}), 400

        intent = classify(prompt)
        lang = pick_language(prompt)

        # explicit override via payload
        explicit = (data.get("lang") or "").strip().lower()
        if explicit in ("python", "go", "rust", "csharp"):
            lang.lang = explicit
            lang.reason = f"explicit payload lang={explicit}"

        if intent.kind == "web_app":
            if lang.lang == "python":
                code = render_app(title=intent.name.replace("_", " ").title(), subtitle=intent.brief)
                Path("app.py").write_text(code, encoding="utf-8")
                return jsonify(
                    {
                        "ok": True,
                        "kind": "web_app",
                        "lang": "python",
                        "file": "app.py",
                        "reason": lang.reason,
                        "hint": "python app.py",
                    }
                )
            if lang.lang == "go":
                pkg = render_go_service(intent.name)
                for fname, src in pkg["files"].items():
                    Path(fname).parent.mkdir(parents=True, exist_ok=True)
                    Path(fname).write_text(src, encoding="utf-8")
                return jsonify(
                    {
                        "ok": True,
                        "kind": "web_app",
                        "lang": "go",
                        "files": list(pkg["files"].keys()),
                        "reason": lang.reason,
                        "hint": pkg["hint"],
                    }
                )
            if lang.lang == "csharp":
                pkg = render_csharp_webapi(intent.name)
                folder = Path(pkg.get("folder") or "Aurora.WebApi")
                for fname, src in pkg["files"].items():
                    Path(folder / fname).parent.mkdir(parents=True, exist_ok=True)
                    Path(folder / fname).write_text(src, encoding="utf-8")
                return jsonify(
                    {
                        "ok": True,
                        "kind": "web_app",
                        "lang": "csharp",
                        "folder": str(folder),
                        "files": list(pkg["files"].keys()),
                        "reason": lang.reason,
                        "hint": pkg["hint"],
                    }
                )
            # rust fallback to python/go
            code = render_app(title=intent.name.replace("_", " ").title(), subtitle=intent.brief)
            Path("app.py").write_text(code, encoding="utf-8")
            return jsonify(
                {
                    "ok": True,
                    "kind": "web_app",
                    "lang": "python",
                    "file": "app.py",
                    "reason": "fallback to python",
                    "hint": "python app.py",
                }
            )

        if intent.kind == "cli_tool":
            if lang.lang == "rust":
                pkg = render_rust_cli(intent.name)
                for fname, src in pkg["files"].items():
                    Path(fname).parent.mkdir(parents=True, exist_ok=True)
                    Path(fname).write_text(src, encoding="utf-8")
                return jsonify(
                    {
                        "ok": True,
                        "kind": "cli_tool",
                        "lang": "rust",
                        "files": list(pkg["files"].keys()),
                        "reason": lang.reason,
                        "hint": pkg["hint"],
                    }
                )
            code = render_cli(intent.name, intent.brief)
            fname = f"{intent.name}.py"
            Path(fname).write_text(code, encoding="utf-8")
            return jsonify(
                {
                    "ok": True,
                    "kind": "cli_tool",
                    "lang": "python",
                    "file": fname,
                    "reason": lang.reason,
                    "hint": f"python {fname} --help",
                }
            )

        code, tests = render_function(intent.name, intent.brief)
        fname = f"{intent.name}.py"
        Path(fname).write_text(code, encoding="utf-8")
        Path("tests").mkdir(exist_ok=True, parents=True)
        Path(f"tests/test_{intent.name}.py").write_text(tests, encoding="utf-8")
        return jsonify(
            {
                "ok": True,
                "kind": "lib_func",
                "lang": "python",
                "file": fname,
                "reason": lang.reason,
                "hint": "pytest -q",
            }
        )
