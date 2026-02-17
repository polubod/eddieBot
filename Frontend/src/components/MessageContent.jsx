import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./MessageContent.css";

export function MessageContent({ text, isAssistant }) {
  if (!text?.trim()) return null;

  if (isAssistant) {
    return (
      <div className="message-content message-content--assistant">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="message-content message-content--user">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  );
}
