import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./MessageContent.css";

export function MessageContent({ text, isAssistant }) {
  if (!text?.trim()) return null;

  const markdownComponents = {
    a: ({ node, ...props }) => (
      <a {...props} target="_blank" rel="noopener noreferrer" />
    ),
  };

  if (isAssistant) {
    return (
      <div className="message-content message-content--assistant">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {text}
        </ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="message-content message-content--user">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
