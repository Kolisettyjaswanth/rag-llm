import { FormEvent, useEffect, useState } from 'react';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type HealthResponse = {
  status: string;
  service: string;
  database?: string;
};

type ChatSource = {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  similarity: number;
  guest?: string | null;
  title?: string | null;
  youtube_url?: string | null;
  video_id?: string | null;
  publish_date?: string | null;
};

type ChatResponse = {
  message_id: string;
  answer: string;
  sources: ChatSource[];
  skill: string;
  route_reason: string;
  artifact?: {
    type: 'html' | 'markdown';
    content: string;
  } | null;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  skill?: string;
  routeReason?: string;
  artifact?: ChatResponse['artifact'];
};

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [statusText, setStatusText] = useState('Checking backend...');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const initialize = async () => {
      try {
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        const healthData =
          (await healthResponse.json()) as HealthResponse;

        setHealth(healthData);

        if (
          healthResponse.ok &&
          healthData.status === 'ok' &&
          healthData.database === 'connected'
        ) {
          setStatusText('Backend connected');
        } else {
          setStatusText('Backend degraded');
        }

        const sessionResponse = await fetch(
          `${API_BASE_URL}/api/sessions`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: 'Lenny Growth Assistant',
            }),
          },
        );

        if (!sessionResponse.ok) {
          throw new Error('Unable to create session');
        }

        const session = await sessionResponse.json();
        setSessionId(session.id);
      } catch {
        setStatusText('Backend unavailable');
        setHealth(null);
      }
    };

    initialize();
  }, []);

  const sendMessage = async (event: FormEvent) => {
    event.preventDefault();

    const question = input.trim();

    if (!question || !sessionId || loading) {
      return;
    }

    setInput('');

    setMessages((current) => [
      ...current,
      {
        role: 'user',
        content: question,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: question,
        }),
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = (await response.json()) as ChatResponse;

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          skill: data.skill,
          routeReason: data.route_reason,
          artifact: data.artifact,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content:
            'I could not complete the request. Please check that the backend and Ollama are running and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Lenny's Podcast · Growth Intelligence</p>
          <h1>Lenny Growth Assistant</h1>
          <p className="subtitle">
            Ask growth and product questions grounded in Lenny's Podcast
            transcripts.
          </p>
        </div>

        <div
          className={`status-pill ${
            health?.database === 'connected' ? 'healthy' : 'degraded'
          }`}
        >
          <span className="status-dot" />
          {statusText}
        </div>
      </header>

      <main className="content">
        <section className="chat-panel" aria-label="Lenny Growth Assistant chat">
          <div className="chat-header">
            <div>
              <span className="chat-title">Growth Assistant</span>
              <span className="chat-description">
                Grounded in Lenny's Podcast
              </span>
            </div>
          </div>

          <div className="message-list">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">✦</div>
                <h2>What do you want to learn?</h2>
                <p>
                  Ask about growth, product strategy, teams, onboarding,
                  retention, experimentation, or other topics discussed on
                  Lenny's Podcast.
                </p>

                <div className="suggestions">
                  <button
                    type="button"
                    onClick={() =>
                      setInput(
                        'What does Adam Fishman say about onboarding?',
                      )
                    }
                  >
                    Ask about onboarding
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setInput(
                        'What are some important principles for building a growth team?',
                      )
                    }
                  >
                    Ask about growth teams
                  </button>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                className={`message-row ${
                  message.role === 'user' ? 'user-row' : 'assistant-row'
                }`}
                key={`${message.role}-${index}`}
              >
                <div className={`message ${message.role}`}>
                  {message.content}
                </div>

                {message.role === 'assistant' && message.skill && (
                  <div className="route-meta">
                    <span className="skill-badge">{message.skill}</span>
                    <span>{message.routeReason}</span>
                  </div>
                )}

                {message.role === 'assistant' &&
                  message.artifact?.type === 'html' && (
                    <details className="artifact-viewer">
                      <summary>View generated artifact</summary>
                      <iframe
                        title="Generated HTML artifact"
                        sandbox=""
                        srcDoc={message.artifact.content}
                      />
                    </details>
                  )}

                {message.role === 'assistant' &&
                  message.sources &&
                  message.sources.length > 0 && (
                    <div className="sources">
                      <div className="sources-title">
                        Sources · {message.sources.length}
                      </div>

                      {message.sources.map((source, sourceIndex) => (
                        <details
                          className="source-card"
                          key={source.chunk_id}
                        >
                          <summary>
                            <span>
                              {sourceIndex + 1}.{' '}
                              {source.title || 'Lenny Podcast transcript'}
                            </span>
                            <span className="source-score">
                              {Math.round(source.similarity * 100)}%
                            </span>
                          </summary>

                          <div className="source-content">
                            <p>
                              <strong>Guest:</strong>{' '}
                              {source.guest || 'Unknown'}
                            </p>

                            <p>
                              <strong>Transcript excerpt:</strong>
                            </p>

                            <p>{source.content}</p>

                            {source.youtube_url && (
                              <a
                                href={source.youtube_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                View episode
                              </a>
                            )}
                          </div>
                        </details>
                      ))}
                    </div>
                  )}
              </div>
            ))}

            {loading && (
              <div className="message-row assistant-row">
                <div className="message assistant loading-message">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="sr-only">Assistant is thinking</span>
                </div>
              </div>
            )}
          </div>

          <form className="composer" onSubmit={sendMessage}>
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={
                sessionId
                  ? 'Ask a question about growth or product...'
                  : 'Connecting to assistant...'
              }
              aria-label="Message input"
              disabled={!sessionId || loading}
            />

            <button
              type="submit"
              disabled={!sessionId || !input.trim() || loading}
            >
              {loading ? 'Thinking...' : 'Send'}
            </button>
          </form>

          <p className="composer-note">
            Answers are generated from retrieved Lenny's Podcast transcript
            sources.
          </p>
        </section>
      </main>
    </div>
  );
}

export default App;