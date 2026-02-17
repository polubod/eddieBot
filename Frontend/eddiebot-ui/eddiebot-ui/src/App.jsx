import { useEffect, useRef, useState } from "react";
import "./App.css";
import siueLogo from "./assets/SIUE_Logo.png";

/* -----------------------------
   Session ID generator
-------------------------------- */
function getSessionId() {
  const key = "eddiebot_session_id";
  let id = localStorage.getItem(key);

  if (!id) {
    id = crypto.randomUUID();   // modern browser-safe UUID
    localStorage.setItem(key, id);
  }

  return id;
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! Ask me anything about SIUE." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: getSessionId(),   // SESSION ID ADDED
          message: text,
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || `HTTP ${res.status}`);
      }

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            "Sorry — I hit an error talking to the backend. Check the backend terminal for details.",
        },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      {/* Header */}
      <div className="header">
        <img src={siueLogo} alt="SIUE Logo" className="logo" />
        <h1 className="header-title">EddieBot</h1>
      </div>

      {/* Chat area */}
      <div className="chat-area">
        {messages.map((m, idx) => (
          <div key={idx} className="message-row">
            <div
              className={`chat-message ${
                m.role === "user" ? "user" : "assistant"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row">
            <div className="chat-message assistant">Thinking…</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={sendMessage} className="input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message…"
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>

      {/* Disclaimer */}
      <div className="disclaimer">
        *This assistant uses generative AI and can make mistakes. Check important info.
      </div>
    </div>
  );
}
