
import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function createSessionId() {
  return crypto.randomUUID();
}

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [chats, setChats] = useState([]);
  const [sessionId, setSessionId] = useState(createSessionId);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");

  // Auto-scroll reference
  const chatEndRef = useRef(null);

  // Automatically scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end"
    });
  }, [messages, loading, historyLoading, error]);

  // Fetch all chat history
  const fetchChats = async () => {
    try {
      const response = await fetch(`${API_URL}/chats`);

      if (!response.ok) {
        throw new Error("Unable to fetch chats");
      }

      const data = await response.json();
      setChats(data.chats || []);

    } catch (error) {
      console.error("Chat history error:", error);
    }
  };

  // Load chat history when app starts
  useEffect(() => {
    fetchChats();
  }, []);

  // Start a new chat
  const startNewChat = () => {
    if (loading || historyLoading) return;

    setSessionId(createSessionId());
    setMessages([]);
    setMessage("");
    setError("");
  };

  // Open an old chat
  const openChat = async (id) => {
    if (loading || historyLoading) return;

    setHistoryLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/chats/${encodeURIComponent(id)}/messages`
      );

      if (!response.ok) {
        throw new Error("Unable to load conversation");
      }

      const data = await response.json();

      setSessionId(id);

      setMessages(
        (data.messages || []).map((item) => ({
          role: item.role === "assistant" ? "assistant" : "user",
          text: item.content
        }))
      );

    } catch (error) {
      console.error("Open chat error:", error);
      setError("Unable to load this conversation. Please try again.");

    } finally {
      setHistoryLoading(false);
    }
  };

  // Delete a chat
  const deleteChat = async (event, id) => {
    event.stopPropagation();

    if (loading || historyLoading) return;

    const confirmed = window.confirm(
      "Are you sure you want to delete this conversation?"
    );

    if (!confirmed) return;

    setError("");

    try {
      const response = await fetch(
        `${API_URL}/chats/${encodeURIComponent(id)}`,
        {
          method: "DELETE"
        }
      );

      if (!response.ok) {
        throw new Error("Unable to delete chat");
      }

      // If currently opened chat is deleted
      if (sessionId === id) {
        setSessionId(createSessionId());
        setMessages([]);
        setMessage("");
      }

      // Refresh sidebar history
      await fetchChats();

      alert("Chat deleted successfully!");

    } catch (error) {
      console.error("Delete chat error:", error);
      setError("Unable to delete this conversation. Please try again.");
    }
  };

  // Send message to Gemini
  const sendMessage = async () => {
    if (!message.trim() || loading || historyLoading) return;

    const userMessage = message.trim();

    setError("");

    setMessages((previous) => [
      ...previous,
      { role: "user", text: userMessage }
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: userMessage
        })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        { role: "assistant", text: data.answer }
      ]);

      await fetchChats();

    } catch (error) {
      console.error("Chat error:", error);

      setError(
        "Unable to get a response. Please check your internet connection or try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>✦ Nexora AI</h2>

        <button
          className="new-chat"
          onClick={startNewChat}
          disabled={loading || historyLoading}
        >
          + New Chat
        </button>

        <p className="sidebar-label">YOUR ASSISTANT</p>
        <p className="sidebar-item">✦ AI Assistant</p>

        <p className="sidebar-label">CHAT HISTORY</p>

        <div className="chat-history">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`history-item-wrapper ${
                sessionId === chat.id ? "active" : ""
              }`}
            >
              <button
                className={`history-item ${
                  sessionId === chat.id ? "active" : ""
                }`}
                onClick={() => openChat(chat.id)}
                disabled={loading || historyLoading}
                title={chat.title}
              >
                <span>✦</span>
                <span className="history-title">{chat.title}</span>
              </button>

              <button
                className="delete-chat"
                onClick={(event) => deleteChat(event, chat.id)}
                disabled={loading || historyLoading}
                title="Delete conversation"
                aria-label={`Delete ${chat.title}`}
              >
                🗑
              </button>
            </div>
          ))}

          {chats.length === 0 && (
            <p className="empty-history">
              No previous chats yet.
            </p>
          )}
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <span>Nexora AI</span>
          <span className="status">● Online</span>
        </header>

        <section className="chat-area">
          {historyLoading ? (
            <div className="welcome">
              <p>Loading conversation...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">✦</div>
              <h1>Welcome to Nexora AI</h1>
              <p>
                Your intelligent AI assistant. How can I help you today?
              </p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${msg.role}`}
              >
                {msg.text}
              </div>
            ))
          )}

          {/* Animated Loading Indicator */}
          {loading && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Auto Scroll Reference */}
          <div ref={chatEndRef} />
        </section>

        <div className="input-area">
          <div className="input-box">
            <input
              type="text"
              placeholder="Ask Nexora anything..."
              value={message}
              disabled={loading || historyLoading}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") sendMessage();
              }}
            />

            <button
              onClick={sendMessage}
              disabled={loading || historyLoading || !message.trim()}
            >
              ➤
            </button>
          </div>

          <p>Powered by Nexora AI</p>
        </div>
      </main>
    </div>
  );
}

export default App;
