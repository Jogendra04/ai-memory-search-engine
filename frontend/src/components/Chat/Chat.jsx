import { useEffect, useRef, useState } from "react";

import {
  search,
  getChatHistory,
  clearChatHistory,
} from "../../services/api";


function Chat() {

  const [messages, setMessages] = useState([]);

  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(false);

  const chatContainerRef = useRef(null);


  // ==========================================
  // Welcome Message
  // ==========================================

  const getWelcomeMessage = () => ({
    sender: "AI",

    text:
      "Welcome! I can search through your uploaded documents and saved memories. Ask me a question to get started.",

    sources: [],
  });


  // ==========================================
  // Load Chat History
  // ==========================================

  useEffect(() => {

    const loadChatHistory = async () => {

      try {

        const data = await getChatHistory();

        const history = data.history || [];


        const formattedMessages = history.map(
          (message) => ({

            sender:
              message.role === "user"
                ? "You"
                : "AI",

            text: message.content,

            sources:
              message.sources || [],

          })
        );


        if (formattedMessages.length > 0) {

          setMessages(
            formattedMessages
          );

        } else {

          setMessages([
            getWelcomeMessage()
          ]);

        }

      } catch (error) {

        console.error(
          "Failed to load chat history:",
          error
        );

        setMessages([
          getWelcomeMessage()
        ]);

      }

    };


    loadChatHistory();

  }, []);


  // ==========================================
  // Auto Scroll
  // ==========================================

  useEffect(() => {

    if (!chatContainerRef.current) {
      return;
    }


    chatContainerRef.current.scrollTo({

      top:
        chatContainerRef.current.scrollHeight,

      behavior: "smooth",

    });

  }, [messages, loading]);


  // ==========================================
  // Clear Chat History
  // ==========================================

  const handleClearChat = async () => {

    const confirmed =
      window.confirm(
        "Are you sure you want to clear your chat history?"
      );


    if (!confirmed) {
      return;
    }


    try {

      setLoading(true);

      await clearChatHistory();


      setMessages([
        getWelcomeMessage()
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

    } finally {

      setLoading(false);

    }

  };


  // ==========================================
  // Send Message
  // ==========================================

  const sendMessage = async () => {

    if (
      !question.trim() ||
      loading
    ) {

      return;

    }


    const currentQuestion =
      question.trim();


    // Add user message immediately

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

      const data =
        await search(
          currentQuestion
        );


      setMessages((previousMessages) => [

        ...previousMessages,

        {
          sender: "AI",

          text:
            data.answer ||
            "No answer found.",

          sources:
            data.sources || [],

        },

      ]);

    } catch (error) {

      console.error(
        "Search error:",
        error
      );


      setMessages((previousMessages) => [

        ...previousMessages,

        {
          sender: "AI",

          text:
            "I couldn't connect to the backend. Please make sure the FastAPI server is running and try again.",

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

  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();

    }

  };


  // ==========================================
  // Render Source
  // ==========================================

  const renderSource = (
    source,
    index
  ) => {

    const score =
      source.score !== undefined
        ? `${Math.round(
            source.score * 100
          )}%`
        : "N/A";


    // ----------------------------------------
    // Memory Source
    // ----------------------------------------

    if (
      source.type === "memory"
    ) {

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

              {source.tags.map(
                (tag, tagIndex) => (

                  <span
                    key={tagIndex}
                    className="source-tag"
                  >
                    #{tag}
                  </span>

                )
              )}

            </div>

          )}


          <div className="source-score">
            Match: {score}
          </div>

        </div>

      );

    }


    // ----------------------------------------
    // Document Source
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


      {/* ======================================
          CHAT HEADER
      ====================================== */}

      <div className="chat-header">

        <div>

          <h2>
            Ask Your AI
          </h2>

          <p>
            Search your documents and memories
          </p>

        </div>


        <button
          className="clear-chat-button"
          onClick={handleClearChat}
          disabled={
            loading ||
            messages.length === 0
          }
        >
          Clear Chat
        </button>

      </div>


      {/* ======================================
          CHAT AREA
      ====================================== */}

      <div
        className="chat-container"
        ref={chatContainerRef}
      >

        {/* ====================================
            EMPTY / WELCOME STATE
        ==================================== */}

        {messages.length === 1 &&
          messages[0].sender === "AI" && (

            <div className="chat-empty-state">

              <div className="chat-empty-icon">
                🧠
              </div>

              <h3>
                Ask your AI anything
              </h3>

              <p>
                Your AI can search through
                your documents and saved
                memories to answer questions.
              </p>

              <div className="suggestion-list">

                <button
                  onClick={() =>
                    setQuestion(
                      "What information is available in my documents?"
                    )
                  }
                  disabled={loading}
                >
                  📄 Search my documents
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "What do you remember about me?"
                    )
                  }
                  disabled={loading}
                >
                  🧠 Search my memories
                </button>

              </div>

            </div>

          )}


        {/* ====================================
            MESSAGES
        ==================================== */}

        {messages.map(
          (message, index) => (

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

                {/* Sender */}

                <div className="message-sender">

                  {message.sender === "You"
                    ? "👤 You"
                    : "🤖 AI"}

                </div>


                {/* Message */}

                <div className="message-text">

                  {message.text}

                </div>


                {/* Sources */}

                {message.sender === "AI" &&
                  message.sources?.length > 0 && (

                    <div className="sources">

                      <h4>
                        Sources used
                      </h4>


                      {message.sources.map(
                        (
                          source,
                          sourceIndex
                        ) =>
                          renderSource(
                            source,
                            sourceIndex
                          )
                      )}

                    </div>

                  )}

              </div>

            </div>

          )
        )}


        {/* ====================================
            THINKING INDICATOR
        ==================================== */}

        {loading && (

          <div className="message-row ai-row">

            <div className="message ai-message">

              <div className="message-sender">
                🤖 AI
              </div>


              <div className="thinking">

                <span>
                  Thinking
                </span>

                <span className="thinking-dots">

                  <span>.</span>
                  <span>.</span>
                  <span>.</span>

                </span>

              </div>

            </div>

          </div>

        )}

      </div>


      {/* ======================================
          INPUT
      ====================================== */}

      <div className="input-container">

        <input
          type="text"
          placeholder={
            loading
              ? "AI is thinking..."
              : "Ask about your documents or memories..."
          }
          value={question}
          onChange={(event) =>
            setQuestion(
              event.target.value
            )
          }
          onKeyDown={handleKeyDown}
          disabled={loading}
        />


        <button
          onClick={sendMessage}
          disabled={
            loading ||
            !question.trim()
          }
        >

          {loading
            ? "Thinking..."
            : "Send"}

        </button>

      </div>


      {/* ======================================
          FOOTER HINT
      ====================================== */}

      <div className="chat-input-hint">

        Press Enter to send · Shift + Enter
        for a new line

      </div>

    </div>

  );

}


export default Chat;