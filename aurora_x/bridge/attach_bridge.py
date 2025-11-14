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
        components = {
            "ui_needed": False,
            "api_needed": False,
            "database_needed": False,
            "auth_needed": False,
        }

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
        db_patterns = [
            "database",
            "db",
            "sql",
            "postgres",
            "mysql",
            "mongodb",
            "store",
            "persist",
            "save data",
        ]
        if any(pattern in prompt_lower for pattern in db_patterns):
            components["database_needed"] = True

        # Auth detection patterns
        auth_patterns = [
            "auth",
            "login",
            "user",
            "account",
            "signup",
            "signin",
            "authentication",
            "authorization",
        ]
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
                {
                    "ok": True,
                    "files_changed": files_changed,
                    "summary": summary,
                    "has_changes": len(files_changed) > 0,
                }
            )
        else:
            return JSONResponse(
                {"ok": False, "err": err or "Failed to get diff", "has_changes": False},
                status_code=500,
            )

    @app.get("/bridge/diff/full", response_class=PlainTextResponse)
    def bridge_diff_full():
        """Get the full git diff as plain text (for viewing in browser)."""
        code, out, err = _shell("git --no-pager diff")
        if code == 0:
            return out if out else "No changes to display"
        else:
            return f"Error getting diff: {err or 'unknown error'}"

    @app.get("/bridge/comparison/commits")
    def bridge_comparison_commits():
        """Get recent git commits for comparison selection."""
        code, out, err = _shell("git log --oneline -20")
        if code == 0:
            commits = []
            for line in out.strip().split("\n") if out else []:
                if line:
                    parts = line.split(" ", 1)
                    if len(parts) >= 2:
                        commits.append({"hash": parts[0], "message": parts[1], "short_hash": parts[0][:7]})

            # Get current branch
            branch_code, branch_out, _ = _shell("git branch --show-current")
            current_branch = branch_out.strip() if branch_code == 0 else "unknown"

            return JSONResponse({"ok": True, "commits": commits, "current_branch": current_branch})
        else:
            return JSONResponse({"ok": False, "err": err or "Failed to get commits"}, status_code=500)

    @app.get("/bridge/comparison/diff")
    def bridge_comparison_diff(commit1: str | None = None, commit2: str | None = None):
        """Get detailed diff between two commits or commit vs current."""
        if not commit1:
            # Default to comparing working directory with HEAD
            cmd = "git --no-pager diff --name-status HEAD"
        elif not commit2:
            # Compare commit with current working directory
            cmd = f"git --no-pager diff --name-status {commit1}"
        else:
            # Compare two commits
            cmd = f"git --no-pager diff --name-status {commit1}..{commit2}"

        code, out, err = _shell(cmd)
        if code == 0:
            files = []
            for line in out.strip().split("\n") if out else []:
                if line:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        status = parts[0]
                        filepath = parts[1]
                        files.append(
                            {
                                "status": status,
                                "file": filepath,
                                "status_text": {
                                    "M": "Modified",
                                    "A": "Added",
                                    "D": "Deleted",
                                    "R": "Renamed",
                                    "C": "Copied",
                                }.get(status[0], "Changed"),
                            }
                        )

            return JSONResponse({"ok": True, "files": files, "commit1": commit1, "commit2": commit2})
        else:
            return JSONResponse({"ok": False, "err": err or "Failed to get diff"}, status_code=500)

    @app.get("/bridge/comparison/aurora-runs")
    def bridge_comparison_aurora_runs():
        """Get available Aurora runs for comparison."""
        import pathlib

        runs_dir = pathlib.Path("runs")
        if not runs_dir.exists():
            return JSONResponse({"ok": True, "runs": []})

        runs = []
        for run_path in sorted(runs_dir.glob("run-*"), reverse=True)[:20]:  # Last 20 runs
            try:
                # Check for run metadata
                meta_file = run_path / "run_meta.json"
                spec_file = run_path / "spec.json"

                run_info = {
                    "name": run_path.name,
                    "path": str(run_path),
                    "has_graph_diff": (run_path / "graph_diff.json").exists(),
                    "has_scores_diff": (run_path / "scores_diff.json").exists(),
                    "has_report": (run_path / "report.html").exists(),
                }

                if meta_file.exists():
                    import json

                    try:
                        with open(meta_file) as f:
                            meta = json.load(f)
                        run_info["start_time"] = meta.get("start_ts")
                        run_info["duration"] = meta.get("duration_seconds")
                    except:
                        pass

                if spec_file.exists():
                    try:
                        with open(spec_file) as f:
                            spec = json.load(f)
                        run_info["seed"] = spec.get("seed")
                        run_info["max_iters"] = spec.get("max_iters")
                    except:
                        pass

                runs.append(run_info)
            except:
                continue

        return JSONResponse({"ok": True, "runs": runs})

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

    # Comparison endpoints for git and Aurora data
    @app.get("/api/bridge/comparison/commits")
    def get_commits():
        """Get git commit history for comparison"""
        try:
            # Get current branch
            current_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=".", text=True).strip()

            # Get recent commits
            result = subprocess.check_output(
                ["git", "log", "--oneline", "-20", "--pretty=format:%H|%s"], cwd=".", text=True
            )

            commits = []
            for line in result.strip().split("\n"):
                if "|" in line:
                    hash_part, message = line.split("|", 1)
                    commits.append({"hash": hash_part, "short_hash": hash_part[:7], "message": message})

            return JSONResponse({"ok": True, "commits": commits, "current_branch": current_branch})
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.get("/api/bridge/comparison/diff")
    def get_diff(commit1: str = "", commit2: str = ""):
        """Get diff between two commits or working directory"""
        try:
            # Build git diff command
            cmd = ["git", "diff", "--name-status"]
            if commit1 and commit2:
                cmd.append(f"{commit1}..{commit2}")
            elif commit1:
                cmd.append(commit1)
            elif commit2:
                cmd.append(commit2)

            result = subprocess.check_output(cmd, cwd=".", text=True)

            files = []
            for line in result.strip().split("\n"):
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        status = parts[0]
                        file_path = parts[1]
                        status_text = {
                            "M": "Modified",
                            "A": "Added",
                            "D": "Deleted",
                            "R": "Renamed",
                            "C": "Copied",
                        }.get(status, status)

                        files.append({"status": status, "file": file_path, "status_text": status_text})

            return JSONResponse({"ok": True, "files": files})
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.get("/api/bridge/comparison/aurora-runs")
    def get_aurora_runs():
        """Get Aurora run history for comparison"""
        try:
            runs_dir = pathlib.Path("runs")
            if not runs_dir.exists():
                return JSONResponse({"ok": True, "runs": []})

            runs = []
            for run_path in sorted(runs_dir.iterdir()):
                if run_path.is_dir():
                    run_data = {
                        "name": run_path.name,
                        "path": str(run_path),
                        "has_graph_diff": (run_path / "graph_diff.json").exists(),
                        "has_scores_diff": (run_path / "scores_diff.json").exists(),
                        "has_report": (run_path / "report.html").exists(),
                    }

                    # Try to get run metadata
                    spec_file = run_path / "spec.json"
                    if spec_file.exists():
                        try:
                            import json

                            spec = json.loads(spec_file.read_text())
                            run_data.update(
                                {
                                    "start_time": spec.get("start_time"),
                                    "duration": spec.get("duration"),
                                    "seed": spec.get("seed"),
                                    "max_iters": spec.get("max_iters"),
                                }
                            )
                        except:
                            pass

                    runs.append(run_data)

            return JSONResponse({"ok": True, "runs": runs})
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.get("/api/bridge/diff/full", response_class=PlainTextResponse)
    def get_full_diff(commit1: str = "", commit2: str = ""):
        """Get full git diff as plain text"""
        try:
            cmd = ["git", "diff"]
            if commit1 and commit2:
                cmd.append(f"{commit1}..{commit2}")
            elif commit1:
                cmd.append(commit1)
            elif commit2:
                cmd.append(commit2)

            result = subprocess.check_output(cmd, cwd=".", text=True)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @app.get("/api/bridge/comparison/branches")
    def get_branches():
        """Get all available branches with analysis data"""
        try:
            # Get all branches
            result = subprocess.check_output(["git", "branch", "-a"], cwd=".", text=True)
            branches = []

            for line in result.strip().split("\n"):
                line = line.strip()
                if line.startswith("*"):
                    line = line[1:].strip()
                if line.startswith("remotes/origin/"):
                    branch_name = line.replace("remotes/origin/", "")
                    if branch_name not in ["HEAD", "main"]:  # Skip HEAD pointer and we'll add main separately
                        branches.append(branch_name)
                elif not line.startswith("remotes/") and line and line != "main":
                    branches.append(line)

            # Always include main branch
            if "main" not in branches:
                branches.insert(0, "main")

            # Get current branch to compare against
            current_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=".", text=True
            ).strip()

            branch_data = []
            for branch in branches:
                try:
                    # Get commit count
                    if branch == current_branch:
                        commit_count = int(
                            subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=".", text=True).strip()
                        )
                    else:
                        try:
                            commit_count = int(
                                subprocess.check_output(
                                    ["git", "rev-list", "--count", f"origin/{branch}"], cwd=".", text=True
                                ).strip()
                            )
                        except:
                            commit_count = 0

                    # Get last commit info
                    try:
                        if branch == current_branch:
                            last_commit = subprocess.check_output(
                                ["git", "log", "-1", "--format=%h", "HEAD"], cwd=".", text=True
                            ).strip()
                            last_commit_msg = subprocess.check_output(
                                ["git", "log", "-1", "--format=%s", "HEAD"], cwd=".", text=True
                            ).strip()
                        else:
                            last_commit = subprocess.check_output(
                                ["git", "log", "-1", "--format=%h", f"origin/{branch}"], cwd=".", text=True
                            ).strip()
                            last_commit_msg = subprocess.check_output(
                                ["git", "log", "-1", "--format=%s", f"origin/{branch}"], cwd=".", text=True
                            ).strip()
                    except:
                        last_commit = "unknown"
                        last_commit_msg = "No commits"

                    # Analyze unique features based on commit messages and file changes
                    unique_features = []
                    feature_category = "General Development"
                    improvement_score = 5

                    # Get file changes compared to main
                    file_changes = 0
                    lines_added = 0
                    lines_deleted = 0

                    try:
                        if branch != "main":
                            # Get commits unique to this branch
                            try:
                                if branch == current_branch:
                                    commits_output = subprocess.check_output(
                                        ["git", "log", "--oneline", "main..HEAD"], cwd=".", text=True
                                    )
                                else:
                                    commits_output = subprocess.check_output(
                                        ["git", "log", "--oneline", f"main..origin/{branch}"], cwd=".", text=True
                                    )

                                # Analyze commit messages for features
                                commit_lines = [line.strip() for line in commits_output.split("\n") if line.strip()]

                                # Check for specific feature patterns in commits
                                ui_keywords = [
                                    "dashboard",
                                    "ui",
                                    "interface",
                                    "visual",
                                    "frontend",
                                    "react",
                                    "component",
                                ]
                                api_keywords = ["api", "endpoint", "service", "backend", "server", "fastapi"]
                                ai_keywords = ["copilot", "ai", "learning", "intelligent", "auto", "generate"]
                                config_keywords = ["config", "setup", "build", "deploy", "env", "docker"]

                                ui_count = sum(
                                    1 for commit in commit_lines if any(kw in commit.lower() for kw in ui_keywords)
                                )
                                api_count = sum(
                                    1 for commit in commit_lines if any(kw in commit.lower() for kw in api_keywords)
                                )
                                ai_count = sum(
                                    1 for commit in commit_lines if any(kw in commit.lower() for kw in ai_keywords)
                                )
                                config_count = sum(
                                    1 for commit in commit_lines if any(kw in commit.lower() for kw in config_keywords)
                                )

                            except:
                                ui_count = api_count = ai_count = config_count = 0

                            # Compare with main branch for file changes
                            try:
                                if branch == current_branch:
                                    diff_output = subprocess.check_output(
                                        ["git", "diff", "--stat", "main", "HEAD"], cwd=".", text=True
                                    )
                                else:
                                    diff_output = subprocess.check_output(
                                        ["git", "diff", "--stat", "main", f"origin/{branch}"], cwd=".", text=True
                                    )

                                # Parse diff stats
                                lines = diff_output.strip().split("\n")
                                if lines and lines[-1].strip():
                                    # Last line usually contains summary like "5 files changed, 123 insertions(+), 45 deletions(-)"
                                    summary = lines[-1]
                                    if "file" in summary:
                                        file_changes = (
                                            int(re.search(r"(\d+) files? changed", summary).group(1))
                                            if re.search(r"(\d+) files? changed", summary)
                                            else 0
                                        )
                                    if "insertion" in summary:
                                        lines_added = (
                                            int(re.search(r"(\d+) insertion", summary).group(1))
                                            if re.search(r"(\d+) insertion", summary)
                                            else 0
                                        )
                                    if "deletion" in summary:
                                        lines_deleted = (
                                            int(re.search(r"(\d+) deletion", summary).group(1))
                                            if re.search(r"(\d+) deletion", summary)
                                            else 0
                                        )
                            except:
                                pass

                            # Analyze feature category and score based on branch name and commits
                            branch_lower = branch.lower()
                            if "copilot" in branch_lower or ai_count > 0:
                                feature_category = "AI/Copilot Enhancement"
                                improvement_score = 8
                                unique_features = [
                                    "AI-powered code generation",
                                    "Intelligent completions",
                                    "Enhanced developer experience",
                                ]
                                if "help-pull-request" in branch_lower:
                                    unique_features.append("Professional comparison dashboard")
                                    unique_features.append("Intelligent service management")
                            elif "dashboard" in branch_lower or ui_count > 0:
                                feature_category = "UI/UX Improvements"
                                improvement_score = 7
                                unique_features = [
                                    "Enhanced user interface",
                                    "Better visualization",
                                    "Improved user experience",
                                ]
                            elif "config" in branch_lower or "setup" in branch_lower or config_count > 0:
                                feature_category = "Configuration & Setup"
                                improvement_score = 6
                                unique_features = [
                                    "Configuration improvements",
                                    "Setup enhancements",
                                    "Build system updates",
                                ]
                                if "implement-configuration-updates" in branch_lower:
                                    unique_features = [
                                        "Comprehensive build guide",
                                        "Improved .gitignore",
                                        "Build artifact management",
                                    ]
                            elif "badge" in branch_lower:
                                feature_category = "Documentation/Badges"
                                improvement_score = 4
                                unique_features = ["Documentation updates", "Badge integration", "Project metadata"]
                            elif api_count > 0:
                                feature_category = "API Development"
                                improvement_score = 7
                                unique_features = [
                                    "New API endpoints",
                                    "Enhanced backend services",
                                    "Improved data handling",
                                ]
                            elif lines_added > 100:
                                feature_category = "Major Feature Addition"
                                improvement_score = 8
                                unique_features = [
                                    "Significant code additions",
                                    "New functionality",
                                    "Feature enhancement",
                                ]
                            elif commit_count > 1200:  # Current branch has more commits
                                feature_category = "Active Development"
                                improvement_score = 9
                                unique_features = [
                                    "Latest development",
                                    "Most recent features",
                                    "Current working branch",
                                ]

                    except Exception as e:
                        print(f"Error analyzing branch {branch}: {e}")

                    branch_info = {
                        "name": branch,
                        "commit_count": commit_count,
                        "last_commit": last_commit,
                        "last_commit_message": last_commit_msg,
                        "unique_features": unique_features,
                        "file_changes": file_changes,
                        "lines_added": lines_added,
                        "lines_deleted": lines_deleted,
                        "feature_category": feature_category,
                        "improvement_score": improvement_score,
                    }

                    branch_data.append(branch_info)

                except Exception as e:
                    print(f"Error processing branch {branch}: {e}")
                    continue

            return JSONResponse({"ok": True, "branches": branch_data})

        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.get("/api/bridge/comparison/branch-analysis")
    def get_branch_analysis(branch: str):
        """Get detailed analysis of a specific branch"""
        try:
            # Get current branch for comparison
            current_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=".", text=True
            ).strip()

            # Analyze the target branch
            if branch == current_branch:
                target_ref = "HEAD"
            elif branch == "main":
                target_ref = "main"
            else:
                target_ref = f"origin/{branch}"

            # Get detailed commit analysis
            try:
                if branch == "main":
                    # For main branch, get recent commits
                    commits_output = subprocess.check_output(
                        ["git", "log", "--oneline", "-10", "origin/main"], cwd=".", text=True
                    )
                else:
                    # Get commits unique to this branch compared to origin/main
                    commits_output = subprocess.check_output(
                        ["git", "log", "--oneline", f"origin/main..{target_ref}"], cwd=".", text=True
                    )
            except subprocess.CalledProcessError:
                # If that fails, try alternative approaches
                try:
                    if branch == current_branch:
                        commits_output = subprocess.check_output(
                            ["git", "log", "--oneline", "origin/main..HEAD"], cwd=".", text=True
                        )
                    else:
                        commits_output = subprocess.check_output(
                            ["git", "log", "--oneline", f"origin/main..origin/{branch}"], cwd=".", text=True
                        )
                except subprocess.CalledProcessError:
                    commits_output = ""

            # Analyze key features from commit messages
            key_features = []
            commit_messages = commits_output.strip().split("\n") if commits_output.strip() else []

            for commit in commit_messages:
                if not commit.strip():
                    continue

                msg = commit.split(" ", 1)[1] if " " in commit else commit

                # Categorize commits
                if any(word in msg.lower() for word in ["dashboard", "ui", "interface", "visual"]):
                    key_features.append(
                        {
                            "category": "UI Enhancement",
                            "description": f"User interface improvements: {msg}",
                            "impact": "High",
                        }
                    )
                elif any(word in msg.lower() for word in ["api", "endpoint", "service"]):
                    key_features.append(
                        {
                            "category": "API Development",
                            "description": f"Backend service enhancement: {msg}",
                            "impact": "Medium",
                        }
                    )
                elif any(word in msg.lower() for word in ["fix", "bug", "error"]):
                    key_features.append(
                        {"category": "Bug Fix", "description": f"Code stability improvement: {msg}", "impact": "Medium"}
                    )
                elif any(word in msg.lower() for word in ["feature", "add", "implement"]):
                    key_features.append(
                        {"category": "New Feature", "description": f"Feature addition: {msg}", "impact": "High"}
                    )

            # Get file changes details
            try:
                if branch == "main":
                    # For main branch, show recent changes
                    file_changes_output = subprocess.check_output(
                        ["git", "diff", "--name-status", "origin/main~5", "origin/main"], cwd=".", text=True
                    )
                else:
                    try:
                        file_changes_output = subprocess.check_output(
                            ["git", "diff", "--name-status", f"origin/main...{target_ref}"], cwd=".", text=True
                        )
                    except subprocess.CalledProcessError:
                        if branch == current_branch:
                            file_changes_output = subprocess.check_output(
                                ["git", "diff", "--name-status", "origin/main", "HEAD"], cwd=".", text=True
                            )
                        else:
                            file_changes_output = subprocess.check_output(
                                ["git", "diff", "--name-status", "origin/main", f"origin/{branch}"], cwd=".", text=True
                            )

                file_changes = []
                for line in file_changes_output.strip().split("\n"):
                    if not line.strip():
                        continue
                    if line.startswith(("A", "M", "D")):
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            file_changes.append(
                                {
                                    "status": parts[0],
                                    "file": parts[1],
                                    "additions": 0,  # Would need more detailed analysis
                                    "deletions": 0,
                                }
                            )

            except Exception as e:
                print(f"Error getting file changes: {e}")
                file_changes = []

            # Generate quality metrics (mock data for now, could be enhanced with real analysis)
            quality_metrics = {
                "test_coverage": 75 + (len(key_features) * 2) % 25,  # Mock calculation
                "code_quality_score": 7 + (len(key_features) % 3),
                "performance_score": 6 + (len(file_changes) % 4),
                "maintainability": 8 if len(key_features) > 3 else 6,
            }

            # Generate recommendations
            recommendations = {
                "summary": f"Branch '{branch}' contains {len(key_features)} significant improvements with focus on {key_features[0]['category'] if key_features else 'general development'}.",
                "action_items": [
                    "Review code changes for compatibility",
                    "Test integration with current branch",
                    "Validate new features work as expected",
                    "Consider merging valuable improvements",
                ],
            }

            # Add specific recommendations based on analysis
            if any(f["category"] == "UI Enhancement" for f in key_features):
                recommendations["action_items"].append("Test UI changes across different screen sizes")
            if any(f["category"] == "API Development" for f in key_features):
                recommendations["action_items"].append("Verify API endpoints work with existing clients")

            analysis = {
                "key_features": key_features,
                "quality_metrics": quality_metrics,
                "file_changes": file_changes,
                "recommendations": recommendations,
            }

            return JSONResponse({"ok": True, "analysis": analysis})

        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.get("/api/bridge/comparison/diff")
    async def get_comparison_diff():
        """Get diff between branches."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "diff", "--stat", "HEAD~1..HEAD"], capture_output=True, text=True, timeout=5
            )
            # Parse the diff stat output to extract file changes and summary
            files_changed = []
            summary = {"additions": 0, "deletions": 0, "files_changed": 0}
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) == 2:
                            file_path = parts[0].strip()
                            changes = parts[1].strip()
                            files_changed.append({"file": file_path, "changes": changes})

                # Try to parse the summary line if it exists
                if lines and lines[-1].strip().startswith(f"{len(files_changed)} file"):
                    summary_line = lines[-1]
                    match_files = re.search(r"(\d+) file", summary_line)
                    if match_files:
                        summary["files_changed"] = int(match_files.group(1))
                    match_insertions = re.search(r"(\d+) insertion", summary_line)
                    if match_insertions:
                        summary["additions"] = int(match_insertions.group(1))
                    match_deletions = re.search(r"(\d+) deletion", summary_line)
                    if match_deletions:
                        summary["deletions"] = int(match_deletions.group(1))

            return JSONResponse({"diff": files_changed, "summary": summary})
        except Exception as e:
            return JSONResponse(
                {"diff": [], "summary": {"additions": 0, "deletions": 0, "files_changed": 0}, "error": str(e)}
            )

    @app.get("/api/bridge/comparison/branches")
    async def get_comparison_branches():
        """Get available branches."""
        try:
            import subprocess

            result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, timeout=5)
            branches = []
            if result.returncode == 0:
                for b in result.stdout.split("\n"):
                    stripped_b = b.strip()
                    if stripped_b and not stripped_b.startswith("remotes/origin/HEAD"):
                        # Remove remote prefix and '*' for current branch marker
                        branch_name = stripped_b.replace("remotes/origin/", "").replace("* ", "")
                        if branch_name:
                            branches.append(branch_name)

            # Ensure 'main' is included if not found and return unique branches
            if not branches:
                return JSONResponse({"branches": ["main"]})
            elif "main" not in branches:
                branches.insert(0, "main")

            return JSONResponse({"branches": list(dict.fromkeys(branches))})  # Return unique branches preserving order
        except Exception as e:
            # Fallback to 'main' if any error occurs
            return JSONResponse({"branches": ["main"], "error": str(e)})

    @app.get("/api/bridge/comparison/commits")
    async def get_comparison_commits():
        """Get commit history."""
        try:
            import subprocess

            result = subprocess.run(["git", "log", "--oneline", "-10"], capture_output=True, text=True, timeout=5)
            commits = []
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        parts = line.split(" ", 1)
                        if len(parts) == 2:
                            commits.append(
                                {
                                    "hash": parts[0],
                                    "short_hash": parts[0][:7],  # Add short hash
                                    "message": parts[1],
                                    "date": "",  # Placeholder, as --oneline doesn't easily provide date
                                }
                            )
            return JSONResponse({"commits": commits})
        except Exception as e:
            return JSONResponse({"commits": [], "error": str(e)})
