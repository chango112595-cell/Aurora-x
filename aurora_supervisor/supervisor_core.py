"""
Aurora Supervisor System
Phase 4–6 Mega Supervisor
Safe for Replit sandbox execution
"""
import os, json, time, threading, queue, platform, psutil, traceback, shutil

# ---------- KNOWLEDGE FABRIC (persistent memory) ----------
class KnowledgeFabric:
    def __init__(self, root="aurora_supervisor/data/knowledge"):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.events_log = os.path.join(root, "events.jsonl")
        self.models_dir = os.path.join(root, "models")
        os.makedirs(self.models_dir, exist_ok=True)
        self.memory = {}

    def record_event(self, kind, path, reason):
        event = {"ts": time.time(), "kind": kind, "path": path, "reason": reason}
        with open(self.events_log, "a") as f:
            f.write(json.dumps(event) + "\n")

    def save_state(self, name="state_snapshot"):
        path = os.path.join(self.models_dir, f"{name}.json")
        snapshot = {"timestamp": time.time(),"memory": self.memory}
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)

    def load_state(self, name="state_snapshot"):
        path = os.path.join(self.models_dir, f"{name}.json")
        if os.path.exists(path):
            with open(path) as f:
                self.memory = json.load(f).get("memory", {})

# ---------- ENVIRONMENT ANALYSIS ----------
def analyze_environment():
    info = {
        "os": platform.system(),
        "version": platform.version(),
        "cpu_count": os.cpu_count(),
        "total_memory_gb": round(psutil.virtual_memory().total / 1e9, 2),
        "disk_free_gb": round(shutil.disk_usage("/").free / 1e9, 2),
    }
    print(f"[Supervisor] Environment scan: {info}")
    return info

# ---------- WORKER THREADS ----------
class BaseWorker(threading.Thread):
    def __init__(self, wid, role, task_q, fabric):
        super().__init__(daemon=True)
        self.wid = wid
        self.role = role
        self.q = task_q
        self.fabric = fabric
        self.active = True

    def run(self):
        while self.active:
            try:
                task = self.q.get(timeout=2)
                self.process(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.fabric.record_event("error", f"{self.role}-{self.wid}", str(e))
                traceback.print_exc()

    def process(self, task):
        msg = f"[{self.role}-{self.wid}] processing task: {task}"
        print(msg)
        self.fabric.record_event("task", f"{self.role}-{self.wid}", msg)
        self.fabric.memory[f"{self.role}-{self.wid}"] = task

    def stop(self):
        self.active = False

# ---------- SUPERVISOR CORE ----------
class AuroraSupervisor:
    def __init__(self, root="aurora_supervisor"):
        self.root = root
        self.fabric = KnowledgeFabric(os.path.join(root, "data/knowledge"))
        self.heal_q = queue.Queue()
        self.task_q = queue.Queue()
        self.healers = []
        self.workers = []
        self.running = True
        self.fabric.load_state()

    def start(self):
        analyze_environment()
        self.spawn_workers()
        self.main_loop()

    def spawn_workers(self):
        for i in range(100):
            h = BaseWorker(i, "healer", self.heal_q, self.fabric)
            self.healers.append(h); h.start()
        for i in range(300):
            w = BaseWorker(i, "task", self.task_q, self.fabric)
            self.workers.append(w); w.start()
        print("[Supervisor] 400 workers operational (100 healers + 300 tasks).")

    def main_loop(self):
        try:
            while self.running:
                self.dispatch_health_tasks()
                self.fabric.save_state()
                time.sleep(15)
        except KeyboardInterrupt:
            self.shutdown()

    def dispatch_health_tasks(self):
        self.heal_q.put("validate_integrity_phase_4_6")
        self.task_q.put("build_phase_4_6_modules")
        self.task_q.put("optimize_learning_parameters")

    def shutdown(self):
        print("[Supervisor] Shutting down...")
        self.running = False
        for h in self.healers + self.workers:
            h.stop()
        self.fabric.save_state()
        print("[Supervisor] State saved, all workers stopped.")

if __name__ == "__main__":
    sup = AuroraSupervisor()
    sup.start()
