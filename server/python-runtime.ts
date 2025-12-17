import fs from "fs";
import path from "path";

const isWindows = process.platform === "win32";

const VENV_CANDIDATES = isWindows
  ? [".venv\\Scripts\\python.exe", "venv\\Scripts\\python.exe"]
  : [".venv/bin/python", "venv/bin/python"];

const FALLBACKS = isWindows ? ["python"] : ["python3", "python"];

export function resolvePythonCommand(): string {
  if (process.env.AURORA_PYTHON) {
    return process.env.AURORA_PYTHON;
  }

  const root = process.cwd();
  for (const candidate of VENV_CANDIDATES) {
    const fullPath = path.join(root, candidate);
    if (fs.existsSync(fullPath)) {
      process.env.AURORA_PYTHON = fullPath;
      return fullPath;
    }
  }

  const envPython = process.env.PYTHON || process.env.PYTHON_CMD;
  if (envPython) {
    process.env.AURORA_PYTHON = envPython;
    return envPython;
  }

  const fallback = FALLBACKS[0];
  process.env.AURORA_PYTHON = fallback;
  return fallback;
}
