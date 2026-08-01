import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // =============================
  // CHAT STATE
  // =============================

  const [messages, setMessages] = useState([
    {
      sender: "AI",
      text: "Welcome! Ask me anything about your documents or memories.",
      sources: [],
    },
  ]);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  // =============================
  // MEMORY STATE
  // =============================

  const [memories, setMemories] = useState([]);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");

  const [memoryLoading, setMemoryLoading] = useState(false);

  // =============================
  // PDF UPLOAD STATE
  // =============================

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  // =============================
  // LOAD MEMORIES
  // =============================

  const loadMemories = async () => {
  try {
    const response = await fetch(`${API_URL}/memories`);

    if (!response.ok) {
      throw new Error("Failed to load memories");
    }

    const data = await response.json();

    setMemories(data.memories || []);
  } catch (error) {
    console.error("Error loading memories:", error);
  }
};


  // =============================
  // SEND CHAT MESSAGE
  // =============================

  const sendMessage = async () => {
    if (!question.trim() || loading) {
      return;
    }

    const currentQuestion = question.trim();

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        sender: "You",
        text: currentQuestion,
        sources: [],
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data = await response.json();

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          sender: "AI",
          text: data.answer || "I couldn't find an answer.",
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          sender: "AI",
          text: "Sorry, I couldn't connect to the backend.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // =============================
  // SAVE MEMORY
  // =============================

  const saveMemory = async () => {
    if (!title.trim()) {
      alert("Please enter a memory title.");
      return;
    }

    if (!content.trim()) {
      alert("Please enter memory content.");
      return;
    }

    setMemoryLoading(true);

    const tagList = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    try {
      const response = await fetch(`${API_URL}/memory`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: title.trim(),
          content: content.trim(),
          tags: tagList,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save memory");
      }

      setTitle("");
      setContent("");
      setTags("");

      await loadMemories();

      alert("Memory saved successfully!");
    } catch (error) {
      console.error("Save memory error:", error);
      alert("Failed to save memory.");
    } finally {
      setMemoryLoading(false);
    }
  };

  // =============================
  // DELETE MEMORY
  // =============================

  const deleteMemory = async (memoryId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this memory?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/memory/${memoryId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete memory");
      }

      setMemories((previousMemories) =>
        previousMemories.filter((memory) => memory.id !== memoryId)
      );
    } catch (error) {
      console.error("Delete memory error:", error);
      alert("Failed to delete memory.");
    }
  };

  // =============================
  // PDF FILE SELECT
  // =============================

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setUploadMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setSelectedFile(null);
      setUploadMessage("Please select a PDF file.");
      return;
    }

    setSelectedFile(file);
  };

  // =============================
  // PDF UPLOAD
  // =============================

  const uploadDocument = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select a PDF file first.");
      return;
    }

    setUploadLoading(true);
    setUploadMessage("");

    const formData = new FormData();

    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setUploadMessage(
        data.message || "Document uploaded successfully!"
      );

      setSelectedFile(null);

      // Reset file input
      const fileInput = document.getElementById("pdf-upload");

      if (fileInput) {
        fileInput.value = "";
      }
    } catch (error) {
      console.error("Upload error:", error);

      setUploadMessage(
        "Failed to upload document. Please try again."
      );
    } finally {
      setUploadLoading(false);
    }
  };

  // =============================
  // ENTER KEY
  // =============================

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  // =============================
  // RENDER SOURCE
  // =============================

  const renderSource = (source, index) => {
    const score = source.score
      ? `${Math.round(source.score * 100)}%`
      : "N/A";

    if (source.type === "memory") {
      return (
        <div className="source-card" key={`${source.id}-${index}`}>
          <div className="source-title">
            🧠 {source.title}
          </div>

          {source.tags && source.tags.length > 0 && (
            <div className="source-tags">
              {source.tags.map((tag, tagIndex) => (
                <span className="source-tag" key={tagIndex}>
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
      <div className="source-card" key={`${source.id}-${index}`}>
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

  // =============================
  // UI
  // =============================

  return (
    <div className="app">
      <h1>AI Memory Search Engine</h1>

      <div className="main-layout">

        {/* =========================
            CHAT SECTION
        ========================== */}

        <div className="chat-section">
          <h2>Ask Your AI</h2>

          <div className="chat-container">
            {messages.map((message, index) => (
              <div className="message" key={index}>

                <strong>{message.sender}:</strong>{" "}
                {message.text}

                {message.sender === "AI" &&
                  message.sources &&
                  message.sources.length > 0 && (
                    <div className="sources">
                      <h4>Sources</h4>

                      {message.sources.map((source, sourceIndex) =>
                        renderSource(source, sourceIndex)
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
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button onClick={sendMessage} disabled={loading}>
              {loading ? "Thinking..." : "Send"}
            </button>
          </div>
        </div>

        {/* =========================
            MEMORY SECTION
        ========================== */}

        <div className="memory-section">

          {/* =========================
              DOCUMENT UPLOAD
          ========================== */}

          <div className="upload-section">
            <h2>Documents</h2>

            <input
              id="pdf-upload"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />

            {selectedFile && (
              <p className="selected-file">
                Selected: {selectedFile.name}
              </p>
            )}

            <button
              className="upload-button"
              onClick={uploadDocument}
              disabled={uploadLoading}
            >
              {uploadLoading
                ? "Processing..."
                : "Upload Document"}
            </button>

            {uploadMessage && (
              <p className="upload-message">
                {uploadMessage}
              </p>
            )}
          </div>

          {/* =========================
              ADD MEMORY
          ========================== */}

          <div className="memory-form">
            <h2>Add Memory</h2>

            <input
              type="text"
              placeholder="Memory title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />

            <textarea
              placeholder="Write your memory..."
              value={content}
              onChange={(event) => setContent(event.target.value)}
              rows={5}
            />

            <input
              type="text"
              placeholder="Tags: python, ai, project"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
            />

            <button
              onClick={saveMemory}
              disabled={memoryLoading}
            >
              {memoryLoading
                ? "Saving..."
                : "Save Memory"}
            </button>
          </div>

          {/* =========================
              SAVED MEMORIES
          ========================== */}

          <div className="memory-list">
            <h2>Saved Memories</h2>

            {memories.length === 0 ? (
              <p>No memories saved yet.</p>
            ) : (
              memories.map((memory) => (
                <div
                  className="memory-card"
                  key={memory.id}
                >

                  <div className="memory-header">
                    <h3>{memory.title}</h3>

                    <button
                      className="delete-button"
                      onClick={() =>
                        deleteMemory(memory.id)
                      }
                    >
                      Delete
                    </button>
                  </div>

                  <p>{memory.content}</p>

                  {memory.tags &&
                    memory.tags.length > 0 && (
                      <div className="tags">
                        {memory.tags.map(
                          (tag, tagIndex) => (
                            <span
                              className="tag"
                              key={tagIndex}
                            >
                              #{tag}
                            </span>
                          )
                        )}
                      </div>
                    )}
                </div>
              ))
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;