import { useEffect, useState } from "react";

import {
  search,
  getChatHistory,
  clearChatHistory,
} from "../../services/api";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  // ==========================================
  // Load chat history
  // ==========================================

  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const data = await getChatHistory();

        const history = data.history || [];

        const formattedMessages = history.map((message) => ({
          sender: message.role === "user" ? "You" : "AI",
          text: message.content,
          sources: [],
        }));

        if (formattedMessages.length > 0) {
          setMessages(formattedMessages);
        } else {
          setMessages([
            {
              sender: "AI",
              text: "Welcome! Ask me anything about your documents or memories.",
              sources: [],
            },
          ]);
        }
      } catch (error) {
        console.error("Failed to load chat history:", error);

        setMessages([
          {
            sender: "AI",
            text: "Welcome! Ask me anything about your documents or memories.",
            sources: [],
          },
        ]);
      }
    };

    loadChatHistory();
  }, []);

  // ==========================================
  // Clear chat history
  // ==========================================

  const handleClearChat = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear your chat history?"
    );

    if (!confirmed) return;

    try {
      await clearChatHistory();

      setMessages([
        {
          sender: "AI",
          text: "Welcome! Ask me anything about your documents or memories.",
          sources: [],
        },
      ]);
    } catch (error) {
      console.error("Failed to clear chat history:", error);

      alert(
        error.message || "Failed to clear chat history."
      );
    }
  };

  // ==========================================
  // Send message
  // ==========================================

  const sendMessage = async () => {
    if (!question.trim() || loading) return;

    const currentQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        sender: "You",
        text: currentQuestion,
        sources: [],
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const data = await search(currentQuestion);

      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: data.answer || "No answer found.",
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: "Unable to connect to the backend.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Enter key
  // ==========================================

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  // ==========================================
  // Render source
  // ==========================================

  const renderSource = (source, index) => {
    const score =
      source.score !== undefined
        ? `${Math.round(source.score * 100)}%`
        : "N/A";

    // ----------------------------------------
    // Saved Memory
    // ----------------------------------------

    if (source.type === "memory") {
      return (
        <div
          className="source-card memory-source"
          key={index}
        >
          <div className="source-type">
            🧠 Saved Memory
          </div>

          <div className="source-title">
            {source.title}
          </div>

          {source.tags?.length > 0 && (
            <div className="source-tags">
              {source.tags.map((tag, i) => (
                <span
                  key={i}
                  className="source-tag"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          <div className="source-score">
            Match: {score}
          </div>
        </div>
      );
    }

    // ----------------------------------------
    // Uploaded Document
    // ----------------------------------------

    return (
      <div
        className="source-card document-source"
        key={index}
      >
        <div className="source-type">
          📄 Uploaded Document
        </div>

        <div className="source-title">
          {source.filename}
        </div>

        <div className="source-chunk">
          Chunk: {source.chunk_number}
        </div>

        <div className="source-score">
          Match: {score}
        </div>
      </div>
    );
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="chat-page">

      <div className="chat-header">
        <div>
          <h2>Ask Your AI</h2>

          <p>
            Search your documents and memories
          </p>
        </div>

        <button
          className="clear-chat-button"
          onClick={handleClearChat}
          disabled={loading}
        >
          Clear Chat
        </button>
      </div>

      {/* ======================================
          Chat Messages
      ====================================== */}

      <div className="chat-container">

        {messages.map((message, index) => (
          <div
            key={index}
            className={`message-row ${
              message.sender === "You"
                ? "user-row"
                : "ai-row"
            }`}
          >

            <div
              className={`message ${
                message.sender === "You"
                  ? "user-message"
                  : "ai-message"
              }`}
            >

              <div className="message-sender">
                {message.sender === "You"
                  ? "👤 You"
                  : "🤖 AI"}
              </div>

              <div className="message-text">
                {message.text}
              </div>

              {/* =================================
                  Sources
              ================================= */}

              {message.sender === "AI" &&
                message.sources?.length > 0 && (

                  <div className="sources">

                    <h4>Sources</h4>

                    {message.sources.map(
                      (source, i) =>
                        renderSource(
                          source,
                          i
                        )
                    )}

                  </div>
                )}

            </div>
          </div>
        ))}

        {/* ======================================
            Loading
        ====================================== */}

        {loading && (
          <div className="message-row ai-row">

            <div className="message ai-message">

              <div className="message-sender">
                🤖 AI
              </div>

              <div className="typing-indicator">
                Thinking...
              </div>

            </div>

          </div>
        )}

      </div>

      {/* ======================================
          Input
      ====================================== */}

      <div className="input-container">

        <input
          type="text"
          placeholder="Ask about your documents or memories..."
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          onKeyDown={handleKeyDown}
          disabled={loading}
        />

        <button
          onClick={sendMessage}
          disabled={
            loading || !question.trim()
          }
        >
          {loading
            ? "Thinking..."
            : "Send"}
        </button>

      </div>

    </div>
  );
}

export default Chat;