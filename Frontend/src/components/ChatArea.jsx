import { MessageContent } from "./MessageContent";

export function ChatArea({ messages, loading, bottomRef }) {
  return (
    <div className="chat-area">
      {messages.map((message, index) => (
        <div key={index} className="message-row">
          <div
            className={`chat-message chat-message--${
              message.role === "user" ? "user" : "assistant"
            }`}
          >
            <MessageContent
              text={message.text}
              isAssistant={message.role === "assistant"}
            />
          </div>
        </div>
      ))}

      {loading && (
        <div className="message-row">
          <div className="chat-message chat-message--assistant chat-message--loading">
            <span className="typing-dots">
              <span></span><span></span><span></span>
            </span>
            <span className="typing-label">Thinking…</span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
