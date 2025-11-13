import React, { useState, useEffect, useRef } from 'react';

export default function AuroraChatInterface() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Connect to Aurora WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/aurora/chat`;

    console.log('Connecting to:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('✅ Connected to Aurora');
      setIsConnected(true);
      setError(null);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: '🌌 Aurora is now online and ready to assist you!' 
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'error') {
          setError(data.content);
        } else {
          setMessages(prev => [...prev, { role: 'aurora', content: data.content }]);
        }
      } catch (err) {
        console.error('Failed to parse message:', err);
        setError('Received malformed message from server.');
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setError('Connection error occurred');
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 Disconnected from Aurora');
      setIsConnected(false);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: '⚠️ Connection to Aurora closed' 
      }]);
    };

    wsRef.current = ws;

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const addMessage = (sender: string, text: string) => {
    setMessages(prev => [...prev, { role: sender, content: text }]);
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  };

  const sendMessage = () => {
    if (!input.trim() || !isConnected) return;

    addMessage('user', input);
    wsRef.current?.send(JSON.stringify({ message: input }));
    setInput('');
  };

  return (
    <div className="aurora-chat-container">
      <div className="aurora-header">
        <h1>🌌 Aurora</h1>
        <div className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="messages" ref={messagesEndRef}>
        {messages.length === 0 && !isConnected && (
          <div className="message system no-messages">
            Connecting to Aurora...
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="sender">
              {msg.role === 'aurora' ? '🌌 Aurora' : 
               msg.role === 'user' ? '👤 You' : '⚙️ System'}
            </div>
            <div className="text">{msg.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={isConnected ? "Message Aurora..." : "Connecting..."}
          disabled={!isConnected}
        />
        <button onClick={sendMessage} disabled={!isConnected || !input.trim()}>
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
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
          font-size: 1.8rem;
          letter-spacing: 1px;
          text-shadow: 0 0 8px rgba(139, 92, 246, 0.7);
        }

        .status {
          font-size: 0.9rem;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-weight: bold;
          text-shadow: 0 0 4px rgba(0,0,0,0.2);
        }

        .status.connected {
          background: rgba(34, 197, 94, 0.2);
          color: #22c55e;
        }

        .status.disconnected {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }
        
        .error-message {
          padding: 10px 15px;
          margin: 10px 15px;
          background-color: #ffebee;
          color: #c62828;
          border-radius: 4px;
          border: 1px solid #ef5350;
          text-align: center;
          font-size: 0.9rem;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .message.no-messages {
          text-align: center;
          color: rgba(255, 255, 255, 0.6);
          font-style: italic;
          margin-top: 30%;
        }

        .message {
          padding: 0.75rem;
          border-radius: 8px;
          line-height: 1.5;
        }

        .message.user {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.2) 100%);
          margin-left: 25%;
          border: 1px solid rgba(59, 130, 246, 0.3);
          box-shadow: 0 1px 3px rgba(59, 130, 246, 0.2);
        }

        .message.aurora {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.2) 100%);
          margin-right: 25%;
          border: 1px solid rgba(139, 92, 246, 0.3);
          box-shadow: 0 1px 3px rgba(139, 92, 246, 0.2);
        }

        .message.system {
          background: rgba(255, 255, 255, 0.05);
          text-align: center;
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.6);
          border: 1px solid rgba(255, 255, 255, 0.1);
          margin: 0 auto;
          padding: 0.5rem 1rem;
          border-radius: 10px;
          max-width: 60%;
        }

        .sender {
          font-weight: bold;
          margin-bottom: 0.4rem;
          font-size: 0.9rem;
          opacity: 0.8;
        }
        .message.user .sender { color: #90caf9; }
        .message.aurora .sender { color: #b39ddb; }
        .message.system .sender { color: rgba(255, 255, 255, 0.7); }

        .text {
          font-size: 1rem;
        }

        .input-area {
          padding: 1rem;
          background: rgba(255,255,255,0.05);
          display: flex;
          gap: 0.75rem;
          align-items: center;
          border-top: 1px solid rgba(255,255,255,0.1);
        }

        .input-area input {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 8px;
          background: rgba(255,255,255,0.05);
          color: #fff;
          font-size: 1rem;
          transition: border-color 0.3s ease;
        }

        .input-area input:focus {
          outline: none;
          border-color: #8b5cf6;
          box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3);
        }
        
        .input-area input::placeholder {
          color: rgba(255, 255, 255, 0.5);
        }

        .input-area button {
          padding: 0.75rem 1.5rem;
          background: #8b5cf6;
          border: none;
          border-radius: 8px;
          color: #fff;
          font-weight: bold;
          cursor: pointer;
          font-size: 1rem;
          transition: background 0.3s ease, transform 0.2s ease;
        }

        .input-area button:hover:not(:disabled) {
          background: #7c3aed;
          transform: translateY(-1px);
        }
        
        .input-area button:active:not(:disabled) {
          transform: translateY(0);
        }

        .input-area button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          background: #ccc;
        }
      `}</style>
    </div>
  );
}