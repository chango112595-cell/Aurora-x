from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, Literal
import time
from aurora_x.bridge.pipeline import compile_from_nl, compile_from_spec, compile_from_nl_project
from aurora_x.bridge.deploy import deploy as deploy_fn

class NLBody(BaseModel):
    prompt: str

class SpecBody(BaseModel):
    path: str

class RepoInfo(BaseModel):
    owner: str
    name: str
    branch: str = "main"

class ProjectBody(BaseModel):
    prompt: str
    repo: Optional[RepoInfo] = None
    stack: Optional[str] = None
    mode: Literal["commit", "pr"] = "commit"

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
        
        # Basic planner logic to determine if UI/API components are needed
        prompt_lower = body.prompt.lower()
        stack_lower = body.stack.lower() if body.stack else ""
        
        # Determine project components based on stack and prompt keywords
        components = {
            "ui_needed": False,
            "api_needed": False,
            "database_needed": False,
            "auth_needed": False
        }
        
        # UI detection patterns - use word boundaries for better matching
        ui_patterns = ["frontend", "react", "vue", "angular", "interface", 
                       "dashboard", "website", "html", "css", "component", "page", 
                       "user interface", "web ui", "webapp", "web app"]
        if any(pattern in prompt_lower for pattern in ui_patterns) or \
           any(pattern in stack_lower for pattern in ["react", "vue", "angular", "nextjs"]) or \
           " ui " in f" {prompt_lower} ":  # Check for UI as a standalone word
            components["ui_needed"] = True
        
        # API detection patterns  
        api_patterns = ["api", "backend", "rest", "endpoint", "server", "flask", 
                        "fastapi", "express", "django", "route", "crud"]
        if any(pattern in prompt_lower for pattern in api_patterns) or \
           any(pattern in stack_lower for pattern in ["flask", "fastapi", "express", "django"]):
            components["api_needed"] = True
        
        # Database detection patterns
        db_patterns = ["database", "db", "sql", "postgres", "mysql", "mongodb", 
                       "store", "persist", "save data"]
        if any(pattern in prompt_lower for pattern in db_patterns):
            components["database_needed"] = True
        
        # Auth detection patterns
        auth_patterns = ["auth", "login", "user", "account", "signup", "signin", 
                         "authentication", "authorization"]
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
        if body.mode == "pr":
            # Call PR creation function (stub for now)
            pr_result = pr_create(
                prompt=enhanced_prompt,
                repo_info=body.repo.dict() if body.repo else None,
                components=components
            )
            return JSONResponse({
                "ok": True,
                "message": "PR creation initiated",
                "mode": "pr",
                "components": components,
                **pr_result
            })
        else:
            # Regular commit mode - use compile_from_nl_project
            # Pass the enhanced context to the compiler
            res = compile_from_nl_project(
                prompt=enhanced_prompt,
                repo_info=body.repo.dict() if body.repo else None,
                stack=body.stack,
                components=components
            )
            
            return JSONResponse({
                **res.__dict__,
                "components": components,
                "mode": "commit"
            })


def pr_create(prompt: str, repo_info: Optional[Dict] = None, components: Optional[Dict] = None) -> Dict:
    """
    Stub function for PR creation mode.
    Will be implemented in the next iteration to handle:
    - Creating feature branch
    - Generating code changes
    - Creating pull request via GitHub API
    """
    return {
        "pr_status": "stub",
        "pr_message": "PR creation not yet implemented",
        "branch_name": f"feature/aurora-{int(time.time())}",
        "repo_info": repo_info,
        "planned_components": components
    }