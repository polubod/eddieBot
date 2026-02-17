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
