import { useState } from "react";
import { sendChatMessage } from "../services/chatApi";

export function useChat() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! Ask me anything about SIUE." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(text);

      if (!data) return;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            "Sorry — I hit an error talking to the backend. Check the backend terminal for details.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(event) {
    setInput(event.target.value);
  }

  return {
    messages,
    input,
    loading,
    handleSubmit,
    handleInputChange,
  };
}
