import pathlib
import re
import shlex
import subprocess
import zipfile
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from aurora_x.bridge.deploy import deploy as deploy_fn
from aurora_x.bridge.pipeline import compile_from_nl, compile_from_nl_project, compile_from_spec
from aurora_x.bridge.pr import pr_create as pr_create_fn


def _shell(cmd: str):
    """Execute shell command and return result."""
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class NLBody(BaseModel):
    prompt: str


class SpecBody(BaseModel):
    path: str


class ProjectBody(BaseModel):
    prompt: str
    repo: str | None = None  # Repository string in format "owner/name" or full URL
    stack: str | None = None
    mode: Literal["create", "enhance"] = "create"  # "create" for new, "enhance" for PR


def attach_bridge(app: FastAPI):
    @app.post("/api/bridge/nl")
    def bridge_nl(body: NLBody):
        if not body.prompt or len(body.prompt.strip()) < 4:
            raise HTTPException(400, "prompt too short")
        res = compile_from_nl(body.prompt.strip())
        return JSONResponse(res.__dict__)

    @app.post("/api/bridge/spec")
    def bridge_spec(body: SpecBody):
        res = compile_from_spec(body.path)
        return JSONResponse(res.__dict__)

    @app.post("/api/bridge/deploy")
    def bridge_deploy():
        return JSONResponse(deploy_fn())

    @app.post("/api/bridge/nl/project")
    def bridge_nl_project(body: ProjectBody):
        if not body.prompt or len(body.prompt.strip()) < 4:
            raise HTTPException(400, "prompt too short")

        # Parse repository string if provided
        repo_info = None
        repo_owner = None
        repo_name = None
        repo_branch = "main"

        if body.repo:
            # Handle different repo formats:
            # - "owner/name"
            # - "github.com/owner/name"
            # - "https://github.com/owner/name"
            # - "https://github.com/owner/name.git"
            repo_str = body.repo.strip()

            # Remove common prefixes
            repo_str = re.sub(r"^https?://", "", repo_str)
            repo_str = re.sub(r"^github\.com/", "", repo_str)
            repo_str = re.sub(r"\.git$", "", repo_str)
            repo_str = repo_str.strip("/")

            # Split owner/name
            parts = repo_str.split("/")
            if len(parts) >= 2:
                repo_owner = parts[0]
                repo_name = parts[1]
                repo_info = {"owner": repo_owner, "name": repo_name, "branch": repo_branch}
            else:
                # Invalid format
                return JSONResponse(
                    {
                        "ok": False,
                        "message": f"Invalid repository format: {body.repo}. Use 'owner/name' format",
                        "mode": body.mode,
                    }
                )

        # Basic planner logic to determine if UI/API components are needed
        prompt_lower = body.prompt.lower()
        stack_lower = body.stack.lower() if body.stack else ""

        # Determine project components based on stack and prompt keywords
        components = {"ui_needed": False, "api_needed": False, "database_needed": False, "auth_needed": False}

        # UI detection patterns - use word boundaries for better matching
        ui_patterns = [
            "frontend",
            "react",
            "vue",
            "angular",
            "interface",
            "dashboard",
            "website",
            "html",
            "css",
            "component",
            "page",
            "user interface",
            "web ui",
            "webapp",
            "web app",
        ]
        if (
            any(pattern in prompt_lower for pattern in ui_patterns)
            or any(pattern in stack_lower for pattern in ["react", "vue", "angular", "nextjs"])
            or " ui " in f" {prompt_lower} "
        ):  # Check for UI as a standalone word
            components["ui_needed"] = True

        # API detection patterns
        api_patterns = [
            "api",
            "backend",
            "rest",
            "endpoint",
            "server",
            "flask",
            "fastapi",
            "express",
            "django",
            "route",
            "crud",
        ]
        if any(pattern in prompt_lower for pattern in api_patterns) or any(
            pattern in stack_lower for pattern in ["flask", "fastapi", "express", "django"]
        ):
            components["api_needed"] = True

        # Database detection patterns
        db_patterns = ["database", "db", "sql", "postgres", "mysql", "mongodb", "store", "persist", "save data"]
        if any(pattern in prompt_lower for pattern in db_patterns):
            components["database_needed"] = True

        # Auth detection patterns
        auth_patterns = ["auth", "login", "user", "account", "signup", "signin", "authentication", "authorization"]
        if any(pattern in prompt_lower for pattern in auth_patterns):
            components["auth_needed"] = True

        # If nothing detected but stack is fullstack, enable both UI and API
        if body.stack and "fullstack" in stack_lower:
            components["ui_needed"] = True
            components["api_needed"] = True

        # Build enhanced prompt with stack info
        enhanced_prompt = body.prompt
        if body.stack:
            enhanced_prompt = f"[Stack: {body.stack}] {body.prompt}"

        # Process based on mode
        if body.mode == "enhance":  # PR mode
            # Check if we have repo information
            if not repo_owner or not repo_name:
                return JSONResponse(
                    {
                        "ok": False,
                        "message": "Repository information (owner/name) required for enhance mode",
                        "mode": "enhance",
                        "components": components,
                    }
                )

            # First, generate the project to get the ZIP file (skip git operations for PR mode)
            res = compile_from_nl_project(
                prompt=enhanced_prompt,
                repo_info=repo_info,
                stack=body.stack,
                components=components,
                skip_git_operations=True,  # Don't auto-commit in PR mode
            )

            # Call PR creation function with the generated ZIP
            try:
                pr_result = pr_create_fn(
                    owner=repo_owner,
                    name=repo_name,
                    base=repo_branch,
                    title=f"Aurora: {body.prompt[:60]}",
                    body=f"Automated PR generated from prompt:\n\n{enhanced_prompt}\n\nComponents: {components}",
                    zip_rel=res.zip_rel,
                )

                return JSONResponse(
                    {
                        "ok": pr_result.get("ok", False),
                        "message": (
                            "PR creation initiated"
                            if pr_result.get("ok")
                            else pr_result.get("err", "PR creation failed")
                        ),
                        "mode": "enhance",
                        "components": components,
                        "pr_result": pr_result,
                    }
                )
            except Exception as e:
                return JSONResponse(
                    {
                        "ok": False,
                        "message": f"PR creation failed: {str(e)}",
                        "mode": "enhance",
                        "components": components,
                    }
                )
        else:
            # Regular create mode - use compile_from_nl_project with git operations
            # Pass the enhanced context to the compiler
            res = compile_from_nl_project(
                prompt=enhanced_prompt,
                repo_info=repo_info,
                stack=body.stack,
                components=components,
                skip_git_operations=False,  # Do auto-commit in create mode
            )

            return JSONResponse({**res.__dict__, "components": components, "mode": "create"})

    @app.get("/bridge/diff")
    def bridge_diff():
        """Get a structured summary of current git diff."""
        code, out, err = _shell("git --no-pager diff --stat")
        if code == 0:
            # Parse the diff stat output
            lines = out.strip().split("\n") if out else []
            files_changed = []
            summary = ""

            for line in lines:
                # Skip empty lines and the summary line
                if not line or "file" in line and "changed" in line:
                    summary = line
                elif "|" in line:
                    # This is a file change line
                    parts = line.split("|")
                    if len(parts) == 2:
                        file_path = parts[0].strip()
                        changes = parts[1].strip()
                        files_changed.append({"file": file_path, "changes": changes})

            return JSONResponse(
                {"ok": True, "files_changed": files_changed, "summary": summary, "has_changes": len(files_changed) > 0}
            )
        else:
            return JSONResponse(
                {"ok": False, "err": err or "Failed to get diff", "has_changes": False}, status_code=500
            )

    @app.get("/bridge/diff/full", response_class=PlainTextResponse)
    def bridge_diff_full():
        """Get the full git diff as plain text (for viewing in browser)."""
        code, out, err = _shell("git --no-pager diff")
        if code == 0:
            return out if out else "No changes to display"
        else:
            return f"Error getting diff: {err or 'unknown error'}"

    @app.get("/bridge/preview")
    def bridge_preview(zip: str | None = None):
        """
        Returns a JSON manifest of files that WOULD be applied from the zip (no write).
        """
        # prefer explicit ?zip=/api/runs/<ts>/project.zip; fallback newest
        if zip:
            zpath = pathlib.Path(".") / (zip.lstrip("/") if zip else "")
        else:
            zpath = None

        if not zpath or not zpath.exists():
            candidates = sorted(pathlib.Path("runs").glob("*/project.zip"))
            zpath = candidates[-1] if candidates else None

        if not zpath or not zpath.exists():
            return JSONResponse({"ok": False, "err": "no zip found"}, status_code=404)

        manifest = []
        with zipfile.ZipFile(zpath, "r") as z:
            for info in z.infolist():
                manifest.append({"name": info.filename, "size": info.file_size})

        return {"ok": True, "zip": str(zpath), "files": manifest}
