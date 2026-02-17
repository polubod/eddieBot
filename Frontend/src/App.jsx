import { useEffect, useRef } from "react";
import "./App.css";
import { useChat } from "./hooks/useChat";
import { Header } from "./components/Header";
import { ChatArea } from "./components/ChatArea";
import { InputBar } from "./components/InputBar";
import { Disclaimer } from "./components/Disclaimer";

export default function App() {
  const bottomRef = useRef(null);
  const { messages, input, loading, handleSubmit, handleInputChange } =
    useChat();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="page">
      <Header />
      <ChatArea messages={messages} loading={loading} bottomRef={bottomRef} />
      <InputBar
        input={input}
        loading={loading}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
      />
      <Disclaimer />
    </div>
  );
}
