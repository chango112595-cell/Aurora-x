"""
Universal Code Synthesis Engine (UCSE) for Aurora-X
Complete code synthesis pipeline with multi-project support
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# ========== Component 1: Multi-Intent Parser ==========

class ProjectType(Enum):
    """Supported project types for synthesis"""
    UI_FRONTEND = "ui_frontend"  # React, Vue, HTML/CSS/JS
    API_BACKEND = "api_backend"  # Flask, FastAPI, Express
    AI_ML = "ai_ml"  # Model training, data processing
    DATABASE = "database"  # Schema design, migrations
    FULLSTACK = "fullstack"  # Complete applications
    LIBRARY = "library"  # Python/JS libraries
    CLI_TOOL = "cli_tool"  # Command-line tools
    MICROSERVICE = "microservice"  # Containerized services


@dataclass
class ParsedIntent:
    """Result of intent parsing"""
    project_type: ProjectType
    framework: str  # e.g., "react", "flask", "fastapi", "pytorch"
    language: str  # "python", "javascript", "typescript"
    features: list[str]  # ["auth", "database", "api", "ui"]
    description: str
    entities: dict[str, Any]  # Extracted entities like route names, models, etc.


class MultiIntentParser:
    """Parse natural language prompts to determine project intent"""

    # Intent patterns for different project types
    PATTERNS = {
        ProjectType.UI_FRONTEND: [
            r"\b(react|vue|angular|frontend|ui|interface|dashboard|website|webpage|html|css)\b",
            r"\b(component|button|form|modal|navbar|sidebar|layout)\b"
        ],
        ProjectType.API_BACKEND: [
            r"\b(api|backend|rest|restful|endpoint|server|flask|fastapi|express|django)\b",
            r"\b(route|middleware|controller|service|crud)\b"
        ],
        ProjectType.AI_ML: [
            r"\b(ai|ml|model|train|predict|neural|network|tensorflow|pytorch|sklearn)\b",
            r"\b(dataset|features|classification|regression|clustering)\b"
        ],
        ProjectType.DATABASE: [
            r"\b(database|db|schema|migration|sql|postgres|mysql|mongodb)\b",
            r"\b(table|column|index|constraint|relationship)\b"
        ],
        ProjectType.FULLSTACK: [
            r"\b(fullstack|full-stack|complete app|entire application)\b",
            r"\b(frontend.*backend|backend.*frontend|ui.*api|api.*ui)\b"
        ],
        ProjectType.CLI_TOOL: [
            r"\b(cli|command|tool|script|automation|terminal)\b",
            r"\b(argparse|click|arguments|options)\b"
        ]
    }

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "react": r"\b(react|jsx|nextjs|next\.js)\b",
        "vue": r"\b(vue|vuejs|vue\.js|nuxt)\b",
        "flask": r"\b(flask|jinja|werkzeug)\b",
        "fastapi": r"\b(fastapi|fast api|uvicorn|pydantic)\b",
        "express": r"\b(express|expressjs|express\.js)\b",
        "django": r"\b(django|drf|django rest)\b",
        "pytorch": r"\b(pytorch|torch|neural)\b",
        "tensorflow": r"\b(tensorflow|tf|keras)\b"
    }

    def parse(self, prompt: str) -> ParsedIntent:
        """Parse a natural language prompt to determine project intent"""
        prompt_lower = prompt.lower()

        # Detect project type
        project_type = self._detect_project_type(prompt_lower)

        # Detect framework
        framework = self._detect_framework(prompt_lower, project_type)

        # Determine language based on framework/type
        language = self._determine_language(framework, project_type)

        # Extract features
        features = self._extract_features(prompt_lower)

        # Extract entities (routes, models, etc.)
        entities = self._extract_entities(prompt)

        return ParsedIntent(
            project_type=project_type,
            framework=framework,
            language=language,
            features=features,
            description=prompt.strip(),
            entities=entities
        )

    def _detect_project_type(self, prompt: str) -> ProjectType:
        """Detect the main project type from prompt"""
        scores = {}

        for ptype, patterns in self.PATTERNS.items():
            score = sum(1 for pattern in patterns if re.search(pattern, prompt, re.I))
            scores[ptype] = score

        # Check for fullstack explicitly
        if scores.get(ProjectType.FULLSTACK, 0) > 0:
            return ProjectType.FULLSTACK

        # If both frontend and backend detected, it's fullstack
        if scores.get(ProjectType.UI_FRONTEND, 0) > 0 and scores.get(ProjectType.API_BACKEND, 0) > 0:
            return ProjectType.FULLSTACK

        # Return highest scoring type
        if scores:
            return max(scores, key=scores.get)

        # Default to API backend for generic requests
        return ProjectType.API_BACKEND

    def _detect_framework(self, prompt: str, project_type: ProjectType) -> str:
        """Detect framework from prompt"""
        for framework, pattern in self.FRAMEWORK_PATTERNS.items():
            if re.search(pattern, prompt, re.I):
                return framework

        # Default frameworks by project type
        defaults = {
            ProjectType.UI_FRONTEND: "react",
            ProjectType.API_BACKEND: "flask",
            ProjectType.AI_ML: "pytorch",
            ProjectType.DATABASE: "postgresql",
            ProjectType.FULLSTACK: "flask-react",
            ProjectType.CLI_TOOL: "click",
            ProjectType.MICROSERVICE: "fastapi"
        }
        return defaults.get(project_type, "python")

    def _determine_language(self, framework: str, project_type: ProjectType) -> str:
        """Determine programming language based on framework/type"""
        js_frameworks = ["react", "vue", "angular", "express", "nextjs", "nuxt"]

        if framework in js_frameworks:
            return "javascript"
        elif project_type == ProjectType.UI_FRONTEND and framework not in ["flask", "django"]:
            return "javascript"
        else:
            return "python"

    def _extract_features(self, prompt: str) -> list[str]:
        """Extract feature requirements from prompt"""
        features = []

        feature_keywords = {
            "auth": ["auth", "login", "user", "signup", "signin", "authentication"],
            "database": ["database", "db", "sql", "postgres", "mysql", "mongodb"],
            "api": ["api", "endpoint", "rest", "graphql", "routes"],
            "ui": ["ui", "interface", "frontend", "dashboard", "form", "button"],
            "realtime": ["realtime", "websocket", "socket", "live", "streaming"],
            "testing": ["test", "testing", "unittest", "pytest", "jest"],
            "docker": ["docker", "container", "kubernetes", "k8s"],
            "payment": ["payment", "stripe", "paypal", "checkout", "billing"]
        }

        for feature, keywords in feature_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                features.append(feature)

        return features

    def _extract_entities(self, prompt: str) -> dict[str, Any]:
        """Extract specific entities from prompt"""
        entities = {}

        # Extract route names (e.g., /users, /products)
        route_pattern = r"(?:/\w+|route\s+(\w+)|endpoint\s+(\w+))"
        routes = re.findall(route_pattern, prompt, re.I)
        if routes:
            entities["routes"] = [r for r in routes if r]

        # Extract model/table names
        model_pattern = r"\b(user|product|order|customer|item|post|comment|article)s?\b"
        models = re.findall(model_pattern, prompt, re.I)
        if models:
            entities["models"] = list(set(models))

        # Extract port numbers
        port_pattern = r"\b(port\s+)?(\d{4,5})\b"
        port_match = re.search(port_pattern, prompt, re.I)
        if port_match:
            entities["port"] = int(port_match.group(2))

        return entities


# ========== Component 2: Blueprint Engine ==========

class BlueprintEngine:
    """Generate project structure and configuration files"""

    def generate_structure(self, intent: ParsedIntent, run_dir: Path) -> dict[str, str]:
        """Generate complete project structure based on intent"""
        files = {}

        # Base structure depends on project type
        if intent.project_type == ProjectType.FULLSTACK:
            files.update(self._fullstack_structure(intent))
        elif intent.project_type == ProjectType.UI_FRONTEND:
            files.update(self._frontend_structure(intent))
        elif intent.project_type == ProjectType.API_BACKEND:
            files.update(self._backend_structure(intent))
        elif intent.project_type == ProjectType.AI_ML:
            files.update(self._ml_structure(intent))
        elif intent.project_type == ProjectType.DATABASE:
            files.update(self._database_structure(intent))
        elif intent.project_type == ProjectType.CLI_TOOL:
            files.update(self._cli_structure(intent))
        else:
            files.update(self._default_structure(intent))

        # Add common files
        files["README.md"] = self._generate_readme(intent)
        files[".gitignore"] = self._generate_gitignore(intent)

        # Add Docker support if requested
        if "docker" in intent.features:
            files["Dockerfile"] = self._generate_dockerfile(intent)
            files["docker-compose.yml"] = self._generate_docker_compose(intent)

        return files

    def _fullstack_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate fullstack project structure"""
        return {
            "backend/app.py": "",
            "backend/requirements.txt": self._python_requirements(intent.features),
            "backend/config.py": "",
            "backend/models.py": "",
            "backend/routes.py": "",
            "frontend/package.json": self._package_json(intent.framework, intent.features),
            "frontend/src/index.js": "",
            "frontend/src/App.js": "",
            "frontend/src/components/Header.js": "",
            "frontend/public/index.html": ""
        }

    def _frontend_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate frontend project structure"""
        return {
            "package.json": self._package_json(intent.framework, intent.features),
            "src/index.js": "",
            "src/App.js": "",
            "src/components/.gitkeep": "",
            "src/styles/main.css": "",
            "public/index.html": "",
            "webpack.config.js": "" if intent.framework != "react" else "",
            "vite.config.js": "" if intent.framework == "react" else ""
        }

    def _backend_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate backend project structure"""
        return {
            "app.py": "" if intent.framework == "flask" else "main.py",
            "requirements.txt": self._python_requirements(intent.features),
            "config.py": "",
            "models.py": "" if "database" in intent.features else "",
            "routes.py": "",
            "middleware.py": "",
            "tests/test_app.py": "",
            "tests/test_routes.py": ""
        }

    def _ml_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate ML project structure"""
        return {
            "train.py": "",
            "predict.py": "",
            "model.py": "",
            "data_loader.py": "",
            "utils.py": "",
            "requirements.txt": self._ml_requirements(),
            "config.yaml": "",
            "notebooks/exploration.ipynb": "",
            "data/.gitkeep": "",
            "models/.gitkeep": ""
        }

    def _database_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate database project structure"""
        return {
            "schema.sql": "",
            "migrations/001_initial.sql": "",
            "migrations/002_indexes.sql": "",
            "seeds/seed_data.sql": "",
            "queries/common_queries.sql": "",
            "config/database.yml": "",
            "scripts/backup.sh": "",
            "scripts/restore.sh": ""
        }

    def _cli_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Generate CLI tool structure"""
        return {
            "cli.py": "",
            "commands.py": "",
            "utils.py": "",
            "config.py": "",
            "requirements.txt": "click>=8.0\ncolorama>=0.4\n",
            "setup.py": "",
            "tests/test_cli.py": ""
        }

    def _default_structure(self, intent: ParsedIntent) -> dict[str, str]:
        """Default project structure"""
        return {
            "main.py": "",
            "requirements.txt": "",
            "config.py": "",
            "utils.py": "",
            "tests/test_main.py": ""
        }

    def _generate_readme(self, intent: ParsedIntent) -> str:
        """Generate README.md content"""
        return f"""# {intent.description}

## Project Type
{intent.project_type.value.replace('_', ' ').title()}

## Technology Stack
- Language: {intent.language.title()}
- Framework: {intent.framework.title()}
- Features: {', '.join(intent.features)}

## Setup Instructions

### Prerequisites
{"- Node.js 18+" if intent.language == "javascript" else "- Python 3.9+"}
{"- npm or yarn" if intent.language == "javascript" else "- pip"}

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install dependencies:
```bash
{"npm install" if intent.language == "javascript" else "pip install -r requirements.txt"}
```

3. Run the application:
```bash
{"npm start" if intent.language == "javascript" else "python app.py"}
```

## Project Structure
```
.
├── {'src/' if intent.language == 'javascript' else ''}
├── {'app.py' if intent.framework == 'flask' else 'main.py'}
├── {'package.json' if intent.language == 'javascript' else 'requirements.txt'}
├── tests/
└── README.md
```

## API Documentation
{self._generate_api_docs(intent) if "api" in intent.features else "N/A"}

## Testing
```bash
{"npm test" if intent.language == "javascript" else "python -m pytest"}
```

## License
MIT

---
Generated by Aurora-X Synthesis Engine
"""

    def _generate_api_docs(self, intent: ParsedIntent) -> str:
        """Generate basic API documentation"""
        routes = intent.entities.get("routes", ["/"])
        docs = "\n### Endpoints\n\n"
        for route in routes:
            docs += f"- `GET {route}` - Description\n"
            docs += f"- `POST {route}` - Description\n"
        return docs

    def _generate_gitignore(self, intent: ParsedIntent) -> str:
        """Generate .gitignore file"""
        base = """# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.env.local
"""

        if intent.language == "python":
            base += """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
pip-log.txt
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
"""

        if intent.language == "javascript":
            base += """
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
dist/
build/
.cache/
"""

        return base

    def _generate_dockerfile(self, intent: ParsedIntent) -> str:
        """Generate Dockerfile"""
        if intent.language == "python":
            return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {intent.entities.get('port', 8000)}

CMD ["python", "{"app.py" if intent.framework == "flask" else "main.py"}"]
"""
        else:
            return f"""FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE {intent.entities.get('port', 3000)}

CMD ["npm", "start"]
"""

    def _generate_docker_compose(self, intent: ParsedIntent) -> str:
        """Generate docker-compose.yml"""
        return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "{intent.entities.get('port', 8000)}:{intent.entities.get('port', 8000)}"
    environment:
      - NODE_ENV=production
    {"depends_on:" if "database" in intent.features else ""}
{"      - db" if "database" in intent.features else ""}
{'''
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: app_db
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:''' if "database" in intent.features else ""}
"""

    def _python_requirements(self, features: list[str]) -> str:
        """Generate Python requirements.txt"""
        reqs = []

        # Base requirements
        reqs.extend(["flask>=2.3.0", "python-dotenv>=1.0.0"])

        # Feature-specific requirements
        if "database" in features:
            reqs.extend(["sqlalchemy>=2.0.0", "psycopg2-binary>=2.9.0"])
        if "auth" in features:
            reqs.extend(["flask-login>=0.6.0", "flask-jwt-extended>=4.5.0"])
        if "api" in features:
            reqs.extend(["flask-restful>=0.3.10", "marshmallow>=3.20.0"])
        if "testing" in features:
            reqs.extend(["pytest>=7.4.0", "pytest-cov>=4.1.0"])

        return "\n".join(reqs)

    def _ml_requirements(self) -> str:
        """Generate ML requirements.txt"""
        return """torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
jupyter>=1.0.0
tensorboard>=2.13.0
"""

    def _package_json(self, framework: str, features: list[str]) -> str:
        """Generate package.json"""
        deps = {}
        dev_deps = {}

        if framework == "react":
            deps = {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.15.0"
            }
            dev_deps = {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.4.0"
            }
        elif framework == "vue":
            deps = {
                "vue": "^3.3.0"
            }
            dev_deps = {
                "@vitejs/plugin-vue": "^4.2.0",
                "vite": "^4.4.0"
            }

        # Add feature-specific dependencies
        if "ui" in features:
            deps["@mui/material"] = "^5.14.0"
        if "api" in features:
            deps["axios"] = "^1.5.0"

        package = {
            "name": "aurora-generated-app",
            "version": "1.0.0",
            "description": "Generated by Aurora-X",
            "scripts": {
                "start": "vite",
                "build": "vite build",
                "test": "jest"
            },
            "dependencies": deps,
            "devDependencies": dev_deps
        }

        return json.dumps(package, indent=2)


# ========== Component 3: Dynamic Synthesizer ==========

class DynamicSynthesizer:
    """Generate actual code based on templates and patterns"""

    def __init__(self):
        self.templates = self._load_templates()

    def synthesize_code(self, intent: ParsedIntent, files: dict[str, str]) -> dict[str, str]:
        """Generate code for all project files"""
        completed_files = {}

        for file_path, _ in files.items():
            if file_path.endswith('.py'):
                content = self._generate_python_file(file_path, intent)
            elif file_path.endswith('.js') or file_path.endswith('.jsx'):
                content = self._generate_javascript_file(file_path, intent)
            elif file_path.endswith('.sql'):
                content = self._generate_sql_file(file_path, intent)
            elif file_path.endswith('.html'):
                content = self._generate_html_file(file_path, intent)
            elif file_path.endswith('.css'):
                content = self._generate_css_file(file_path, intent)
            elif file_path.endswith('.json') or file_path.endswith('.yml') or file_path.endswith('.yaml'):
                content = files[file_path]  # Already generated
            elif file_path.endswith('.md'):
                content = files[file_path]  # Already generated
            elif file_path.endswith('.gitignore') or file_path.endswith('Dockerfile'):
                content = files[file_path]  # Already generated
            else:
                content = files[file_path] or ""  # Empty or placeholder

            completed_files[file_path] = content

        return completed_files

    def _load_templates(self) -> dict[str, str]:
        """Load code templates"""
        return {
            "flask_app": self._flask_app_template(),
            "react_app": self._react_app_template(),
            "fastapi_app": self._fastapi_app_template(),
            "cli_tool": self._cli_tool_template(),
            "ml_model": self._ml_model_template()
        }

    def _generate_python_file(self, file_path: str, intent: ParsedIntent) -> str:
        """Generate Python code based on file type"""
        file_name = Path(file_path).name

        if file_name in ["app.py", "main.py"]:
            if intent.framework == "flask":
                return self._flask_app_code(intent)
            elif intent.framework == "fastapi":
                return self._fastapi_app_code(intent)
            else:
                return self._generic_python_main(intent)
        elif file_name == "models.py":
            return self._models_code(intent)
        elif file_name == "routes.py":
            return self._routes_code(intent)
        elif file_name == "config.py":
            return self._config_code(intent)
        elif file_name == "cli.py":
            return self._cli_code(intent)
        elif file_name == "train.py":
            return self._ml_train_code(intent)
        elif file_name.startswith("test_"):
            return self._test_code(intent, file_name)
        else:
            return f'"""Generated by Aurora-X: {file_name}"""\n\n# TODO: Implement {file_name}'

    def _generate_javascript_file(self, file_path: str, intent: ParsedIntent) -> str:
        """Generate JavaScript/React code"""
        file_name = Path(file_path).name

        if file_name == "App.js" or file_name == "App.jsx":
            return self._react_app_code(intent)
        elif file_name == "index.js":
            return self._js_index_code(intent)
        elif "component" in file_name.lower():
            return self._react_component_code(intent, file_name)
        else:
            return f"// Generated by Aurora-X: {file_name}\n\n// TODO: Implement"

    def _generate_sql_file(self, file_path: str, intent: ParsedIntent) -> str:
        """Generate SQL code"""
        file_name = Path(file_path).name

        if "schema" in file_name:
            return self._sql_schema_code(intent)
        elif "migration" in file_name:
            return self._sql_migration_code(intent)
        else:
            return f"-- Generated by Aurora-X: {file_name}\n\n-- TODO: Implement"

    def _generate_html_file(self, file_path: str, intent: ParsedIntent) -> str:
        """Generate HTML code"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{intent.description[:50]}</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div id="root"></div>
    <script src="src/index.js"></script>
</body>
</html>"""

    def _generate_css_file(self, file_path: str, intent: ParsedIntent) -> str:
        """Generate CSS code"""
        return """/* Aurora-X Generated Styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    line-height: 1.6;
    color: var(--dark-color);
    background-color: var(--light-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}
"""

    def _flask_app_code(self, intent: ParsedIntent) -> str:
        """Generate Flask application code"""
        features_imports = []
        features_setup = []

        if "database" in intent.features:
            features_imports.append("from flask_sqlalchemy import SQLAlchemy")
            features_setup.append("db = SQLAlchemy(app)")

        if "auth" in intent.features:
            features_imports.append("from flask_login import LoginManager")
            features_setup.append("login_manager = LoginManager(app)")

        return f"""\"\"\"
Flask Application
{intent.description}
Generated by Aurora-X Synthesis Engine
\"\"\"

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
{chr(10).join(features_imports) if features_imports else ""}

def create_app():
    \"\"\"Create and configure Flask application\"\"\"
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Enable CORS for API endpoints
    CORS(app)

    {(chr(10) + "    ").join(features_setup) if features_setup else ""}

    @app.route('/')
    def index():
        \"\"\"Home page\"\"\"
        return jsonify({{
            'message': 'Welcome to {intent.description[:50]}',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'running'
        }})

    @app.route('/health')
    def health_check():
        \"\"\"Health check endpoint\"\"\"
        return jsonify({{'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}})

    {self._generate_route_handlers(intent.entities.get('routes', []))}

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({{'error': 'Not found'}}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({{'error': 'Internal server error'}}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', {intent.entities.get('port', 8000)}))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    print(f"🚀 Starting Flask application on port {{port}}...")
    print(f"📝 Description: {intent.description[:100]}")
    print(f"🔧 Features: {', '.join(intent.features)}")

    app.run(host='0.0.0.0', port=port, debug=debug)
"""

    def _generate_route_handlers(self, routes: list[str]) -> str:
        """Generate route handler functions"""
        if not routes:
            return ""

        handlers = []
        for route in routes:
            route_name = route.strip('/').replace('/', '_') or 'root'
            handlers.append(f"""@app.route('/{route}')
    def {route_name}_handler():
        \"\"\"Handler for /{route} endpoint\"\"\"
        return jsonify({{
            'endpoint': '/{route}',
            'method': request.method,
            'timestamp': datetime.utcnow().isoformat()
        }})""")

        return "\n    \n    ".join(handlers)

    def _fastapi_app_code(self, intent: ParsedIntent) -> str:
        """Generate FastAPI application code"""
        return f"""\"\"\"
FastAPI Application
{intent.description}
Generated by Aurora-X Synthesis Engine
\"\"\"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="{intent.description[:50]}",
    description="{intent.description}",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

@app.get("/")
async def root():
    \"\"\"Root endpoint\"\"\"
    return {{
        "message": "Welcome to {intent.description[:50]}",
        "timestamp": datetime.utcnow(),
        "docs": "/docs"
    }}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())

{self._generate_fastapi_routes(intent.entities.get('routes', []))}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", {intent.entities.get('port', 8000)}))

    print(f"🚀 Starting FastAPI application on port {{port}}...")
    print(f"📝 Description: {intent.description[:100]}")
    print(f"📚 API Documentation: http://localhost:{{port}}/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
"""

    def _generate_fastapi_routes(self, routes: list[str]) -> str:
        """Generate FastAPI route handlers"""
        if not routes:
            return ""

        handlers = []
        for route in routes:
            route_name = route.strip('/').replace('/', '_') or 'root'
            handlers.append(f"""@app.get("/{route}")
async def get_{route_name}():
    \"\"\"GET handler for /{route}\"\"\"
    return {{"endpoint": "/{route}", "method": "GET"}}

@app.post("/{route}")
async def post_{route_name}(data: dict):
    \"\"\"POST handler for /{route}\"\"\"
    return {{"endpoint": "/{route}", "method": "POST", "data": data}}""")

        return "\n\n".join(handlers)

    def _react_app_code(self, intent: ParsedIntent) -> str:
        """Generate React App component"""
        return f"""import React, {{ useState, useEffect }} from 'react';
import './App.css';

function App() {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {{
    // Fetch initial data
    fetchData();
  }}, []);

  const fetchData = async () => {{
    try {{
      setLoading(true);
      const response = await fetch('/api/');
      if (!response.ok) {{
        throw new Error('Failed to fetch data');
      }}
      const json = await response.json();
      setData(json);
    }} catch (err) {{
      setError(err.message);
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <div className="App">
      <header className="App-header">
        <h1>{intent.description[:50]}</h1>
        <p>Generated by Aurora-X Synthesis Engine</p>
      </header>

      <main className="App-main">
        {{loading && <div className="loading">Loading...</div>}}
        {{error && <div className="error">Error: {{error}}</div>}}
        {{data && (
          <div className="data-display">
            <pre>{{JSON.stringify(data, null, 2)}}</pre>
          </div>
        )}}

        <div className="features">
          <h2>Features</h2>
          <ul>
            {chr(10).join(f'            <li>{feature}</li>' for feature in intent.features) if intent.features else '            <li>No features specified</li>'}
          </ul>
        </div>
      </main>

      <footer className="App-footer">
        <p>&copy; 2024 Aurora-X Generated Application</p>
      </footer>
    </div>
  );
}}

export default App;
"""

    def _models_code(self, intent: ParsedIntent) -> str:
        """Generate database models code"""
        models = intent.entities.get('models', ['User', 'Item'])

        code = """\"\"\"
Database Models
Generated by Aurora-X Synthesis Engine
\"\"\"

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

"""

        for model in models:
            model_name = model.capitalize()
            code += f"""
class {model_name}(Base):
    __tablename__ = '{model.lower()}s'

    id = Column(Integer, primary_key=True)
    {"username = Column(String(80), unique=True, nullable=False)" if model.lower() == "user" else "name = Column(String(100), nullable=False)"}
    {"email = Column(String(120), unique=True, nullable=False)" if model.lower() == "user" else "description = Column(Text)"}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    {"is_active = Column(Boolean, default=True)" if model.lower() == "user" else "is_available = Column(Boolean, default=True)"}

    def __repr__(self):
        return f"<{model_name} {{self.id}}>"

    def to_dict(self):
        return {{
            'id': self.id,
            '{"username" if model.lower() == "user" else "name"}': self.{"username" if model.lower() == "user" else "name"},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}
"""

        return code

    def _routes_code(self, intent: ParsedIntent) -> str:
        """Generate routes/endpoints code"""
        return """\"\"\"
API Routes
Generated by Aurora-X Synthesis Engine
\"\"\"

from flask import Blueprint, jsonify, request, abort
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
def status():
    \"\"\"API status endpoint\"\"\"
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/items', methods=['GET', 'POST'])
def items():
    \"\"\"Items CRUD endpoint\"\"\"
    if request.method == 'GET':
        # TODO: Implement GET logic
        return jsonify({'items': [], 'total': 0})

    elif request.method == 'POST':
        # TODO: Implement POST logic
        data = request.get_json()
        return jsonify({'message': 'Item created', 'data': data}), 201

@api_bp.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def item_detail(item_id):
    \"\"\"Single item CRUD endpoint\"\"\"
    if request.method == 'GET':
        # TODO: Implement GET logic
        return jsonify({'id': item_id, 'name': 'Sample Item'})

    elif request.method == 'PUT':
        # TODO: Implement PUT logic
        data = request.get_json()
        return jsonify({'message': f'Item {item_id} updated', 'data': data})

    elif request.method == 'DELETE':
        # TODO: Implement DELETE logic
        return jsonify({'message': f'Item {item_id} deleted'}), 204

# Error handlers
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
"""

    def _config_code(self, intent: ParsedIntent) -> str:
        """Generate configuration code"""
        return f"""\"\"\"
Application Configuration
Generated by Aurora-X Synthesis Engine
\"\"\"

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    \"\"\"Application configuration\"\"\"

    # Application
    APP_NAME: str = "{intent.description[:30]}"
    DEBUG: bool = os.environ.get('DEBUG', 'true').lower() == 'true'
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Server
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', {intent.entities.get('port', 8000)}))

{'    # Database' if "database" in intent.features else ""}
{'    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///app.db")' if "database" in intent.features else ""}
{'    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False' if "database" in intent.features else ""}

{'    # Authentication' if "auth" in intent.features else ""}
{'    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)' if "auth" in intent.features else ""}
{'    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour' if "auth" in intent.features else ""}

    # Features
    FEATURES_ENABLED = {intent.features}

    @classmethod
    def from_env(cls) -> 'Config':
        \"\"\"Create config from environment variables\"\"\"
        return cls()

# Global config instance
config = Config.from_env()
"""

    def _cli_code(self, intent: ParsedIntent) -> str:
        """Generate CLI tool code"""
        return f"""#!/usr/bin/env python3
\"\"\"
Command-Line Interface
{intent.description}
Generated by Aurora-X Synthesis Engine
\"\"\"

import click
import sys
from pathlib import Path

@click.group()
@click.version_option(version='1.0.0')
def cli():
    \"\"\"
    {intent.description[:100]}
    \"\"\"
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def process(input_file, output, verbose):
    \"\"\"Process input file\"\"\"
    if verbose:
        click.echo(f"Processing: {{input_file}}")

    # TODO: Implement processing logic
    input_path = Path(input_file)

    if output:
        click.echo(f"Output will be saved to: {{output}}")

    click.echo(click.style("✅ Processing complete!", fg='green', bold=True))

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'txt']), default='json')
def list(format):
    \"\"\"List available items\"\"\"
    click.echo(f"Listing items in {{format}} format...")
    # TODO: Implement listing logic
    click.echo("No items found.")

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to reset?')
def reset():
    \"\"\"Reset application state\"\"\"
    click.echo("Resetting...")
    # TODO: Implement reset logic
    click.echo(click.style("Reset complete!", fg='yellow'))

if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        click.echo(click.style(f"Error: {{e}}", fg='red', bold=True), err=True)
        sys.exit(1)
"""

    def _ml_train_code(self, intent: ParsedIntent) -> str:
        """Generate ML training code"""
        return """\"\"\"
Machine Learning Training Script
Generated by Aurora-X Synthesis Engine
\"\"\"

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class CustomDataset(Dataset):
    \"\"\"Custom dataset for training\"\"\"

    def __init__(self, data_path):
        # TODO: Implement data loading
        self.data = []
        self.labels = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

class SimpleModel(nn.Module):
    \"\"\"Simple neural network model\"\"\"

    def __init__(self, input_size=10, hidden_size=128, output_size=2):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x

def train_model(model, dataloader, criterion, optimizer, epochs=10):
    \"\"\"Train the model\"\"\"
    model.train()

    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (data, labels) in enumerate(dataloader):
            optimizer.zero_grad()

            outputs = model(data)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        avg_loss = total_loss / len(dataloader)

        print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')

    return model

def save_model(model, path='models/model.pth'):
    \"\"\"Save trained model\"\"\"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'timestamp': datetime.utcnow().isoformat()
    }, path)
    print(f"Model saved to {path}")

def main():
    \"\"\"Main training pipeline\"\"\"
    print("🤖 Starting ML Training Pipeline")
    print("Generated by Aurora-X Synthesis Engine")

    # Hyperparameters
    batch_size = 32
    learning_rate = 0.001
    epochs = 10

    # TODO: Load real data
    # dataset = CustomDataset('data/train.csv')
    # dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = SimpleModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Train
    # model = train_model(model, dataloader, criterion, optimizer, epochs)

    # Save model
    # save_model(model)

    print("✅ Training complete!")

if __name__ == '__main__':
    main()
"""

    def _test_code(self, intent: ParsedIntent, file_name: str) -> str:
        """Generate test code"""
        return f"""\"\"\"
Tests for {file_name.replace('test_', '').replace('.py', '')}
Generated by Aurora-X Synthesis Engine
\"\"\"

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMain(unittest.TestCase):
    \"\"\"Test cases for main functionality\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        self.test_data = {{'key': 'value'}}

    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass

    def test_basic_functionality(self):
        \"\"\"Test basic functionality\"\"\"
        # TODO: Implement actual tests
        self.assertTrue(True)

    def test_edge_cases(self):
        \"\"\"Test edge cases\"\"\"
        # TODO: Implement edge case tests
        self.assertIsNotNone(self.test_data)

    def test_error_handling(self):
        \"\"\"Test error handling\"\"\"
        # TODO: Implement error handling tests
        with self.assertRaises(Exception):
            raise Exception("Test exception")

if __name__ == '__main__':
    unittest.main()
"""

    def _js_index_code(self, intent: ParsedIntent) -> str:
        """Generate JavaScript index file"""
        if intent.framework == "react":
            return """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        else:
            return """// Application entry point
// Generated by Aurora-X Synthesis Engine

document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');

    // TODO: Initialize application
});
"""

    def _react_component_code(self, intent: ParsedIntent, file_name: str) -> str:
        """Generate React component code"""
        component_name = file_name.replace('.js', '').replace('.jsx', '')
        return f"""import React, {{ useState, useEffect }} from 'react';

const {component_name} = ({{ props }}) => {{
  const [state, setState] = useState({{}});

  useEffect(() => {{
    // Component mounted
    return () => {{
      // Component unmounted - cleanup
    }};
  }}, []);

  return (
    <div className="{component_name.lower()}">
      <h2>{component_name}</h2>
      {{/* TODO: Implement component */}}
    </div>
  );
}};

export default {component_name};
"""

    def _sql_schema_code(self, intent: ParsedIntent) -> str:
        """Generate SQL schema code"""
        models = intent.entities.get('models', ['users', 'items'])

        schema = "-- Database Schema\n-- Generated by Aurora-X Synthesis Engine\n\n"

        for model in models:
            table_name = model.lower() if model.endswith('s') else f"{model.lower()}s"
            schema += f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    {"username VARCHAR(80) UNIQUE NOT NULL," if "user" in model.lower() else "name VARCHAR(100) NOT NULL,"}
    {"email VARCHAR(120) UNIQUE NOT NULL," if "user" in model.lower() else "description TEXT,"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP{"," if "user" in model.lower() else ""}
    {"is_active BOOLEAN DEFAULT TRUE" if "user" in model.lower() else ""}
);

-- Create indexes
CREATE INDEX idx_{table_name}_created_at ON {table_name}(created_at);
{"CREATE INDEX idx_users_email ON users(email);" if "user" in model.lower() else ""}
"""

        return schema

    def _sql_migration_code(self, intent: ParsedIntent) -> str:
        """Generate SQL migration code"""
        return """-- Database Migration
-- Generated by Aurora-X Synthesis Engine

BEGIN;

-- Add new columns or modifications here
-- ALTER TABLE users ADD COLUMN last_login TIMESTAMP;

-- Create new tables
-- CREATE TABLE IF NOT EXISTS sessions (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER REFERENCES users(id),
--     token VARCHAR(255) UNIQUE NOT NULL,
--     expires_at TIMESTAMP NOT NULL
-- );

COMMIT;
"""

    def _generic_python_main(self, intent: ParsedIntent) -> str:
        """Generate generic Python main file"""
        return f"""#!/usr/bin/env python3
\"\"\"
{intent.description}
Generated by Aurora-X Synthesis Engine
\"\"\"

import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

def main(args: argparse.Namespace) -> int:
    \"\"\"
    Main entry point

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    \"\"\"
    print(f"Running: {intent.description[:100]}")

    if args.verbose:
        print("Verbose mode enabled")
        print(f"Arguments: {{vars(args)}}")

    # TODO: Implement main logic

    print("✅ Execution complete")
    return 0

def parse_arguments() -> argparse.Namespace:
    \"\"\"Parse command-line arguments\"\"\"
    parser = argparse.ArgumentParser(
        description="{intent.description[:100]}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path'
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    sys.exit(main(args))
"""

    # Template methods
    def _flask_app_template(self) -> str:
        """Flask app template"""
        return "# Flask template loaded"

    def _react_app_template(self) -> str:
        """React app template"""
        return "// React template loaded"

    def _fastapi_app_template(self) -> str:
        """FastAPI app template"""
        return "# FastAPI template loaded"

    def _cli_tool_template(self) -> str:
        """CLI tool template"""
        return "# CLI template loaded"

    def _ml_model_template(self) -> str:
        """ML model template"""
        return "# ML template loaded"


# ========== Component 4: Safety Gate ==========

class SafetyGate:
    """Validate generated code for safety and completeness"""

    # Dangerous patterns to check
    DANGEROUS_PATTERNS = [
        r"os\.system\s*\(",  # Shell command execution
        r"eval\s*\(",  # Dynamic code execution
        r"exec\s*\(",  # Dynamic code execution
        r"__import__\s*\(",  # Dynamic imports
        r"subprocess\.call\s*\(",  # Subprocess without shell=False
        r"rm\s+-rf",  # Dangerous shell command
        r"DROP\s+DATABASE",  # Dangerous SQL
        r"DELETE\s+FROM.*WHERE\s+1=1",  # SQL injection pattern
    ]

    def validate(self, files: dict[str, str], intent: ParsedIntent) -> tuple[bool, list[str]]:
        """
        Validate generated files for safety and completeness

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for dangerous patterns
        for file_path, content in files.items():
            dangerous = self._check_dangerous_patterns(content)
            if dangerous:
                issues.append(f"Dangerous pattern in {file_path}: {dangerous}")

        # Check completeness
        required_files = self._get_required_files(intent)
        for req_file in required_files:
            if not any(req_file in path for path in files.keys()):
                issues.append(f"Missing required file: {req_file}")

        # Check file sizes (not too small, not too large)
        for file_path, content in files.items():
            if len(content) < 10 and not file_path.endswith('.gitkeep'):
                issues.append(f"File too small: {file_path}")
            if len(content) > 1_000_000:  # 1MB
                issues.append(f"File too large: {file_path}")

        # Validate syntax for known file types
        for file_path, content in files.items():
            syntax_errors = self._check_syntax(file_path, content)
            if syntax_errors:
                issues.append(f"Syntax error in {file_path}: {syntax_errors}")

        return len(issues) == 0, issues

    def _check_dangerous_patterns(self, content: str) -> str | None:
        """Check for dangerous code patterns"""
        for pattern in self.DANGEROUS_PATTERNS:
            match = re.search(pattern, content, re.I | re.M)
            if match:
                return pattern
        return None

    def _get_required_files(self, intent: ParsedIntent) -> list[str]:
        """Get list of required files based on intent"""
        required = ["README.md"]

        if intent.language == "python":
            required.append("requirements.txt")
            if intent.framework == "flask":
                required.append("app.py")
            else:
                required.append("main.py")

        if intent.language == "javascript":
            required.append("package.json")

        if "database" in intent.features:
            required.append("models")  # Can be models.py or models/

        if "testing" in intent.features:
            required.append("test")  # Should have test files

        return required

    def _check_syntax(self, file_path: str, content: str) -> str | None:
        """Basic syntax checking for known file types"""
        if file_path.endswith('.json'):
            try:
                json.loads(content) if content else {}
            except json.JSONDecodeError as e:
                return str(e)

        if file_path.endswith('.py'):
            try:
                compile(content, file_path, 'exec')
            except SyntaxError as e:
                return str(e)

        return None


# ========== Component 5: Persistence Layer ==========

class PersistenceLayer:
    """Save generated code to runs directory"""

    def save_project(self,
                    files: dict[str, str],
                    intent: ParsedIntent,
                    run_id: str = None) -> dict[str, Any]:
        """
        Save project files to runs directory

        Returns:
            Dict with run metadata
        """
        # Generate run ID if not provided
        if not run_id:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            run_id = f"run-{timestamp}"

        # Create run directory
        run_dir = Path("runs") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save all files
        saved_files = []
        for file_path, content in files.items():
            full_path = run_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            saved_files.append(file_path)

        # Create spec.json with metadata
        spec_data = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "project_type": intent.project_type.value,
            "framework": intent.framework,
            "language": intent.language,
            "features": intent.features,
            "description": intent.description,
            "entities": intent.entities,
            "files": saved_files,
            "file_count": len(saved_files)
        }

        spec_path = run_dir / "spec.json"
        spec_path.write_text(json.dumps(spec_data, indent=2), encoding='utf-8')

        # Create project.zip for download
        zip_path = self._create_zip(run_dir, files)

        # Update latest symlink
        self._update_latest_symlink(run_dir)

        return {
            "status": "success",
            "run_id": run_id,
            "run_dir": str(run_dir),
            "files": saved_files,
            "project_type": intent.project_type.value,
            "zip_path": str(zip_path)
        }

    def _create_zip(self, run_dir: Path, files: dict[str, str]) -> Path:
        """Create a zip file of the project"""
        zip_path = run_dir / "project.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, content in files.items():
                zipf.writestr(file_path, content)

        return zip_path

    def _update_latest_symlink(self, run_dir: Path) -> None:
        """Update the 'latest' symlink to point to this run"""
        latest_link = run_dir.parent / "latest"

        # Remove existing symlink if it exists
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()

        # Create new symlink
        try:
            latest_link.symlink_to(run_dir.name)
        except Exception as e:
            print(f"Warning: Could not create latest symlink: {e}")


# ========== Main Universal Synthesis Function ==========

async def synthesize_universal(
    prompt: str,
    run_id: str = None,
    context: dict = None
) -> dict:
    """
    Universal code synthesis engine main function

    Args:
        prompt: Natural language description of what to build
        run_id: Optional run ID (will be generated if not provided)
        context: Optional context dictionary with additional parameters

    Returns:
        Dict with synthesis results including status, run_id, files, etc.
    """
    try:
        # Initialize components
        parser = MultiIntentParser()
        blueprint_engine = BlueprintEngine()
        synthesizer = DynamicSynthesizer()
        safety_gate = SafetyGate()
        persistence = PersistenceLayer()

        # Step 1: Parse intent
        print(f"🔍 Parsing prompt: {prompt[:100]}...")
        intent = parser.parse(prompt)
        print(f"✅ Detected project type: {intent.project_type.value}")
        print(f"   Framework: {intent.framework}, Language: {intent.language}")

        # Step 2: Generate blueprint
        print("📐 Generating project blueprint...")
        run_dir = Path("runs") / (run_id or f"run-{time.strftime('%Y%m%d-%H%M%S')}")
        file_structure = blueprint_engine.generate_structure(intent, run_dir)
        print(f"✅ Generated {len(file_structure)} file blueprints")

        # Step 3: Synthesize code
        print("⚙️ Synthesizing code...")
        completed_files = synthesizer.synthesize_code(intent, file_structure)
        print(f"✅ Synthesized code for {len(completed_files)} files")

        # Step 4: Safety validation
        print("🔒 Validating generated code...")
        is_valid, issues = safety_gate.validate(completed_files, intent)

        if not is_valid:
            print("⚠️ Validation issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   - {issue}")
            # Continue anyway but mark as having issues

        # Step 5: Persist to disk
        print("💾 Saving project to disk...")
        result = persistence.save_project(completed_files, intent, run_id)

        # Add validation results to output
        result["validation"] = {
            "is_valid": is_valid,
            "issues": issues if not is_valid else []
        }

        print(f"✅ Project saved to: {result['run_dir']}")
        print(f"📦 Download package: {result['zip_path']}")

        return result

    except Exception as e:
        print(f"❌ Error during synthesis: {e}")
        return {
            "status": "error",
            "error": str(e),
            "run_id": run_id or "error",
            "files": [],
            "project_type": "unknown"
        }


# Synchronous wrapper for compatibility
def synthesize_universal_sync(prompt: str, run_id: str = None, context: dict = None) -> dict:
    """Synchronous wrapper for synthesize_universal"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(synthesize_universal(prompt, run_id, context))
    finally:
        loop.close()


# ========== Bridge API Wrapper ==========

@dataclass
class ProjectResult:
    """Result object for bridge API compatibility"""
    run_dir: Path
    manifest: dict

def generate_project(prompt: str, runs_dir: Path = None) -> ProjectResult:
    """
    Generate a project from natural language prompt (Bridge API compatible)

    Args:
        prompt: Natural language description of what to build
        runs_dir: Optional directory to store runs (defaults to "runs")

    Returns:
        ProjectResult with run_dir and manifest containing files and metadata
    """
    if runs_dir is None:
        runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    # Generate timestamp-based run ID
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"run-{timestamp}"

    # Call the main synthesis function
    result = synthesize_universal_sync(prompt, run_id)

    # Create project.zip if it doesn't exist
    run_dir = Path(result.get("run_dir", runs_dir / run_id))
    zip_path = run_dir / "project.zip"

    if not zip_path.exists() and run_dir.exists():
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in run_dir.rglob("*"):
                if file_path.is_file() and file_path.name != "project.zip":
                    zf.write(file_path, file_path.relative_to(run_dir))

    # Build manifest for bridge compatibility
    manifest = {
        "ts": timestamp,
        "files": result.get("files", []),
        "project_type": result.get("project_type", "unknown"),
        "status": result.get("status", "success"),
        "validation": result.get("validation", {})
    }

    return ProjectResult(run_dir=run_dir, manifest=manifest)


# ========== Testing & Demo ==========

if __name__ == "__main__":
    # Demo usage
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Create a Flask API with user authentication and a React frontend dashboard"

    print(f"\n{'='*60}")
    print("Aurora-X Universal Code Synthesis Engine")
    print(f"{'='*60}\n")

    # Run synthesis
    result = synthesize_universal_sync(prompt)

    # Print results
    print(f"\n{'='*60}")
    print("Synthesis Complete!")
    print(f"{'='*60}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Run ID: {result.get('run_id', 'N/A')}")
    print(f"Project Type: {result.get('project_type', 'N/A')}")
    print(f"Files Generated: {len(result.get('files', []))}")

    if result.get('validation'):
        if result['validation']['is_valid']:
            print("✅ All validations passed")
        else:
            print(f"⚠️ {len(result['validation']['issues'])} validation issues found")

    print(f"\nProject saved to: {result.get('run_dir', 'N/A')}")
    print(f"Download: {result.get('zip_path', 'N/A')}")
