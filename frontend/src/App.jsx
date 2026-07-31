import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      sender: "AI",
      text: "Welcome! Ask me anything about your documents.",
    },
  ]);

  const [question, setQuestion] = useState("");

  const sendMessage = async () => {
    if (!question.trim()) return;

    // Show user's message
    setMessages((prev) => [
      ...prev,
      { sender: "You", text: question },
    ]);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      // Show AI response
      setMessages((prev) => [
        ...prev,
        { sender: "AI", text: data.answer },
      ]);

      setQuestion("");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="app">
      <h1>AI Memory Search Engine</h1>

      <div className="chat-container">
        {messages.map((message, index) => (
          <div key={index} className="message">
            <strong>{message.sender}:</strong> {message.text}
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;