import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, loading]);

  async function askQuestion() {
    if (!question.trim()) return;

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, chat_history: chatHistory }),
      });

      const data = await res.json();
      setChatHistory(data.chat_history);
    } catch {
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", content: "Backend running illa. FastAPI server check pannunga." },
      ]);
    }

    setLoading(false);
    setQuestion("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  }

  return (
    <div className="app">
      <header className="chat-header">
        <div className="header-content">
          <h1>
            <span className="logo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
                <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                <path d="M7 8c0-1.5 1-3 2.5-3S12 7 12 7s1.5-2 3-2S18 7 18 8" />
              </svg>
            </span>
            <div className="header-text">
              <span>Weed Sense</span>
              <small>AI Assistant for Farmers</small>
            </div>
          </h1>
        </div>
      </header>

      <div className="messages-container">
        {chatHistory.length === 0 && !loading && (
          <div className="welcome">
            <div className="welcome-icon">
              <svg viewBox="0 0 64 64" fill="none">
                <path d="M32 8C20 8 12 18 12 28c0 8 4 14 10 18l-2 10 12-6 12 6-2-10c6-4 10-10 10-18 0-10-8-20-20-20z" fill="#4a7c59" opacity="0.15" />
                <path d="M26 22c0-3 2-6 6-6s6 3 6 6" stroke="#4a7c59" strokeWidth="2.5" strokeLinecap="round" />
                <path d="M22 30c0-5 4-10 10-10s10 5 10 10" stroke="#4a7c59" strokeWidth="2.5" strokeLinecap="round" />
                <circle cx="24" cy="38" r="2" fill="#4a7c59" />
                <circle cx="32" cy="40" r="2" fill="#4a7c59" />
                <circle cx="40" cy="38" r="2" fill="#4a7c59" />
              </svg>
            </div>
            <h2>Identify & Manage Weeds</h2>
            <p>Describe the weed you see and get instant identification with control recommendations.</p>
            <div className="suggestions">
              <button className="suggestion-btn" onClick={() => { setQuestion("What are the characteristics of Palmer amaranth?"); }}>
                "Characteristics of Palmer amaranth?"
              </button>
              <button className="suggestion-btn" onClick={() => { setQuestion("How do I control broadleaf weeds in corn fields?"); }}>
                "Control broadleaf weeds in corn?"
              </button>
              <button className="suggestion-btn" onClick={() => { setQuestion("What is the best time to apply herbicides?"); }}>
                "Best time for herbicide application?"
              </button>
            </div>
          </div>
        )}

        {chatHistory.map((msg, index) => (
          <div key={index} className={`message-row ${msg.role}`}>
            <div className="bubble">
              {msg.role === "bot" && (
                <span className="bubble-label">Weed Sense</span>
              )}
              <p className="bubble-text">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row bot">
            <div className="bubble">
              <span className="bubble-label">Weed Sense</span>
              <div className="typing-indicator">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-bar">
        <textarea
          className="chat-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the weed or ask about control methods..."
          rows={1}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={askQuestion}
          disabled={loading || !question.trim()}
          aria-label="Send message"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default App;
