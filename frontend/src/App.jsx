import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestions = [
    "What is the lifecycle of Musk thistle?",
    "What does Hoary Cress look like?",
    "What are the key identifying features of Bull thistle?",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, loading]);

  async function askQuestion(customQuestion = null) {
    const finalQuestion = customQuestion || question;

    if (!finalQuestion.trim() || loading) return;

    const updatedHistory = [
      ...chatHistory,
      { role: "user", content: finalQuestion },
    ];

    setChatHistory(updatedHistory);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch("api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: finalQuestion,
          chat_history: chatHistory,
        }),
      });

      const data = await res.json();

      if (data.chat_history) {
        setChatHistory(data.chat_history);
      } else if (data.answer) {
        setChatHistory([
          ...updatedHistory,
          { role: "bot", content: data.answer },
        ]);
      } else {
        setChatHistory([
          ...updatedHistory,
          {
            role: "bot",
            content: "Sorry, backend response format correct illa.",
          },
        ]);
      }
    } catch {
      setChatHistory([
        ...updatedHistory,
        {
          role: "bot",
          content: "Backend running illa. FastAPI server check pannunga.",
        },
      ]);
    }

    setLoading(false);
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
            <span className="logo">🌿</span>
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
            <div className="welcome-icon">🌿</div>

            <h2>Identify & Manage Weeds</h2>

            <p>
              Describe the weed you see and get instant identification with
              control recommendations.
            </p>

            <div className="suggestions">
              {suggestions.map((item, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => askQuestion(item)}
                  disabled={loading}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        )}

        {chatHistory.map((msg, index) => {
          const isBot = msg.role === "bot" || msg.role === "assistant";

          return (
            <div
              key={index}
              className={`message-row ${isBot ? "bot" : "user"}`}
            >
              {isBot ? (
                <div className="bot-bubble">
                  <div className="bot-header">
                    <span className="bot-avatar">🌿</span>
                    <span className="bubble-label">Weed Sense</span>
                  </div>

                  <div className="bot-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              ) : (
                <div className="user-bubble">
                  <p className="bubble-text">{msg.content}</p>
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="message-row bot">
            <div className="bot-bubble">
              <div className="bot-header">
                <span className="bot-avatar">🌿</span>
                <span className="bubble-label">Weed Sense</span>
              </div>

              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
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
          onClick={() => askQuestion()}
          disabled={loading || !question.trim()}
          aria-label="Send message"
        >
          ➤
        </button>
      </div>
    </div>
  );
}

export default App;