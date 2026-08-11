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
  // Load Chat History
  // ==========================================

  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const data = await getChatHistory();

        const history = data.history || [];

        const formattedMessages = history.map((message) => ({
          sender:
            message.role === "user"
              ? "You"
              : "AI",

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
        console.error(
          "Failed to load chat history:",
          error
        );

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
  // Clear Chat History
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
      console.error(
        "Failed to clear chat history:",
        error
      );

      alert(
        error.message ||
          "Failed to clear chat history."
      );
    }
  };

  // ==========================================
  // Send Message
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
  // Enter Key
  // ==========================================

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  // ==========================================
  // Render Sources
  // ==========================================

  const renderSource = (source, index) => {
    const score =
      source.score !== undefined
        ? `${Math.round(source.score * 100)}%`
        : "N/A";

    // ========================================
    // Saved Memory
    // ========================================

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

    // ========================================
    // Uploaded Document
    // ========================================

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
    <div>
      <div className="chat-header">
        <h2>Ask Your AI</h2>

        <button
          onClick={handleClearChat}
          className="clear-chat-button"
        >
          Clear Chat
        </button>
      </div>

      <div className="chat-container">
        {messages.map((message, index) => (
          <div
            className="message"
            key={index}
          >
            <strong>
              {message.sender}:
            </strong>{" "}
            {message.text}

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
        ))}

        {loading && (
          <div className="message">
            <strong>AI:</strong>{" "}
            Thinking...
          </div>
        )}
      </div>

      <div className="input-container">
        <input
          type="text"
          placeholder="Ask about your documents or memories..."
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          onKeyDown={handleKeyDown}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
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