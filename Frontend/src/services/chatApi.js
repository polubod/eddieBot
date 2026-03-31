import { API_BASE_URL } from "../config";
import { getSessionId } from "../utils/session";

export async function sendChatMessage(text) {
  const trimmed = text.trim();
  if (!trimmed) return null;

  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: getSessionId(),
      message: trimmed,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }

  return res.json();
}

// Kept for reference — streaming version, not currently used
// export async function streamChatMessage(text, onToken, onDone) { ... }

/**
 * Streams a chat response token-by-token.
 * @param {string} text - The user's message.
 * @param {(token: string) => void} onToken - Called with each text token as it arrives.
 * @param {(category: string) => void} onDone - Called with the final category when streaming ends.
 */
export async function streamChatMessage(text, onToken, onDone) {
  const trimmed = text.trim();
  if (!trimmed) return;

  const res = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: getSessionId(),
      message: trimmed,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop(); // keep incomplete last line

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6).trim();
      if (payload === "[DONE]") {
        onDone?.("");
        return;
      }
      try {
        const parsed = JSON.parse(payload);
        if (parsed.token !== undefined) onToken(parsed.token);
        if (parsed.category !== undefined) onDone?.(parsed.category);
      } catch {
        // ignore malformed lines
      }
    }
  }
}
