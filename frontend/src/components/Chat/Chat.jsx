import { useState } from "react";
import { search } from "../../services/api";

function Chat() {
  const [messages, setMessages] = useState([
    {
      sender: "AI",
      text: "Welcome! Ask me anything about your documents or memories.",
      sources: [],
    },
  ]);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

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
    }

    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  const renderSource = (source, index) => {

    const score = source.score
      ? `${Math.round(source.score * 100)}%`
      : "N/A";

    if (source.type === "memory") {

      return (
        <div
          className="source-card"
          key={index}
        >
          <div className="source-title">
            🧠 {source.title}
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

    return (
      <div
        className="source-card"
        key={index}
      >
        <div className="source-title">
          📄 {source.filename}
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

  return (
    <div className="chat-section">

      <h2>Ask Your AI</h2>

      <div className="chat-container">

        {messages.map((message, index) => (
          <div
            className="message"
            key={index}
          >
            <strong>{message.sender}:</strong>{" "}
            {message.text}

            {message.sender === "AI" &&
              message.sources?.length > 0 && (
                <div className="sources">

                  <h4>Sources</h4>

                  {message.sources.map((source, i) =>
                    renderSource(source, i)
                  )}

                </div>
              )}
          </div>
        ))}

        {loading && (
          <div className="message">
            <strong>AI:</strong> Thinking...
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
          {loading ? "Thinking..." : "Send"}
        </button>

      </div>

    </div>
  );
}

export default Chat;