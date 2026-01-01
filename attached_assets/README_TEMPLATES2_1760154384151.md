
# T08 Templates Extension
Adds two more target types to /chat:
- **cli_tool** → creates an argparse-based script
- **lib_func** → creates a Python function + minimal tests (e.g., factorial)

## Wire it (choose ONE attach module)
In `aurora_x/serve.py`, import either the original or the extended attach:
```python
# Basic web-only:
# from aurora_x.chat.attach_router import attach_router

# Extended (web + CLI + lib functions):
from aurora_x.chat.attach_router_extend import attach_router

attach_router(app)
```
