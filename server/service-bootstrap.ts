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
      name: "luminar-nexus-v2",
      port: 8000,
      command: pythonCmd,
      args: [path.join(root, "tools", "luminar_nexus_v2.py"), "serve"],
    },
  ];

  const processes: ChildProcess[] = [];

  for (const service of services) {
    const running = await isPortOpen(service.port);
    if (running) {
      continue;
    }

    const scriptPath = service.args.find((arg) => arg.endsWith(".py"));
    if (scriptPath && !fs.existsSync(scriptPath)) {
      console.warn(`[Bootstrap] ${service.name} script missing: ${scriptPath}`);
      continue;
    }

    try {
      processes.push(spawnService(service));
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
