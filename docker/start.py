import importlib
import os
import sys

CANDIDATES = [
    "aurora_x.serve:app",
    "server.main:app",
    "app.main:app",
]


def find_target() -> str:
    for target in CANDIDATES:
        try:
            module_name, attr = target.split(":")
            module = importlib.import_module(module_name)
            if getattr(module, attr, None) is not None:
                return target
        except Exception:
            continue
    print("[start.py] No valid FastAPI app target found.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    target = find_target()
    print(f"[start.py] Starting uvicorn {target}", flush=True)
    os.execvp(
        "uvicorn",
        ["uvicorn", target, "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"],
    )


if __name__ == "__main__":
    main()
