import { spawn, type ChildProcess } from "child_process";
import fs from "fs";
import net from "net";
import path from "path";
import { resolvePythonCommand } from "./python-runtime";

type ServiceSpec = {
  name: string;
  port: number;
  command: string;
  args: string[];
  cwd?: string;
};

const LOG_DIR = path.join(process.cwd(), "logs", "services");
const LUMINAR_SERVICE_NAME = "luminar-nexus-v2";
const LUMINAR_SERVICE_PORT = 8000;
const LUMINAR_SCRIPT_PATH = path.join("tools", "luminar_nexus_v2.py");

let luminarProcess: ChildProcess | null = null;

function ensureLogDir() {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

function logPathFor(name: string) {
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "_");
  return path.join(LOG_DIR, `${slug}.log`);
}

function isPortOpen(port: number, host = "127.0.0.1"): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = new net.Socket();

    const finalize = (open: boolean) => {
      socket.removeAllListeners();
      socket.destroy();
      resolve(open);
    };

    socket.setTimeout(750);
    socket.once("connect", () => finalize(true));
    socket.once("timeout", () => finalize(false));
    socket.once("error", () => finalize(false));
    socket.connect(port, host);
  });
}

function spawnService(spec: ServiceSpec): ChildProcess {
  ensureLogDir();
  const logFile = logPathFor(spec.name);
  const output = fs.openSync(logFile, "a");

  return spawn(spec.command, spec.args, {
    cwd: spec.cwd ?? process.cwd(),
    env: process.env,
    stdio: ["ignore", output, output],
    detached: false,
  });
}

async function waitForPort(port: number, timeoutMs: number = 5000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await isPortOpen(port)) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  return false;
}

export async function ensureLuminarRunning(): Promise<boolean> {
  if (await isPortOpen(LUMINAR_SERVICE_PORT)) {
    return true;
  }

  if (luminarProcess && !luminarProcess.killed) {
    return await waitForPort(LUMINAR_SERVICE_PORT, 5000);
  }

  const pythonCmd = resolvePythonCommand();
  const scriptPath = path.join(process.cwd(), LUMINAR_SCRIPT_PATH);
  if (!fs.existsSync(scriptPath)) {
    console.warn(`[Luminar] Script missing at ${scriptPath}. Chat fallback will stay offline.`);
    return false;
  }

  try {
    luminarProcess = spawnService({
      name: LUMINAR_SERVICE_NAME,
      port: LUMINAR_SERVICE_PORT,
      command: pythonCmd,
      args: [scriptPath, "serve"],
    });

    const ready = await waitForPort(LUMINAR_SERVICE_PORT, 7000);
    if (!ready) {
      console.warn("[Luminar] Service failed to bind to port in time.");
    }
    return ready;
  } catch (error) {
    console.warn("[Luminar] Failed to spawn service:", error);
    return false;
  }
}

export async function bootstrapAuxServices(): Promise<ChildProcess[]> {
  const pythonCmd = resolvePythonCommand();
  const root = process.cwd();
  const services: ServiceSpec[] = [
    {
      name: "aurora-bridge",
      port: 5001,
      command: pythonCmd,
      args: ["-m", "aurora_x.bridge.service"],
    },
    {
      name: "aurora-nexus-v3",
      port: 5002,
      command: pythonCmd,
      args: [path.join(root, "aurora_nexus_v3", "main.py")],
    },
    {
      name: LUMINAR_SERVICE_NAME,
      port: LUMINAR_SERVICE_PORT,
      command: pythonCmd,
      args: [path.join(root, LUMINAR_SCRIPT_PATH), "serve"],
    },
  ];

  const processes: ChildProcess[] = [];

  for (const service of services) {
    const running = await isPortOpen(service.port);
    if (running) {
      if (service.name === LUMINAR_SERVICE_NAME) {
        await ensureLuminarRunning();
      }
      continue;
    }

    const scriptPath = service.args.find((arg) => arg.endsWith(".py"));
    if (scriptPath && !fs.existsSync(scriptPath)) {
      console.warn(`[Bootstrap] ${service.name} script missing: ${scriptPath}`);
      continue;
    }

    try {
      const child = spawnService(service);
      processes.push(child);
      if (service.name === LUMINAR_SERVICE_NAME) {
        luminarProcess = child;
      }
    } catch (error) {
      console.warn(`[Bootstrap] Failed to start ${service.name}:`, error);
    }
  }

  return processes;
}

export function stopAuxServices(processes: ChildProcess[]): void {
  for (const proc of processes) {
    if (!proc || proc.killed) {
      continue;
    }
    try {
      proc.kill("SIGTERM");
    } catch {
      // ignore
    }
  }
}
