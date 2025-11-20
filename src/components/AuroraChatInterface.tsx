import React, { useState, useEffect, useRef } from 'react';

export default function AuroraChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Aurora connects to her backend using WebSocket (TIER_19: Real-time)
    const ws = new WebSocket('ws://localhost:5000/aurora/chat');
    
    ws.onopen = () => {
      setConnected(true);
      addMessage('system', 'Connected to Aurora');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      addMessage('aurora', data.message);
    };
    
    ws.onerror = () => {
      setConnected(false);
      addMessage('system', 'Connection error');
    };
    
    wsRef.current = ws;
    
    return () => ws.close();
  }, []);

  const addMessage = (sender, text) => {
    setMessages(prev => [...prev, { sender, text, timestamp: new Date() }]);
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  };

  const sendMessage = () => {
    if (!input.trim() || !connected) return;
    
    addMessage('user', input);
    wsRef.current?.send(JSON.stringify({ message: input }));
    setInput('');
  };

  return (
    <div className="aurora-chat-container">
      <div className="aurora-header">
        <h1>🌌 Aurora</h1>
        <div className={`status ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>
      
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="sender">
              {msg.sender === 'aurora' ? '🌌 Aurora' : 
               msg.sender === 'user' ? '👤 You' : '⚙️ System'}
            </div>
            <div className="text">{msg.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Message Aurora..."
          disabled={!connected}
        />
        <button onClick={sendMessage} disabled={!connected}>
          Send
        </button>
      </div>
      
      <style jsx>{`
        .aurora-chat-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
          color: #fff;
        }
        
        .aurora-header {
          padding: 1rem;
          background: rgba(255,255,255,0.05);
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .aurora-header h1 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .status {
          font-size: 0.9rem;
          padding: 0.5rem 1rem;
          border-radius: 20px;
        }
        
        .status.connected {
          background: rgba(34, 197, 94, 0.2);
          color: #22c55e;
        }
        
        .status.disconnected {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }
        
        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }
        
        .message {
          margin-bottom: 1rem;
          padding: 0.75rem;
          border-radius: 8px;
        }
        
        .message.user {
          background: rgba(59, 130, 246, 0.2);
          margin-left: 20%;
        }
        
        .message.aurora {
          background: rgba(139, 92, 246, 0.2);
          margin-right: 20%;
        }
        
        .message.system {
          background: rgba(255, 255, 255, 0.05);
          text-align: center;
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.6);
        }
        
        .sender {
          font-weight: bold;
          margin-bottom: 0.25rem;
          font-size: 0.9rem;
        }
        
        .input-area {
          padding: 1rem;
          background: rgba(255,255,255,0.05);
          display: flex;
          gap: 0.5rem;
        }
        
        .input-area input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 8px;
          background: rgba(255,255,255,0.05);
          color: #fff;
          font-size: 1rem;
        }
        
        .input-area input:focus {
          outline: none;
          border-color: #8b5cf6;
        }
        
        .input-area button {
          padding: 0.75rem 1.5rem;
          background: #8b5cf6;
          border: none;
          border-radius: 8px;
          color: #fff;
          font-weight: bold;
          cursor: pointer;
        }
        
        .input-area button:hover:not(:disabled) {
          background: #7c3aed;
        }
        
        .input-area button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}
