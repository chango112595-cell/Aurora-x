import React, { useEffect, useRef, useState } from "react";

const quantumStateColors: Record<string, string> = {
  stable: "#00ff88",
  superposition: "#ff8800",
  entangled: "#8800ff",
};

export default function AuroraChatTest() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const messagesDiv = useRef<HTMLDivElement>(null);

  useEffect(() => {
    addMessage("system", "🌌 Luminar Nexus v2 Advanced Interface Initialized", false);
    addMessage("system", "✨ Features: Quantum State Monitoring | AI Healing | Multi-Endpoint Routing", false);
    refreshStatus();
    const interval = setInterval(refreshStatus, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (messagesDiv.current) {
      messagesDiv.current.scrollTop = messagesDiv.current.scrollHeight;
    }
  }, [messages]);

  function addMessage(role: string, content: string, timestamp = true) {
    setMessages((msgs) => [
      ...msgs,
      {
        role,
        content,
        time: timestamp ? new Date().toLocaleTimeString() : "",
      },
    ]);
  }

  function formatJSON(obj: any) {
    return <pre>{JSON.stringify(obj, null, 2)}</pre>;
  }

  async function refreshStatus() {
    try {
      const nexusResponse = await fetch("http://localhost:5005/api/nexus/status");
      const nexusStatus = await nexusResponse.json();
      setSystemStatus(nexusStatus);
      addMessage("system", "✅ System status updated via Luminar Nexus v2");
    } catch (error: any) {
      addMessage("system", "❌ Failed to refresh status: " + error.message);
    }
  }

  function updateSystemDisplay(status: any) {
    if (!status) return null;
    const services = Object.values(status.services || {});
    const quantumStates: Record<string, string[]> = {};
    services.forEach((service: any) => {
      const state = service.quantum_state || "stable";
      if (!quantumStates[state]) quantumStates[state] = [];
      quantumStates[state].push(service.service_name);
    });
    return (
      <>
        <div id="quantum-states">
          {Object.keys(quantumStates).map((state) => (
            <span
              key={state}
              className={`quantum-indicator quantum-${state}`}
              style={{
                borderColor: quantumStateColors[state] || "#00ff88",
                color: quantumStateColors[state] || "#00ff88",
                marginRight: 8,
                padding: "5px 15px",
                borderRadius: 5,
                fontSize: 12,
                border: "1px solid",
                display: "inline-block",
              }}
            >
              {state.toUpperCase()}: {quantumStates[state].join(", ")}
            </span>
          ))}
        </div>
        <div id="system-metrics">
          <div>
            <strong>Version:</strong> {status.version || "Unknown"}
          </div>
          <div>
            <strong>Uptime:</strong> {status.uptime || "Unknown"}
          </div>
          <div>
            <strong>Quantum Coherence:</strong>{" "}
            <span style={{ color: status.quantum_coherence >= 0.8 ? "#00ff88" : "#ff8800" }}>
              {status.quantum_coherence || 0}
            </span>
          </div>
          <div>
            <strong>AI Learning:</strong> {status.ai_learning_active ? "✅ Active" : "❌ Inactive"}
          </div>
          <div>
            <strong>Auto Healing:</strong> {status.autonomous_healing_active ? "✅ Active" : "❌ Inactive"}
          </div>
        </div>
        <div id="service-health">
          <div>
            <strong>Services:</strong> {status.healthy_services || 0}/{status.total_services || 0} Healthy
          </div>
          {services.map((service: any) => (
            <div className="metric" key={service.service_name}>
              <strong>{service.service_name}:</strong> {service.status} (Port: {service.port}, Mem: {(service.memory_usage * 100).toFixed(2)}%)
            </div>
          ))}
        </div>
      </>
    );
  }

  async function sendMessage() {
    if (!input) return;
    addMessage("user", input);
    setInput("");
    try {
      const endpoints = [
        "http://localhost:5001/chat",
        "http://localhost:5003/api/chat",
      ];
      let data = null;
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: input, message: input }),
          });
          if (response.ok) {
            data = await response.json();
            break;
          }
        } catch (err) { }
      }
      if (data) {
        let auroraReply = "🌟 Aurora via Luminar Nexus v2:\n\n";
        if (data.response) {
          auroraReply += data.response;
        } else if (data.message) {
          auroraReply += data.message;
        } else {
          auroraReply += formatJSON(data);
        }
        addMessage("assistant", auroraReply);
        setTimeout(refreshStatus, 1000);
      } else {
        throw new Error("No valid response from any Aurora endpoint");
      }
    } catch (error: any) {
      addMessage(
        "assistant",
        "❌ Communication Error: " + error.message + "\n\n🔧 Luminar Nexus v2 will attempt autonomous healing..."
      );
      setTimeout(refreshStatus, 2000);
    }
  }

  return (
    <div style={{ fontFamily: 'Monaco, Menlo, monospace', maxWidth: 1200, margin: '20px auto', background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)', color: '#00ff88', padding: 20, minHeight: '100vh' }}>
      <div className="header" style={{ textAlign: 'center', marginBottom: 30, border: '2px solid #00ff88', padding: 20, borderRadius: 10, background: 'rgba(0,255,136,0.05)' }}>
        <h1>🌌 Aurora Luminar Nexus v2 - Advanced System Interface</h1>
        <p>AI-Driven Orchestration | Quantum Coherence Monitoring | Autonomous Healing</p>
        {updateSystemDisplay(systemStatus)}
      </div>
      <div className="system-status" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        <div className="status-panel" style={{ border: '1px solid #00ff88', padding: 15, background: '#0a0a0a', borderRadius: 5 }}>
          <h3>🔋 System Status</h3>
          <div id="system-metrics">{updateSystemDisplay(systemStatus)}</div>
        </div>
        <div className="status-panel" style={{ border: '1px solid #00ff88', padding: 15, background: '#0a0a0a', borderRadius: 5 }}>
          <h3>🏥 Service Health</h3>
          <div id="service-health">{updateSystemDisplay(systemStatus)}</div>
        </div>
      </div>
      <div className="control-panel" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 10, margin: '10px 0' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Send message to Aurora via Luminar Nexus v2..."
          style={{ background: '#0a0a0a', border: '1px solid #00ff88', color: '#00ff88', padding: 12, fontFamily: 'monospace', borderRadius: 3 }}
        />
        <button onClick={sendMessage} style={{ background: '#0a0a0a', border: '1px solid #00ff88', color: '#00ff88', padding: 12, fontFamily: 'monospace', borderRadius: 3, cursor: 'pointer', transition: 'all 0.3s' }}>Send Message</button>
        <button onClick={refreshStatus} style={{ background: '#0a0a0a', border: '1px solid #00ff88', color: '#00ff88', padding: 12, fontFamily: 'monospace', borderRadius: 3, cursor: 'pointer', transition: 'all 0.3s' }}>Refresh Status</button>
      </div>
      <div ref={messagesDiv} id="messages" style={{ border: '1px solid #00ff88', padding: 20, margin: '20px 0', minHeight: 400, background: '#0a0a0a', borderRadius: 5, maxHeight: 400, overflowY: 'auto' }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.role}`}
            style={{
              margin: '10px 0',
              padding: 10,
              borderLeft: `3px solid ${msg.role === 'system' ? '#ff8800' : msg.role === 'assistant' ? '#00ff88' : '#88ccff'}`,
              borderRadius: 3,
              color: msg.role === 'system' ? '#ff8800' : msg.role === 'assistant' ? '#00ff88' : '#88ccff',
              background: msg.role === 'system' ? 'rgba(255,136,0,0.1)' : msg.role === 'assistant' ? 'rgba(0,255,136,0.1)' : 'rgba(136,204,255,0.1)',
            }}
          >
            <strong>{msg.role}{msg.time ? ` [${msg.time}]` : ''}:</strong>
            <br />
            {typeof msg.content === 'string' ? msg.content : formatJSON(msg.content)}
          </div>
        ))}
      </div>
    </div>
  );
}
