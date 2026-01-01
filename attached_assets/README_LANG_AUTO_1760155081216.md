# Language Auto‑Select (Python/Go/Rust/C#)

Wire in `aurora_x/serve.py`:
```python
from aurora_x.chat.attach_router_lang import attach_router
attach_router(app)
```
Env override (optional):
- AURORA_DEFAULT_LANG = python|go|rust|csharp

Examples:
- POST /chat {"prompt":"fast microservice web api"} → Go
- POST /chat {"prompt":"memory-safe cli to parse args"} → Rust
- POST /chat {"prompt":"enterprise web api with health"} → C# (.NET 8)
- POST /chat {"prompt":"make futuristic timer ui"} → Python Flask
Force language:
- POST /chat {"prompt":"make a web api","lang":"csharp"}
