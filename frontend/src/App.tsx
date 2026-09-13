import { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type HealthResponse = {
  status: string;
  service: string;
  database?: string;
};

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [statusText, setStatusText] = useState('Checking backend...');

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = (await response.json()) as HealthResponse;
        setHealth(data);
        setStatusText(response.ok && data.status === 'ok' ? 'Backend healthy' : 'Backend degraded');
      } catch (error) {
        setStatusText('Backend unavailable');
        setHealth(null);
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Growth operations</p>
          <h1>Lenny Growth Assistant</h1>
        </div>
        <div className={`status-pill ${health?.database === 'connected' ? 'healthy' : 'degraded'}`}>
          {statusText}
        </div>
      </header>

      <main className="content">
        <section className="hero">
          <h2>Welcome to your foundation for AI-powered growth analysis.</h2>
          <p>
            This Phase 1 starter establishes the frontend, backend, and PostgreSQL foundation for the
            Lenny Growth Assistant.
          </p>
        </section>

        <section className="chat-panel" aria-label="Chat placeholder">
          <div className="chat-header">
            <span>Assistant</span>
          </div>

          <div className="message-list">
            <div className="message bot">
              <strong>System:</strong> This chat area is a placeholder for future transcript and RAG workflows.
            </div>
            <div className="message user">How can I review my growth signals?</div>
          </div>

          <div className="composer">
            <input type="text" placeholder="Type your message..." aria-label="Message input" />
            <button type="button">Send</button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
