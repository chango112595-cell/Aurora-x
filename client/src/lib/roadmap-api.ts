export async function getRoadmapProgress() {
  const r = await fetch("/api/roadmap/progress");
  return r.json();
}

export async function getRoadmapSummary() {
  const r = await fetch("/api/roadmap/summary");
  return r.json();
}

export async function getEvolutionLog() {
  const r = await fetch("/api/evolution/log");
  return r.json();
}

export async function getQueuedApprovals() {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("aurora_api_key") || "" : "";
  const r = await fetch("/api/evolution/queued", { 
    headers: { "x-api-key": apiKey }
  });
  return r.json();
}

export async function approveChange(target: string) {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("aurora_api_key") || "" : "";
  const r = await fetch("/api/evolution/approve", {
    method: "POST",
    headers: { 
      "content-type": "application/json", 
      "x-api-key": apiKey 
    },
    body: JSON.stringify({ target })
  });
  return r.json();
}

export async function runNextPhase() {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("aurora_api_key") || "" : "";
  const r = await fetch("/api/roadmap/run-next", { 
    method: "POST", 
    headers: { "x-api-key": apiKey }
  });
  return r.json();
}
